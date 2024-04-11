from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from backend.models.allmodels import (
    Course,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory,
    UploadReadingMaterial,
    UploadVideo
)
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    FormView,
    CreateView,
    FormView,
    UpdateView,
)

from backend.forms import (
    QuestionForm,
)
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from backend.models.coremodels import *
from backend.serializers.courseserializers import *

# TODO:
'''
course_list display for different type of users :
    god admin : when he see all courses , he should get all data except summary on the list of courses [course table]
    employer/client-admin : when he see list of courses in dashboard ; courses on which he is registered and their active status[courseregisterrecord]
                            for enrollment [courses for which registration is active [true]] [courseregisterrecord] [RegisterCoursesOnCostumerListDisplayView]
    employee : courses on which he is enrolled and are active themselves and if user is active for this enrollment too
'''


# @method_decorator([login_required], name="dispatch")
class QuizTake(FormView):
    form_class = QuestionForm
    template_name = "question.html"
    result_template_name = "result.html"

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, slug=self.kwargs["quiz_slug"])
        self.course = get_object_or_404(Course, pk=self.kwargs["pk"])
        quiz_questions_count = self.quiz.questions.count()
        course = get_object_or_404(Course, pk=self.kwargs["pk"])

        if quiz_questions_count <= 0:
            messages.warning(request, f"Question set of the quiz is empty. try later!")
            return redirect("course-structure", self.course.id) # redirecting to previous page as this quiz can't be started.
# send here SingleCourseStructureListDisplayView
        # =================================================================
        user_header = request.headers.get("user")
        enrolled_user = get_object_or_404(User, pk=13)
        # ===============================
        # enrolled_user = request.user
        self.sitting = QuizAttemptHistory.objects.user_sitting(
            enrolled_user,
            self.quiz, 
            self.course
        )

        if self.sitting is False:
            messages.info(
                request,
                f"You have already sat this exam and only one sitting is permitted",
            )
            return redirect("course-structure", self.course.id)

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()
        form_class = self.form_class

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        self.form_valid_user(form)
        if self.sitting.get_first_question() is False:
            self.sitting.mark_quiz_complete()
            return self.final_result_user()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context["question"] = self.question
        context["quiz"] = self.quiz
        context["course"] = get_object_or_404(Course, pk=self.kwargs["pk"])
        if hasattr(self, "previous"):
            context["previous"] = self.previous
        if hasattr(self, "progress"):
            context["progress"] = self.progress
        return context

    def form_valid_user(self, form):
        # =================================================================
        user_header = self.request.headers.get("user")
        enrolled_user = get_object_or_404(User, pk=13)
        # ===============================
        # enrolled_user = request.user
        progress, _ = Progress.objects.get_or_create(enrolled_user=enrolled_user)
        guess = form.cleaned_data["answers"]
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {
                "previous_answer": guess,
                "previous_outcome": is_correct,
                "previous_question": self.question,
                "answers": self.question.get_choices(),
                "question_type": {self.question.__class__.__name__: True},
            }
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            "course": get_object_or_404(Course, pk=self.kwargs["pk"]),
            "quiz": self.quiz,
            "score": self.sitting.get_current_score,
            "max_score": self.sitting.get_max_score,
            "percent": self.sitting.get_percent_correct,
            "sitting": self.sitting,
            "previous": self.previous,
            "course": get_object_or_404(Course, pk=self.kwargs["pk"]),
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results["questions"] = self.sitting.get_questions(with_answers=True)
            results["incorrect_questions"] = self.sitting.get_incorrect_questions

        if (
            self.quiz.exam_paper is False
        ):
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)

def dummy_quiz_index(request, course_id):
    course = Course.objects.get(pk=course_id)
    return render(request, 'quiz_index.html', {'course_id': course_id, 'course': course})

