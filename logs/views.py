import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from .models import DroneLog
from .forms import DroneLogForm
from .report_generator import generate_pdf_report

def home(request):
    """ Render home page with file upload form """
    return render(request, "logs/home.html")

def upload_file(request):
    """ Handles file uploads """
    if request.method == "POST":
        form = DroneLogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("log_list")  # Redirect to logs page
    else:
        form = DroneLogForm()
    return render(request, "logs/upload.html", {"form": form})

def log_list(request):
    """ Display all uploaded drone logs """
    logs = DroneLog.objects.all()
    return render(request, "logs/log_list.html", {"logs": logs})

def view_log(request, log_id):
    """View parsed data and allow column selection for report"""
    log = get_object_or_404(DroneLog, id=log_id)

    # Read CSV file
    df = pd.read_csv(log.file.path)

    # Extract column names
    columns = df.columns.tolist()

    # Convert DataFrame to HTML for viewing
    table_data = df.to_html(classes="table table-bordered")

    return render(request, "logs/view_log.html", {"table_data": table_data, "log": log, "columns": columns})

def generate_report(request, log_id, report_type):
    """Generate and download a report (PDF) with selected columns"""
    log = get_object_or_404(DroneLog, id=log_id)

    # Read CSV file
    df = pd.read_csv(log.file.path)

    # Get selected columns from form
    selected_columns = request.POST.getlist("columns")

    if not selected_columns:  # If no columns are selected, include all
        selected_columns = df.columns.tolist()

    if report_type == "pdf":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="log_report_{log_id}.pdf"'

        # ✅ Pass only selected columns to PDF report
        generate_pdf_report(df[selected_columns], response)
        
        return response
    
    return render(request, "logs/report_preview.html", {"data": df.to_html(classes="table table-bordered"), "log": log})