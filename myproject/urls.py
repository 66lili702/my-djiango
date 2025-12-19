"""
URL configuration for myproject project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    # 只保留这一个urlpatterns定义
]