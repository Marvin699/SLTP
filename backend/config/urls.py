"""
URL configuration for the Smart Low-Altitude Emergency Transportation Teaching Platform.
The path-planning FastAPI routes are mounted in asgi.py, not here.
"""
from django.urls import path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
]

if settings.DEBUG:
    from django.urls import re_path
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
