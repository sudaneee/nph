from django.contrib import admin
from django.db.models import Count

from .models import Course, Module, Lesson, Enrollment, LessonProgress, Quiz, Question, QuizAttempt, Certificate


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('title', 'order')
    show_change_link = True


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0
    fields = ('title', 'pass_mark', 'order', 'published')
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'level', 'student_count', 'featured', 'published', 'display_order')
    list_editable = ('featured', 'published', 'display_order')
    list_filter = ('published', 'featured', 'level')
    search_fields = ('title', 'short_description', 'instructor_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline, QuizInline]
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'thumbnail', 'preview_video_url', 'display_order')}),
        ('Pricing', {'fields': ('price',), 'description': 'Whole Naira. Set to 0 for a free course.'}),
        ('Content', {'fields': ('short_description', 'full_description', 'what_you_will_learn', 'requirements')}),
        ('Details', {'fields': ('level', 'duration_text', 'instructor_name', 'certificate_enabled')}),
        ('Visibility', {'fields': ('featured', 'published')}),
        ('SEO', {'classes': ('collapse',), 'fields': (
            'seo_title', 'meta_description', 'og_image', 'canonical_url', 'robots_index', 'robots_follow',
        )}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_students=Count('enrollments'))

    @admin.display(description='Students', ordering='_students')
    def student_count(self, obj):
        return obj._students


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    fields = (('title', 'order'), 'video_url', ('duration_minutes', 'is_free_preview'), 'content')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'lesson_count')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_lessons=Count('lessons'))

    @admin.display(description='Lessons', ordering='_lessons')
    def lesson_count(self, obj):
        return obj._lessons


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'is_free_preview', 'duration_minutes')
    list_filter = ('module__course', 'is_free_preview')
    search_fields = ('title', 'module__title', 'module__course__title')
    list_select_related = ('module__course',)


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text', ('option_a', 'option_b'), ('option_c', 'option_d'), ('correct_option', 'order'))


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_mark', 'order', 'published')
    list_filter = ('course', 'published')
    inlines = [QuestionInline]


class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 0
    readonly_fields = ('lesson', 'completed_at')
    can_delete = False


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'source', 'enrolled_at', 'completed_at')
    list_filter = ('course', 'source')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'course__title')
    raw_id_fields = ('user',)
    date_hierarchy = 'enrolled_at'
    readonly_fields = ('completed_at',)
    inlines = [LessonProgressInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'quiz', 'score', 'passed', 'created_at')
    list_filter = ('passed', 'quiz__course')
    readonly_fields = ('enrollment', 'quiz', 'score', 'passed', 'answers', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('code', 'student_name', 'course_title', 'issued_at')
    search_fields = ('code', 'student_name', 'course_title')
    readonly_fields = ('code',)
    raw_id_fields = ('enrollment',)
