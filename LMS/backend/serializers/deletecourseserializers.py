from rest_framework import serializers
from backend.models.allmodels import (
    Choice, 
    Course, 
    CourseStructure,
    Notification,
    Question, 
    UploadReadingMaterial,
    UploadVideo, 
    Quiz
)
class EditCourseInstanceSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    summary = serializers.CharField(required=True)

    def validate(self, data):
        if not data['title'] or not data['summary']:
            raise serializers.ValidationError("Title and summary cannot be empty")
        return data
    
class DeleteSelectedCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(id=value)
            if course.active:
                raise serializers.ValidationError("Course must be inactive before deletion.")
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")
        return value
    
