from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from payments.fees import processing_fee, total_with_zainpay_charge
from .models import Course, Lesson, Enrollment, LessonProgress, Quiz, QuizAttempt, Certificate


def _enrollment(request, course):
    if not request.user.is_authenticated:
        return None
    return Enrollment.objects.filter(user=request.user, course=course).first()


def _course_crumbs(course, *tail):
    return [('Courses', reverse('learning:course_list')), (course.title, course.get_absolute_url()), *tail]


def _curriculum(course):
    return course.modules.prefetch_related(Prefetch('lessons', queryset=Lesson.objects.order_by('order', 'id')))


def _first_unpassed_quiz(enrollment):
    passed = enrollment.passed_quiz_ids()
    return enrollment.course.quizzes.filter(published=True).exclude(id__in=passed).first()


def course_list(request):
    courses = Course.live.annotate(lesson_count=Count('modules__lessons'))
    page_obj = Paginator(courses, 9).get_page(request.GET.get('page'))
    enrolled_ids = set()
    if request.user.is_authenticated:
        enrolled_ids = set(Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True))
    return render(request, 'learning/course_list.html', {
        'page_obj': page_obj, 'enrolled_ids': enrolled_ids, 'crumbs': [('Courses', None)],
    })


def course_detail(request, slug):
    course = get_object_or_404(Course.live, slug=slug)
    lessons = course.ordered_lessons()
    return render(request, 'learning/course_detail.html', {
        'course': course,
        'modules': _curriculum(course),
        'enrollment': _enrollment(request, course),
        'checkout_total': total_with_zainpay_charge(course.price),
        'processing_fee': processing_fee(course.price),
        'lesson_count': lessons.count(),
        'total_minutes': lessons.aggregate(m=Sum('duration_minutes'))['m'],
        'quizzes': course.quizzes.filter(published=True).annotate(question_count=Count('questions')),
        'seo_title': course.get_seo_title(course.title),
        'seo_description': course.get_meta_description(course.short_description),
        'crumbs': [('Courses', reverse('learning:course_list')), (course.title, None)],
    })


@login_required
def course_learn(request, slug):
    """Resume: jump to the first lesson the student hasn't finished."""
    course = get_object_or_404(Course.live, slug=slug)
    enrollment = _enrollment(request, course)
    if not enrollment:
        return redirect(course)
    lessons = list(course.ordered_lessons())
    if not lessons:
        messages.info(request, 'Lessons for this course are being prepared. Check back soon.')
        return redirect('accounts:dashboard')
    done = enrollment.completed_lesson_ids()
    target = next((lesson for lesson in lessons if lesson.id not in done), None)
    if target is None:
        quiz = _first_unpassed_quiz(enrollment)
        if quiz:
            return redirect(quiz)
        target = lessons[0]
    return redirect(target)


def lesson_view(request, slug, lesson_id):
    course = get_object_or_404(Course.live, slug=slug)
    lesson = get_object_or_404(Lesson.objects.select_related('module'), pk=lesson_id, module__course=course)
    enrollment = _enrollment(request, course)
    if not enrollment and not lesson.is_free_preview:
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        messages.info(request, 'Enroll in this course to unlock this lesson.')
        return redirect(course)

    lessons = list(course.ordered_lessons())
    idx = next(i for i, item in enumerate(lessons) if item.id == lesson.id)
    completed = enrollment.completed_lesson_ids() if enrollment else set()
    passed = enrollment.passed_quiz_ids() if enrollment else set()
    return render(request, 'learning/lesson.html', {
        'course': course, 'lesson': lesson, 'enrollment': enrollment,
        'modules': _curriculum(course),
        'quizzes': course.quizzes.filter(published=True),
        'completed_ids': completed, 'passed_quiz_ids': passed,
        'is_completed': lesson.id in completed,
        'prev_lesson': lessons[idx - 1] if idx > 0 else None,
        'next_lesson': lessons[idx + 1] if idx + 1 < len(lessons) else None,
        'progress': enrollment.progress_percent() if enrollment else 0,
        'lesson_number': idx + 1, 'lesson_total': len(lessons),
        'seo_title': f'{lesson.title} · {course.title}',
        'crumbs': _course_crumbs(course, (lesson.title, None)),
    })


@login_required
@require_POST
def complete_lesson(request, slug, lesson_id):
    course = get_object_or_404(Course.live, slug=slug)
    lesson = get_object_or_404(Lesson, pk=lesson_id, module__course=course)
    enrollment = _enrollment(request, course)
    if not enrollment:
        return redirect(course)
    LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    if enrollment.refresh_completion():
        messages.success(request, 'Congratulations — you have completed this course!')
        if course.certificate_enabled:
            return redirect('learning:certificate', slug=course.slug)
    return redirect('learning:course_learn', slug=course.slug)


@login_required
def quiz_view(request, slug, quiz_id):
    course = get_object_or_404(Course.live, slug=slug)
    quiz = get_object_or_404(Quiz, pk=quiz_id, course=course, published=True)
    enrollment = _enrollment(request, course)
    if not enrollment:
        messages.info(request, 'Enroll in this course to take its quizzes.')
        return redirect(course)
    questions = list(quiz.questions.all())
    context = {
        'course': course, 'quiz': quiz, 'questions': questions,
        'best': quiz.attempts.filter(enrollment=enrollment).order_by('-score').first(),
        'seo_title': f'{quiz.title} · {course.title}',
        'crumbs': _course_crumbs(course, (quiz.title, None)),
    }

    if request.method == 'POST' and questions:
        answers = {str(q.id): request.POST.get(f'q{q.id}', '') for q in questions}
        unanswered = [q for q in questions if answers[str(q.id)] not in dict(q.options())]
        if unanswered:
            context.update(answers=answers, error='Please answer every question before submitting.')
            return render(request, 'learning/quiz.html', context)
        correct = sum(1 for q in questions if answers[str(q.id)] == q.correct_option)
        score = round(100 * correct / len(questions))
        attempt = QuizAttempt.objects.create(enrollment=enrollment, quiz=quiz, score=score,
                                             passed=score >= quiz.pass_mark, answers=answers)
        completed_course = enrollment.refresh_completion()
        context.update(attempt=attempt, answers=answers, correct=correct,
                       completed_course=completed_course,
                       next_quiz=_first_unpassed_quiz(enrollment) if attempt.passed else None)
        return render(request, 'learning/quiz_result.html', context)

    return render(request, 'learning/quiz.html', context)


@login_required
def certificate(request, slug):
    course = get_object_or_404(Course.live, slug=slug)
    enrollment = _enrollment(request, course)
    if not enrollment or not course.certificate_enabled:
        raise Http404
    cert = Certificate.objects.filter(enrollment=enrollment).first()
    if not cert:
        if not enrollment.refresh_completion():
            messages.info(request, 'Finish every lesson and pass every quiz to earn your certificate.')
            return redirect('learning:course_learn', slug=course.slug)
        name = request.user.get_full_name() or request.user.email
        cert, _ = Certificate.objects.get_or_create(
            enrollment=enrollment, defaults={'student_name': name, 'course_title': course.title},
        )
    return redirect(cert)


def certificate_verify(request, code):
    cert = get_object_or_404(Certificate.objects.select_related('enrollment__course'), code=code.upper())
    verify_url = request.build_absolute_uri(cert.get_absolute_url())
    return render(request, 'learning/certificate.html', {
        'cert': cert, 'verify_url': verify_url,
        'is_owner': request.user.is_authenticated and cert.enrollment.user_id == request.user.id,
        'seo_title': f'Certificate {cert.code}',
    })
