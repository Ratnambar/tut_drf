from django.urls import path, include

from rest_framework import routers
from quickstart import views


router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
]