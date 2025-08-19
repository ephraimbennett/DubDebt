# project/collect_urls.py
from django.urls import path, include

urlpatterns = [
    path("", include("main.urls")),  # main app at root
]
