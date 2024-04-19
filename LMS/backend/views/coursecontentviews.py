from django.utils import timezone
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from core.custom_permissions import CourseContentPermissions, SuperAdminOrGetOnly, SuperAdminPermission
from backend.models.coremodels import *
from backend.serializers.courseserializers import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.custom_mixins import (
    ClientAdminMixin,
    ClientMixin,
    SuperAdminMixin)
from rest_framework import status
from backend.models.allmodels import (
    Course,
    CourseRegisterRecord,
    UploadReadingMaterial,
    CourseStructure,
    CourseEnrollment,
    Quiz,
    Notification
)
from backend.serializers.editserializers import EditingQuizInstanceOnConfirmationSerializer
from backend.serializers.createcourseserializers import (
    CreateCourseStructureSerializer,
    CreateQuizSerializer,
    CreateUploadReadingMaterialSerializer,
)
from backend.serializers.courseserializers import (
    QuizSerializer,
)

from backend.serializers.editcourseserializers import (
    DeleteReadingMaterialSerializer,
    DeleteSelectedQuizSerializer,
    EditQuizInstanceSerializer,
    UploadReadingMaterialSerializer,
    NotificationSerializer
    
    )
from core.constants import filtered_display_list, manage_course_list

class CourseStructureView(APIView):
    """
    GET API for all users to list of courses structure for specific course
    
    POST API for super admin to create new instances of course structure while editing existing too
    
    """
    permission_classes = [SuperAdminOrGetOnly]
    def get(self, request, course_id, format=None):
        try:
            course_structures = CourseStructure.objects.filter(course_id=course_id, deleted_at__isnull=True) # active=True,
            if course_structures is not None:
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


class ReadingMaterialView(APIView):
    """
    GET API for all users to instance of reading material for specific course while list of reading material for specific course for super admin too.
    
    POST API for super admin to create new instances of course structure while editing existing too
    
    PUT API for super admin to edit reading material 
    
    PATCH API for super admin to delete reading material 
    
    """
    permission_classes = [CourseContentPermissions]
    def get(self, request, course_id, format=None):
        
        try:
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
                    print('starting with course structure')
                    # Create new CourseStructure instance
                    course_structure_data = {
                        # 'course': course_id,
                        'course' : course_id,
                        'order_number': last_order_number + 1,
                        'content_type': 'reading',
                        'content_id': reading_material.pk
                    }
                    print(course_structure_data)
                    course_structure_serializer = CreateCourseStructureSerializer(data=course_structure_data)
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
    
    def put(self, request, course_id, format=None):
        try:

            reading_material_id = request.data.get('reading_material_id')
            
            if reading_material_id is None:
                return Response({"error": "reading_material_id is required in the request body."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Get the reading material instance
                reading_material = get_object_or_404(UploadReadingMaterial, pk=reading_material_id)
                
                # Check if the associated course is active
                if reading_material.courses.filter(pk=course_id, active=True).exists():
                    return Response({"error": "Cannot edit reading material. Course is active."},
                                    status=status.HTTP_403_FORBIDDEN)

                # Validate request data
                serializer = UploadReadingMaterialSerializer(instance=reading_material, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(updated_at=timezone.now())

                # Return success response with message
                return Response({"message": "Reading material updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = str(e)
            if isinstance(e, (UploadReadingMaterial.DoesNotExist, ValidationError)):
                error_message = "Reading material not found." if isinstance(e, UploadReadingMaterial.DoesNotExist) else str(e)
                status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return Response({"error": error_message}, status=status_code)
    
    def patch(self, request, course_id, format=None):
        try:

            reading_material_id = request.data.get('reading_material_id')
            
            if reading_material_id is None:
                return Response({"error": "reading_material_id is required in the request body."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch the reading material instance
            reading_material = get_object_or_404(UploadReadingMaterial, pk=reading_material_id)
            
            # Validate request data
            serializer = DeleteReadingMaterialSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                # Check if the reading material is associated with other courses
                other_courses_count = reading_material.courses.exclude(id=course_id).count()
                if other_courses_count > 0:
                    # Only remove the relation with the current course
                    reading_material.courses.remove(course_id)
                else:
                    # No other courses are associated, soft delete the reading material
                    reading_material.deleted_at = timezone.now()
                    reading_material.active = False
                    reading_material.save()
                
                return Response({"message": "Reading material deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            error_message = str(e)
            if isinstance(e, (UploadReadingMaterial.DoesNotExist, ValidationError)):
                error_message = "Reading material not found." if isinstance(e, UploadReadingMaterial.DoesNotExist) else str(e)
                status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return Response({"error": error_message}, status=status_code)

class QuizView(APIView):
    """
        get: to retrieve the quiz of course in url (for authorized all)
        post: to create quiz instances for course in url (for super admin only)
        put : to edit quiz 
        patch : to delete a quiz 
    """
    permission_classes = [CourseContentPermissions]
    
    def get(self, request, course_id,format=None):
        try:
            
            content_id = request.query_params.get('content_id')
            list_mode = request.query_params.get('list', '').lower() == 'true'  # Check if list mode is enabled
            if content_id:
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
            requested_data['courses'] = course_id
            print(requested_data)
            serializer = CreateQuizSerializer(data=requested_data)
            if serializer.is_valid():
                quiz = serializer.save()
                course.quizzes.add(quiz)
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
                    course_structure_serializer = CreateCourseStructureSerializer(data=course_structure_data)
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
    
    def put(self, request, course_id, format=None):
        try:
            
            # Check if course exists
            course = Course.objects.get(pk=course_id)
            if course.active:
                return Response({"error": "Editing is not allowed for active courses."},
                                status=status.HTTP_403_FORBIDDEN)

            # Check if quiz exists
            quiz_id = request.data.get('quiz_id', None)
            if not quiz_id:
                return Response({"error": "Quiz ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)
            quiz = Quiz.objects.get(pk=quiz_id)
            if course not in quiz.courses.all():
                return Response({"error": "Quiz not found for the specified course."},
                                status=status.HTTP_404_NOT_FOUND)

            # Update quiz instance
            serializer = EditQuizInstanceSerializer(quiz, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            error_message = "Resource not found" if isinstance(e, ObjectDoesNotExist) else str(e)
            status_code = status.HTTP_404_NOT_FOUND if isinstance(e, ObjectDoesNotExist) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"error": error_message}, status=status_code)
    
    def patch(self, request, course_id, format=None):
        try:
            quiz_id = request.data.get('quiz_id', None)
            if not quiz_id:
                return Response({"error": "Quiz ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate request data
            serializer = DeleteSelectedQuizSerializer(data={'quiz_id': quiz_id})
            serializer.is_valid(raise_exception=True)
            
            # Fetch the quiz instance
            quiz = Quiz.objects.get(id=quiz_id)
            
            # Check if the quiz is associated with other courses
            other_courses_count = quiz.courses.exclude(id=course_id).count()
            if other_courses_count > 0:
                # Only remove the relation with the current course
                quiz.courses.remove(course_id)
            else:
                # No other courses are associated, soft delete the quiz
                quiz.deleted_at = timezone.now()
                quiz.active = False
                quiz.save()
                
            return Response({"message": "Quiz deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist as e:
            error_message = "Quiz not found" if isinstance(e, ObjectDoesNotExist) else "Internal Server Error"
            status_code = status.HTTP_404_NOT_FOUND if isinstance(e, ObjectDoesNotExist) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({"error": error_message}, status=status_code)

class NotificationBasedOnCourseDisplayView(SuperAdminMixin,ClientAdminMixin,ClientMixin,APIView):
    
    """  
    GET API : for all to get notification related to any update i courses
    """
    # permission_classes = [IsAuthenticated]

    def get(self, request, course_id, format=None):
        try:
            # user = request.user
            user = request.data.get('user')
            
            # Fetch notifications for the specified course
            notifications = Notification.objects.filter(course_id=course_id)
            
            if not notifications.exists():
                return Response({"message": "No notifications found"}, status=status.HTTP_404_NOT_FOUND)

            if self.has_super_admin_privileges(request):
              #  print('we are super')
                serializer = NotificationSerializer(notifications, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if self.has_client_admin_privileges(request):
               #  print('we are client')
                course_enrollment = CourseEnrollment.objects.get(user=user['id'], course_id=course_id)
                enrollment_date = course_enrollment.enrolled_at
                new_notifications = notifications.filter(created_at__gt=enrollment_date)
            
            serializer = NotificationSerializer(new_notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (CourseEnrollment.DoesNotExist, CourseRegisterRecord.DoesNotExist) as e:
            return Response({"error": "User is not enrolled or registered in this course."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EditQuizInstanceOnConfirmationView(APIView):
    """ 
    PUT API : for super admin to edit quiz if confirmation is true if not then new quiz is created
    """
    permission_classes = [SuperAdminPermission]
    def put(self, request, course_id, quiz_id, format=None):
        try:
            serializer = EditingQuizInstanceOnConfirmationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            confirmation = serializer.validated_data['confirmation']
            quiz = Quiz.objects.get(pk=quiz_id)
            course = quiz.courses.first()  # Assuming each quiz is related to only one course
            
            if confirmation:
                # Editing existing quiz instance
                if course.active:
                    return Response({"error": "Editing is not allowed for active courses."},
                                    status=status.HTTP_403_FORBIDDEN)

                quiz.title = serializer.validated_data.get('title', quiz.title)
                quiz.description = serializer.validated_data.get('description', quiz.description)
                quiz.answers_at_end = serializer.validated_data.get('answers_at_end', quiz.answers_at_end)
                quiz.exam_paper = serializer.validated_data.get('exam_paper', quiz.exam_paper)
                quiz.pass_mark = serializer.validated_data.get('pass_mark', quiz.pass_mark)
                quiz.updated_at = timezone.now()
                quiz.save()

                return Response({"message": "Quiz instance updated successfully."}, status=status.HTTP_200_OK)
            else:
                # Creating new quiz instance
                new_quiz = Quiz.objects.create(
                    title=serializer.validated_data.get('title'),
                    description=serializer.validated_data.get('description'),
                    answers_at_end=serializer.validated_data.get('answers_at_end'),
                    exam_paper=serializer.validated_data.get('exam_paper'),
                    pass_mark=serializer.validated_data.get('pass_mark'),
                )

                # Update CourseStructure entry with the new quiz id
                CourseStructure.objects.filter(course=course_id, content_type='quiz', content_id=quiz_id) \
                    .update(content_id=new_quiz.id)

                return Response({"message": "New quiz instance created successfully."}, status=status.HTTP_201_CREATED)
        
        except (Quiz.DoesNotExist, Exception) as e:
            if isinstance(e, Quiz.DoesNotExist):
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
