from rest_framework import permissions
from backend.models.coremodels import UserRolePrivileges
import json


'''this is how base permission works :

from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

'''

'''
allowed_resources:
1- LMS
2- Course Customer Registration
3- Course Enrollment
4- Courses
5- Course Management
6- Dashboard
'''

class SuperAdminMixin:
    # permission_classes = [permissions.IsAuthenticated]
 
    def has_super_admin_privileges(self, request):
        super_admin_resources = {1, 2, 4, 5, 6}  
       
        # Check if the user is authenticated
        if not request.user:
            return False
       
        user = request.data.get('user')
        print("super")
        user_privileges = UserRolePrivileges.objects.filter(role= user['role']) # role= user.role
        print(user_privileges)
        print("super")
        privileged_resources = {privilege.resource.id for privilege in user_privileges}
        print(privileged_resources)
        return super_admin_resources == privileged_resources
class ClientAdminMixin:
    # permission_classes = [permissions.IsAuthenticated]
    
    def has_client_admin_privileges(self, request):
        client_admin_resources = {1, 3, 4, 6}  
    
        user = request.data.get('user')
        print("client-admin")
        user_privileges = UserRolePrivileges.objects.filter(role= user['role']) # role= user.role
        privileged_resources = {privilege.resource.id for privilege in user_privileges}
        print(privileged_resources)
        return client_admin_resources == privileged_resources
    
class ClientMixin:
    # permission_classes = [permissions.IsAuthenticated]
    
    def has_client_privileges(self, request):
        client_resources = {1, 4, 6} 
        user = request.data.get('user')
        print("client")
        user_privileges = UserRolePrivileges.objects.filter(role= user['role'])
        privileged_resources = {privilege.resource.id for privilege in user_privileges}
        print(privileged_resources)
        return client_resources == privileged_resources
    


"""
    class ClientMixin:
        def has_client_privileges(self, request):
            # Define client resources that the user should have access to
            client_resources = {1, 4, 6}  # Example set of client resources

            # Retrieve the user from the request
            user = request.user

            # Assuming 'role' is a property of the user object
            user_role = user.role  # Adjust this based on your user model

            # Check if the user's role grants access to all client resources
            return user_role in client_resources
        """


