import json
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from core.custom_mixins import (
    ClientAdminMixin,
    ClientMixin,
    SuperAdminMixin)
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from backend.models.allmodels import (
    Course,
    CourseRegisterRecord,
    UploadVideo,
    UploadReadingMaterial,
    CourseStructure,
    CourseEnrollment,
    Quiz,
    Question,
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from backend.serializers.createcourseserializers import (
    ActivateCourseSerializer,
    CourseSerializer, 
    CourseStructureSerializer,
    CreateChoiceSerializer,
    InActivateCourseSerializer, 
    QuizSerializer, 
    CreateCourseSerializer,
    CreateUploadReadingMaterialSerializer,
)
import pandas as pd # type: ignore
###
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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

class CourseStructureView(SuperAdminMixin, ClientAdminMixin, ClientMixin, APIView):
    """
    GET API for all users to list of courses structure for specific course
    
    POST API for super admin to create new instances of course structure while editing existing too
    
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id, format=None):
        try:
            course_structures = CourseStructure.objects.filter(course_id=course_id, active=True, deleted_at__isnull=True)
            if course_structures.exists():
                serializer = CourseStructureSerializer(course_structures, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No course structures found for the specified course ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, course_id, *args, **kwargs):

        if not self.has_super_admin_privileges(request):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        course = Course.objects.get(pk=course_id)
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if course.active:
            return Response({"error": "Course is active, cannot proceed"}, status=status.HTTP_403_FORBIDDEN)
        try:
            # Extract data from request body
            order_numbers = request.data.get('order_number', [])
            content_types = request.data.get('content_type', [])
            content_ids = request.data.get('content_id', [])
            
            # Check if lengths of lists are same
            if len(order_numbers) != len(content_types) or len(content_types) != len(content_ids):
                return Response({"error": "Length of order_number, content_type, and content_id lists must be the same"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create CourseStructure instances
            new_created_course_structure = []
            course_structure_data = []
            existing_course_structure_data = []
            edited_existing_course_structure_data = []
            
            for order_number, content_type, content_id in zip(order_numbers, content_types, content_ids):
                # Check if an instance with similar course_id, content_type, content_id, and order_number exists
                instance_exists = CourseStructure.objects.filter(course=course_id, content_type=content_type, content_id=content_id, order_number=order_number).exists()
                if instance_exists:
                    data = {
                        'course': course_id,
                        'order_number': order_number,
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    existing_course_structure_data.append(data)
                    course_structure_data.append(data)
                    # Skip mapping this instance
                    continue
                
                # Check if there's an existing instance with the same content_id and content_type but different order_number
                existing_instance = CourseStructure.objects.filter(course=course_id, content_type=content_type, content_id=content_id).first()
                if existing_instance:
                    # Update the order_number
                    existing_instance.order_number = order_number
                    existing_instance.save()
                    data = {
                        'course': course_id,
                        'order_number': order_number,
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    edited_existing_course_structure_data.append(data)
                    course_structure_data.append(data)
                else:
                    # Create a new instance
                    data = {
                        'course': course_id,
                        'order_number': order_number,
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    new_created_course_structure.append(data)
                    course_structure_data.append(data)
            
            # Save new instances
            serializer = CourseStructureSerializer(data=new_created_course_structure, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Course structure created successfully", 
                                "existing_record": existing_course_structure_data,
                                "edited_records" : edited_existing_course_structure_data,
                                "new_records": new_created_course_structure,
                                "all_record": course_structure_data
                                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ReadingMaterialView(SuperAdminMixin, ClientAdminMixin, ClientMixin, APIView):
    """
    GET API for all users to instance of reading material for specific course while list of reading material for specific course for super admin too.
    
    POST API for super admin to create new instances of course structure while editing existing too
    
    """
    
    def get(self, request, course_id, format=None):
        
        try:
            user = request.user
            if not user:
                return Response({"error": "Request body have no user"}, status=status.HTTP_400_BAD_REQUEST)
            actively_enrolled = CourseEnrollment.objects.filter(course=course_id, user=user.id, active=True).exists()
            actively_registered = CourseRegisterRecord.objects.filter(course=course_id, customer=user.customer.id, active=True).exists()
            if not self.has_super_admin_privileges(request) or not actively_enrolled or not actively_registered :
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
            content_id = request.query_params.get('content_id')
            list_mode = request.query_params.get('list', '').lower() == 'true'  # Check if list mode is enabled
            if content_id:
                reading_material = UploadReadingMaterial.objects.get(
                    courses__id=course_id, 
                    id=content_id, 
                    active=True, 
                    deleted_at__isnull=True
                    )
                if reading_material :
                    serializer = ReadingMaterialSerializer(reading_material)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            elif list_mode:
                reading_materials = UploadReadingMaterial.objects.filter(
                    courses__id=course_id, 
                    active=True, 
                    deleted_at__isnull=True
                )
                serializer = ReadingMaterialListPerCourseSerializer(reading_materials, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Specify 'content_id' or enable 'list' mode in query parameters."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, course_id, *args, **kwargs):
        
        if not self.has_super_admin_privileges(request):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        course = Course.objects.get(pk=course_id)
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if course.active:
            return Response({"error": "Course is active, cannot proceed"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not data:
            return Response({"error": "Request body is empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = CreateUploadReadingMaterialSerializer(data=data)
            if serializer.is_valid():
                # Set additional fields
                serializer.validated_data['courses'] = [course_id]
                reading_material = serializer.save()
                # If original_course is null, only save reading material
                if course.original_course is None:
                    return Response({"message": "Reading material created successfully"}, status=status.HTTP_201_CREATED)
                else:
                    # If original_course is not null, also create a CourseStructure entry
                    try:
                        last_order_number = CourseStructure.objects.filter(course=course).latest('order_number').order_number
                    except CourseStructure.DoesNotExist:
                        last_order_number = 0
                    # Create new CourseStructure instance
                    course_structure_data = {
                        'course': course_id,
                        'order_number': last_order_number + 1,
                        'content_type': 'reading',
                        'content_id': reading_material.pk
                    }
                    course_structure_serializer = CourseStructureSerializer(data=course_structure_data)
                    if course_structure_serializer.is_valid():
                        course_structure_serializer.save()
                        return Response({"message": "Reading material created successfully"}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error": course_structure_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class QuizView(SuperAdminMixin, ClientAdminMixin, ClientMixin,APIView):
    """
        get: to retrieve the quiz of course in url (for authorized all)
        post: to create quiz instances for course in url (for super admin only)
    """
    def get(self, request, course_id,format=None):
        try:
            
            content_id = request.query_params.get('content_id')
            list_mode = request.query_params.get('list', '').lower() == 'true'  # Check if list mode is enabled
            if content_id:
                user = request.user
                actively_enrolled = CourseEnrollment.objects.filter(course=course_id, user=user.id, active=True).exists()
                actively_registered = CourseRegisterRecord.objects.filter(course=course_id, customer=user.customer.id, active=True).exists()
                if not self.has_super_admin_privileges(request) or not actively_enrolled or not actively_registered :
                    return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
                quiz = Quiz.objects.get(
                    courses__id=course_id, 
                    id=content_id, 
                    active=True, 
                    deleted_at__isnull=True
                    )
                if quiz:
                    serializer = QuizSerializer(quiz)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No quiz found for the specified ID"}, status=status.HTTP_404_NOT_FOUND)
            elif list_mode:
                if not self.has_super_admin_privileges(request):
                    return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
                quizzes = Quiz.objects.filter(
                    courses__id=course_id, 
                    active=True, 
                    deleted_at__isnull=True
                )
                serializer = QuizListPerCourseSerializer(quizzes, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Specify 'content_id' or enable 'list' mode in query parameters."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, course_id, *args, **kwargs):
        if not self.has_super_admin_privileges(request):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        course = Course.objects.get(pk=course_id)
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if course.active:
            return Response({"error": "Course is active, cannot proceed"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not data:
            return Response({"error": "Request body is empty"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Validate and save quiz
            requested_data = request.data.copy()
            requested_data['courses'] = [course_id]
            serializer = QuizSerializer(data=requested_data)
            if serializer.is_valid():
                quiz = serializer.save()
                # If original_course is null, only save quiz
                if course.original_course is None:
                    return Response({"message": "Quiz created successfully"}, status=status.HTTP_201_CREATED)
                else:
                    # If original_course is not null, also create a CourseStructure entry
                    try:
                        last_order_number = CourseStructure.objects.filter(course=course).latest('order_number').order_number
                    except CourseStructure.DoesNotExist:
                        last_order_number = 0
                    # Create new CourseStructure instance
                    course_structure_data = {
                        'course': course_id,
                        'order_number': last_order_number + 1,
                        'content_type': 'quiz',
                        'content_id': quiz.pk
                    }
                    course_structure_serializer = CourseStructureSerializer(data=course_structure_data)
                    if course_structure_serializer.is_valid():
                        course_structure_serializer.save()
                        return Response({"message": "Quiz created successfully"}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error": course_structure_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)