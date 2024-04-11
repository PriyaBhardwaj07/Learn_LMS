from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from backend.models.allmodels import (
    Course,
    CourseCompletionStatusPerUser,
    CourseRegisterRecord,
)
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator

# to be taken from anuj and lavanya
# =================================================================
# employee dashboard
# =================================================================

class CreateCourseCompletionStatusPerUserView(APIView):
    """
        allowed for client admin
        POST request
        triggered after course enrollment records creation , similar to that one.
                in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
                        each course in list will be mapped for all users in list
        while creating instance :
            enrolled_user = request body
            course = request body
            completion_status = (default=False)
            in_progress_status = (default=False)
            created_at = (auto_now_add=True)
    """
    pass

class CreateQuizScoreView(APIView):
    """
        allowed for client admin
        POST request
        triggered after course enrollment records creation , similar to that one.
                in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
                        each course in list will be mapped for all users in list
        while creating instance :
            enrolled_user = request body
            course = request body
            total_quizzes_per_course = calculate in view for course by counting active quizzes in it
            completed_quiz_count = by default 0
            total_score_per_course = (default=0)
    """
    pass

class UpdateCompleteQuizCountView(APIView):
    """
        POST request
        triggered when quiz attempt history for that course, that user have completed =true , if set of quiz, course, user doesn't already have completed = true in table
        while updating instance :
            completed_quiz_count = increment by 1
    """
    pass

class UpdateTotalScorePerCourseView(APIView):
    """
        POST request
        triggered when quiz attempt history for that course, that user have completed =true 
        while updating instance :
            total_score_per_course -> calculate for it 
    """
    pass

class UpdateCourseCompletionStatusPerUserView(APIView):
    """
        POST request
        triggers when 
        total_quizzes_per_course = completed_quiz_count in quiz score for that user in request
        if total_quizzes_per_course == completed_quiz_count:
            completion_status=True and in_progress_status =False
        if total_quizzes_per_course > completed_quiz_count:
            completion_status=False and in_progress_status =True
    """
    pass

class DisplayClientCourseProgressView(APIView):
    """
        GET request
        for user in request, if he have data in course enrollment table
        
        display if user in request have active enrollment for the course
        display:
            completed_quiz_count
    """
    pass

class DisplayClientCourseCompletionStatusView(APIView):
    """
        GET request
        for user in request, if he have data in course enrollment table(active)
        display:
            completion_status or in_progress_status = Based on which is true for the user for thi course
    """
    pass

class CountOfAssignedCoursesView(APIView):
    """
    GET request
    for user in request , count the number of active enrollments he have in course enrollment table
    """
    pass

class CountClientCompletedCourseView(APIView):
    """
        GET request
        for the user filter the CourseCompletionStatusPerUser table
        and count courses for which completion_status= True and in_progress_status = False as completed courses
        and count courses for which completion_status= False and in_progress_status = True as completed courses
    """
    pass

# =================================================================
# employer dashboard
# =================================================================

class ActiveEnrolledUserCountPerCustomerView(APIView):
    """get api
    for client admin (count per customer id of user in request)
    """
    pass

class RegisteredCourseCountView(APIView):
    """get api
    for client admin (count per customer id of user in request)
    """
    pass

#---------
# graph : (per course)(for a customer) [employeer (client admin) dashboard]
class CountOfCompletionPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfInProgressPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfNotStartedPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass
#---------

