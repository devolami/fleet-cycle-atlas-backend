from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogEntryViewSet

router = DefaultRouter()
router.register(r'logs', LogEntryViewSet, basename='logbook-trip')
urlpatterns = [
    path('', include(router.urls))
]