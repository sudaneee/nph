import re
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from sitecore.models import TimeStampedModel, SEOFields, IMAGE_VALIDATORS

LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('all', 'All Levels'),
]

# Matches the 11-char video id in every common YouTube URL shape:
# youtu.be/ID, youtube.com/watch?v=ID, /embed/ID, /shorts/ID, /live/ID.
YOUTUBE_ID_RE = re.compile(
    r'(?:youtu\.be/|youtube(?:-nocookie)?\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/|v/))([A-Za-z0-9_-]{11})'
)


def youtube_id(url):
    match = YOUTUBE_ID_RE.search(url or '')
    return match.group(1) if match else ''


def validate_youtube_url(url):
    if url and not youtube_id(url):
        raise ValidationError('Enter a valid YouTube video link (e.g. https://youtu.be/abc123XYZ_0).')


def youtube_embed_url(url):
    vid = youtube_id(url)
    return f'https://www.youtube-nocookie.com/embed/{vid}?rel=0&modestbranding=1' if vid else ''


class LiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True)


class Course(TimeStampedModel, SEOFields):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=250)
    full_description = CKEditor5Field(config_name='richtext')
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    preview_video_url = models.URLField(blank=True, validators=[validate_youtube_url],
                                        help_text='Optional YouTube trailer shown on the course page to everyone.')

    price = models.PositiveIntegerField(default=0, help_text='Price in Naira (whole number). 0 makes the course free.')
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    duration_text = models.CharField(max_length=60, blank=True, help_text='e.g. "6 weeks · 3 hrs/week"')
    instructor_name = models.CharField(max_length=120, blank=True)
    what_you_will_learn = models.TextField(blank=True, help_text='One outcome per line.')
    requirements = models.TextField(blank=True, help_text='One requirement per line.')

    certificate_enabled = models.BooleanField(default=True,
                                              help_text='Issue a certificate once all lessons and quizzes are passed.')
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0, db_index=True)

    objects = models.Manager()
    live = LiveManager()

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('learning:course_detail', kwargs={'slug': self.slug})

    @property
    def is_free(self):
        return self.price == 0

    @property
    def preview_embed_url(self):
        return youtube_embed_url(self.preview_video_url)

    @property
    def outcomes(self):
        return [line.strip() for line in self.what_you_will_learn.splitlines() if line.strip()]

    @property
    def requirement_list(self):
        return [line.strip() for line in self.requirements.splitlines() if line.strip()]

    def ordered_lessons(self):
        return Lesson.objects.filter(module__course=self).select_related('module').order_by('module__order', 'module__id', 'order', 'id')


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.course.title} — {self.title}'


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, validators=[validate_youtube_url],
                                help_text='YouTube link. Set the video to "Unlisted" on YouTube.')
    content = CKEditor5Field(config_name='richtext', blank=True, help_text='Notes shown under the video.')
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    is_free_preview = models.BooleanField(default=False, help_text='Anyone can watch this lesson without enrolling.')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    @property
    def course(self):
        return self.module.course

    @property
    def embed_url(self):
        return youtube_embed_url(self.video_url)

    def get_absolute_url(self):
        return reverse('learning:lesson', kwargs={'slug': self.module.course.slug, 'lesson_id': self.pk})


class Enrollment(models.Model):
    SOURCE_CHOICES = [('free', 'Free'), ('paid', 'Paid'), ('admin', 'Added by admin')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='enrollments')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='admin')
    enrolled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-enrolled_at']
        constraints = [models.UniqueConstraint(fields=['user', 'course'], name='unique_enrollment')]

    def __str__(self):
        return f'{self.user} → {self.course}'

    def completed_lesson_ids(self):
        return set(self.progress.values_list('lesson_id', flat=True))

    def progress_percent(self):
        total = self.course.ordered_lessons().count()
        if not total:
            return 0
        return round(100 * self.progress.count() / total)

    def passed_quiz_ids(self):
        return set(self.quiz_attempts.filter(passed=True).values_list('quiz_id', flat=True))

    def is_complete(self):
        lesson_ids = set(self.course.ordered_lessons().values_list('id', flat=True))
        quiz_ids = set(self.course.quizzes.filter(published=True).values_list('id', flat=True))
        if not lesson_ids and not quiz_ids:
            return False
        return lesson_ids <= self.completed_lesson_ids() and quiz_ids <= self.passed_quiz_ids()

    def refresh_completion(self):
        """Stamp/clear completed_at so dashboards don't have to recompute it."""
        done = self.is_complete()
        if done and not self.completed_at:
            self.completed_at = timezone.now()
            self.save(update_fields=['completed_at'])
        elif not done and self.completed_at:
            self.completed_at = None
            self.save(update_fields=['completed_at'])
        return done


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='+')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['enrollment', 'lesson'], name='unique_lesson_progress')]
        verbose_name_plural = 'Lesson progress'


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    pass_mark = models.PositiveSmallIntegerField(default=70, help_text='Percentage needed to pass (0–100).')
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f'{self.course.title} — {self.title}'

    def clean(self):
        if self.pass_mark > 100:
            raise ValidationError({'pass_mark': 'Pass mark cannot exceed 100.'})

    def get_absolute_url(self):
        return reverse('learning:quiz', kwargs={'slug': self.course.slug, 'quiz_id': self.pk})


class Question(models.Model):
    """Multiple choice with up to four options — flat fields keep the admin to one inline table."""
    OPTION_KEYS = ['a', 'b', 'c', 'd']

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300, blank=True)
    option_d = models.CharField(max_length=300, blank=True)
    correct_option = models.CharField(max_length=1, choices=[(k, k.upper()) for k in OPTION_KEYS])
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:80]

    def options(self):
        return [(k, getattr(self, f'option_{k}')) for k in self.OPTION_KEYS if getattr(self, f'option_{k}')]

    def clean(self):
        if self.correct_option and not getattr(self, f'option_{self.correct_option}', ''):
            raise ValidationError({'correct_option': 'The correct option must have text.'})


class QuizAttempt(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveSmallIntegerField(help_text='Percentage')
    passed = models.BooleanField(default=False)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


def _certificate_code():
    return secrets.token_hex(5).upper()


class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    code = models.CharField(max_length=20, unique=True, default=_certificate_code, editable=False)
    student_name = models.CharField(max_length=200)
    course_title = models.CharField(max_length=200)
    issued_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.code} — {self.student_name}'

    def get_absolute_url(self):
        return reverse('learning:certificate_verify', kwargs={'code': self.code})
