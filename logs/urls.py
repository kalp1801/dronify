from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logs/", views.log_list, name="log_list"),
    path("logs/<int:log_id>/", views.view_log, name="view_log"),
    path("logs/<int:log_id>/report/<str:report_type>/", views.generate_report, name="generate_report"),
    path("upload/", views.upload_file, name="upload"),  
]
