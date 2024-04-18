from django.contrib import admin
from django.urls import path

from .views.superadmindashboardviews import (
    ActiveRegisteredCustomerCountView,
    CountOfActiveRegistrationPerCoure, 
    CourseCountView,
    GraphOfProgressPerCourseView, 
)

from .views.registercourseviews import (
    CourseCustomerRegistrationView,
    LMSCustomerListView,
    ManageCourseRegistrationRecordStatusView
)
from .views.coursesviews import (
    CourseView,
    ManageCourseView,
    FirstVersionActiveCourseListView,
    DerivedVersionActiveCourseListView,
)
from .views.coursecontentviews import (
    CourseStructureView,
    ReadingMaterialView,
    QuizView,
    EditQuizInstanceOnConfirmationView,
    NotificationBasedOnCourseDisplayView)


from .views.quizcontentviews import (
    ChoicesView,
    EditingQuestionInstanceOnConfirmationView,
    QuestionView,
    QuizTake,
    dummy_quiz_index,
)
from .views.enrollcourseviews import( 
   CourseEnrollmentView,
    DisplayCourseListView,
    UserListForEnrollmentView,
    ManageCourseEnrollmentView
    )
    
urlpatterns = [
    #courseview.py  views url
    
    #coursemanagementviews.py views url
    
    #registercourseviews.py views url
    path('lms-customer/', LMSCustomerListView.as_view(), name='lms-customer-list'),
    path('course-register-record/', CourseCustomerRegistrationView.as_view(), name='course-register-record'),
    path('manage-status/register-records/', ManageCourseRegistrationRecordStatusView.as_view(), name='manage-register-records'), 
        
    #superadmindashboardviews.py views url
    path('dashboard/sa/registration/count/', ActiveRegisteredCustomerCountView.as_view(), name='active-registration-count'),
    path('dashboard/sa/active_registration-per-course/count/', CountOfActiveRegistrationPerCoure.as_view(), name='active_registration-per-course-count'),
    path('dashboard/sa/progress-per-course/count/', GraphOfProgressPerCourseView.as_view(), name='not_started-per-course-count'),
    path('dashboard/sa/course/count/', CourseCountView.as_view(), name='course-count'),

    # coursesviews.py view urls
    path('courses/', CourseView.as_view(), name='courses'), #*
    path('manage/course/', ManageCourseView.as_view(), name='manage-course'), #*
    path('courses/active/v1/', FirstVersionActiveCourseListView.as_view(), name='active-first-version-courses-list'),
    path('courses/derived-active/<int:course_id>/', DerivedVersionActiveCourseListView.as_view(), name='active-derived-version-course-list'),
    
    # coursecontentviews.py view urls
    path('course/<int:course_id>/structure/', CourseStructureView.as_view(), name='course-structure'), #*
    path('course/<int:course_id>/reading-material/', ReadingMaterialView.as_view(), name='reading-material'), #*
    path('course/<int:course_id>/quiz/', QuizView.as_view(), name='quiz'), #*
    path('course/<int:course_id>/notifications/', NotificationBasedOnCourseDisplayView.as_view(), name='course-notifications'),
    path('course/<int:course_id>/quiz/<int:quiz_id>/edit/', EditQuizInstanceOnConfirmationView.as_view(), name='edit_quiz_instance_confirmation'),

    # quizcontentviews.py views urls
    path('course/<int:course_id>/quiz/<int:quiz_id>/question/', QuestionView.as_view(), name='reading-material'), #10
    path('question/<int:question_id>/choices/', ChoicesView.as_view(), name='question-choice'),  #11
    path('<int:pk>/quiz/<slug:quiz_slug>/take/', QuizTake.as_view(), name="quiz_take"), #12      href="{% url 'quiz_take' pk=course.pk slug=quiz.slug %}
    path('course/<int:course_id>/quiz/<int:quiz_id>/question/', EditingQuestionInstanceOnConfirmationView.as_view(), name='editing-question-instance-on-confirmation'),

    
    #enrollcourseviews.py views url
    path('display/registered-course/', DisplayCourseListView.as_view(), name='course-list'), 
    path('display/users/', UserListForEnrollmentView.as_view(), name='users-list'), 
    path('course-enrollments/', CourseEnrollmentView.as_view(), name='course-enrollments-record'), 
    path('manage-enrollment/', ManageCourseEnrollmentView.as_view(), name='manage_enrollment'),
    

]