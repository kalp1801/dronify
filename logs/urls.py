from django.urls import path
from . import views
from .views import generate_reports_page,generate_report_telemetry
# from .views import upload_telemetry, select_telemetry_column, plot_telemetry_graph,generate_report_telemetry

urlpatterns = [
    path("", views.home, name="home"),
    path("logs/", views.log_list, name="log_list"),
    path("logs/<int:log_id>/", views.view_log, name="view_log"),
    path("logs/<int:log_id>/report/<str:report_type>/", views.generate_report, name="generate_report"),
    path("upload/", views.upload_file, name="upload"),  

    #Telemetry
    path("logs/telemetry/upload/", views.upload_telemetry, name="upload_telemetry"),
    path("logs/telemetry/select/<int:file_id>/", views.select_telemetry_column, name="select_telemetry_column"),
    # urls.py
    path("logs/telemetry/plot/<int:file_id>/", views.plot_telemetry_graph, name="plot_telemetry_graph"),
    # path("logs/<int:log_id>/report/<str:report_type>/", generate_report_telemetry, name="generate_report"),
    # path("generate_report_telemetry/<int:file_id>/<str:report_type>/", generate_report_telemetry, name="generate_report_telemetry"),
    path("reports/", views.generate_reports_page, name="generate_reports"),
    # path("generate_report/<int:log_id>/<str:report_type>/", generate_report, name="generate_report"),
    path("telemetry/report/<int:file_id>/<str:report_type>/", generate_report_telemetry, name="generate_report_telemetry"),
    path("exif/analysis/", views.exif_analysis, name="exif_analysis"),
    path("exif/report/", views.download_exif_pdf, name="download_exif_pdf"),
    path('signup/', views.signup_view, name='signup'),
    path("telemetry/reports/", views.telemetry_reports_page, name="telemetry_reports"),
    path("exif/reports/", views.exif_reports_page, name="exif_reports"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("reports_dash/", views.reports_dashboard_view, name="reports_dashboard"),
    path("logs/clear/", views.clear_user_logs, name="clear_user_logs"),

    
    
]
