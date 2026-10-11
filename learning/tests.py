from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (Course, Module, Lesson, Enrollment, LessonProgress, Quiz, Question, Certificate,
                     youtube_id)

User = get_user_model()


def make_course(price=5000, **kwargs):
    course = Course.objects.create(title='Digital Marketing', slug='digital-marketing', short_description='s',
                                   full_description='<p>d</p>', price=price, published=True, **kwargs)
    module = Module.objects.create(course=course, title='Intro', order=1)
    l1 = Lesson.objects.create(module=module, title='Welcome', video_url='https://youtu.be/dQw4w9WgXcQ',
                               is_free_preview=True, order=1)
    l2 = Lesson.objects.create(module=module, title='Deep dive', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                               order=2)
    return course, l1, l2


class YouTubeTests(TestCase):
    def test_parses_common_url_shapes(self):
        for url in ['https://youtu.be/dQw4w9WgXcQ', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10',
                    'https://youtube.com/embed/dQw4w9WgXcQ', 'https://www.youtube.com/shorts/dQw4w9WgXcQ',
                    'https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ']:
            self.assertEqual(youtube_id(url), 'dQw4w9WgXcQ', url)
        self.assertEqual(youtube_id('https://vimeo.com/123'), '')


class AccessTests(TestCase):
    def setUp(self):
        self.course, self.l1, self.l2 = make_course()
        self.user = User.objects.create_user('u', email='u@example.com', password='pw')

    def test_catalog_and_detail_are_public(self):
        self.assertContains(self.client.get(reverse('learning:course_list')), '₦5,000')
        self.assertContains(self.client.get(self.course.get_absolute_url()), 'Sign up to enroll')

    def test_unpublished_course_hidden(self):
        self.course.published = False
        self.course.save()
        self.assertEqual(self.client.get(self.course.get_absolute_url()).status_code, 404)

    def test_free_preview_lesson_open_to_anyone(self):
        resp = self.client.get(self.l1.get_absolute_url())
        self.assertContains(resp, 'youtube-nocookie.com/embed/dQw4w9WgXcQ')

    def test_locked_lesson_requires_enrollment(self):
        resp = self.client.get(self.l2.get_absolute_url())
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={self.l2.get_absolute_url()}")
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(self.l2.get_absolute_url()), self.course.get_absolute_url())
        Enrollment.objects.create(user=self.user, course=self.course)
        self.assertContains(self.client.get(self.l2.get_absolute_url()), 'Mark complete')

    def test_lesson_from_other_course_is_404(self):
        other = Course.objects.create(title='Other', slug='other', short_description='s', full_description='d',
                                      published=True)
        url = reverse('learning:lesson', kwargs={'slug': other.slug, 'lesson_id': self.l1.pk})
        self.assertEqual(self.client.get(url).status_code, 404)


class ProgressQuizCertificateTests(TestCase):
    def setUp(self):
        self.course, self.l1, self.l2 = make_course()
        self.user = User.objects.create_user('u', email='u@example.com', password='pw', first_name='Amina',
                                             last_name='Bello')
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.quiz = Quiz.objects.create(course=self.course, title='Final quiz', pass_mark=50)
        self.q1 = Question.objects.create(quiz=self.quiz, text='2+2?', option_a='3', option_b='4', correct_option='b')
        self.q2 = Question.objects.create(quiz=self.quiz, text='Capital of Kano State?', option_a='Kano',
                                          option_b='Kaduna', correct_option='a')
        self.client.force_login(self.user)

    def complete(self, lesson):
        return self.client.post(reverse('learning:complete_lesson', kwargs={'slug': self.course.slug,
                                                                          'lesson_id': lesson.pk}))

    def test_resume_goes_to_next_unfinished_lesson_then_quiz(self):
        learn = reverse('learning:course_learn', kwargs={'slug': self.course.slug})
        self.assertRedirects(self.client.get(learn), self.l1.get_absolute_url())
        self.complete(self.l1)
        self.assertRedirects(self.client.get(learn), self.l2.get_absolute_url())
        self.complete(self.l2)
        self.assertRedirects(self.client.get(learn), self.quiz.get_absolute_url())
        self.assertEqual(self.enrollment.progress_percent(), 100)

    def test_quiz_requires_all_answers(self):
        resp = self.client.post(self.quiz.get_absolute_url(), {f'q{self.q1.id}': 'b'})
        self.assertContains(resp, 'Please answer every question')
        self.assertFalse(self.quiz.attempts.exists())

    def test_quiz_rejects_option_that_does_not_exist(self):
        resp = self.client.post(self.quiz.get_absolute_url(), {f'q{self.q1.id}': 'b', f'q{self.q2.id}': 'd'})
        self.assertContains(resp, 'Please answer every question')

    def test_failed_quiz_hides_answers(self):
        resp = self.client.post(self.quiz.get_absolute_url(), {f'q{self.q1.id}': 'a', f'q{self.q2.id}': 'b'})
        self.assertContains(resp, '0%')
        self.assertContains(resp, 'Retake quiz')
        self.assertNotContains(resp, 'is-correct')

    def test_certificate_only_after_lessons_and_quiz(self):
        cert_url = reverse('learning:certificate', kwargs={'slug': self.course.slug})
        self.complete(self.l1)
        self.complete(self.l2)
        self.client.get(cert_url)
        self.assertFalse(Certificate.objects.exists())

        resp = self.client.post(self.quiz.get_absolute_url(), {f'q{self.q1.id}': 'b', f'q{self.q2.id}': 'b'})
        self.assertContains(resp, '50%')
        self.assertContains(resp, 'Get your certificate')

        resp = self.client.get(cert_url)
        cert = Certificate.objects.get()
        self.assertRedirects(resp, cert.get_absolute_url())
        self.assertEqual(cert.student_name, 'Amina Bello')
        self.enrollment.refresh_from_db()
        self.assertIsNotNone(self.enrollment.completed_at)

        # Public verification page works for anyone, and a second request doesn't duplicate.
        self.client.logout()
        self.assertContains(self.client.get(cert.get_absolute_url()), 'Amina Bello')
        self.client.force_login(self.user)
        self.client.get(cert_url)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_completing_twice_is_idempotent(self):
        self.complete(self.l1)
        self.complete(self.l1)
        self.assertEqual(LessonProgress.objects.count(), 1)
