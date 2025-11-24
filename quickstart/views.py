import requests
from django.conf import settings
from django.shortcuts import render
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, GroupSerializer
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, permission_classes
from oauth2_provider import urls as oauth2_urls
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login

# Create your views here.
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['-date_joined']

    def get_permissions(self):
        """
        Allow any authenticated session (e.g. Django/allauth login) to read users,
        but require OAuth scope for mutating operations.
        """
        if self.action in ['list', 'retrieve', 'recent_users']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
        return [permission() for permission in permission_classes]

    @permission_classes([AllowAny])  # Allow anyone to create user (registration)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = request.data.get('password')
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'User created successfully!',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User Updated Successfully !."}, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
    def destroy(self, request, *args, **kwargs):
        instance  = self.get_object()
        instance.delete()
        return Response({"message": "User Deleted Successfully !."}, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User Partially Updated Successfully!."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    # @permission_classes([IsAuthenticated])
    def recent_users(self, request, *args, **kwargs):
        recent_users = self.queryset[:5]
        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']

def home(request):
    # Pass environment variables to template
    context = {
        'google_client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri('/api/dashboard/'),
    }
    return render(request, 'home.html', context)


def dashboard(request):
    """
    Handle the OAuth redirect (authorization code grant) and fetch API data.
    """
    code = request.GET.get('code')
    if not code:
        return render(
            request,
            'dashboard.html',
            {
                'users': [],
                'error': 'Missing authorization code. Please log in again.',
            },
            status=400,
        )
    
    # Exchange authorization code for Google access token
    # Access client_id and secret from settings
    google_client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
    google_client_secret = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
    
    token_resp = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': request.build_absolute_uri('/api/dashboard/'),
            'client_id': google_client_id,
            'client_secret': google_client_secret,
        },
    )
    
    if token_resp.status_code != 200:
        return render(
            request,
            'dashboard.html',
            {
                'users': [],
                'error': f'Failed to exchange token: {token_resp.text}',
            },
            status=400,
        )
    
    google_token_data = token_resp.json()
    google_access_token = google_token_data.get('access_token')
    
    if not google_access_token:
        return render(
            request,
            'dashboard.html',
            {
                'users': [],
                'error': 'No access token received from Google.',
            },
            status=400,
        )
    
    # Get user info from Google using the access token
    user_info_resp = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {google_access_token}'}
    )
    
    if user_info_resp.status_code != 200:
        return render(
            request,
            'dashboard.html',
            {
                'users': [],
                'error': f'Failed to get user info from Google: {user_info_resp.text}',
            },
            status=400,
        )
    
    google_user_data = user_info_resp.json()
    email = google_user_data.get('email')
    if not email:
        return render(
            request,
            'dashboard.html',
            {
                'users': [],
                'error': 'No email found in Google user data.',
            },
            status=400,
        )
    
    username = google_user_data.get('email', '').split('@')[0]  # Use email prefix as username
    first_name = google_user_data.get('given_name', '')
    last_name = google_user_data.get('family_name', '')
    
    # Get or create Django user
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Create new user if doesn't exist
        # Handle case where username might already exist
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
    
    # Log the user in (for session-based auth)
    login(request, user)
    
    # Generate Django JWT token for API calls
    refresh = RefreshToken.for_user(user)
    django_access_token = str(refresh.access_token)
    
    # Now use Django JWT token to call the API
    api_resp = requests.get(
        request.build_absolute_uri('/api/users/'),
        headers={'Authorization': f'Bearer {django_access_token}'}
    )
    
    if api_resp.status_code == 200:
        users = api_resp.json()
        return render(request, 'dashboard.html', {'users': users})
    else:
        return render(
            request,
            'dashboard.html',
            {
                'users': [],
                'error': f'API call failed: {api_resp.status_code} - {api_resp.text}',
            },
            status=api_resp.status_code,
        )