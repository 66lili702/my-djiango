from django.urls import path
from . import views
from . import dashboard_views

app_name = 'main_app'

urlpatterns = [
    path('', views.index, name='index'),


    # 认证相关
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('houses/', views.house_list, name='house_list'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/', dashboard_views.simple_dashboard, name='dashboard'),
    path('dashboard/', views.professional_dashboard, name='professional_dashboard'),
    path('echarts-dashboard/', views.echarts_dashboard, name='echarts_dashboard'),
    path('ai-analysis/', views.ai_analysis, name='ai_analysis'),
    # 只保留这一行
]