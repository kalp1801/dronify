import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from .models import DroneLog,TelemetryLog,EXIFLog
from .forms import DroneLogForm,TelemetryUploadForm,EXIFUploadForm
from .report_generator import generate_pdf_report
import base64
from fpdf import FPDF
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages




def home(request):
    """ Render home page with file upload form """
    return render(request, "logs/home.html")

def upload_file(request):
    if request.method == "POST":
        form = DroneLogForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.drone_model = form.cleaned_data["drone_model"]
            log.exhibit_no = form.cleaned_data["exhibit_no"]
            log.save()
            return redirect("log_list")
    else:
        form = DroneLogForm()
    return render(request, "logs/upload.html", {"form": form})




def log_list(request):
    logs = DroneLog.objects.filter(user=request.user)  # 👈 Show only current user's logs
    return render(request, "logs/log_list.html", {"logs": logs})



def view_log(request, log_id):
    log = get_object_or_404(DroneLog, id=log_id, user=request.user)
    df = pd.read_csv(log.file.path)
    columns = df.columns.tolist()
    table_data = df.to_html(classes="table table-bordered")
    return render(request, "logs/view_log.html", {"table_data": table_data, "log": log, "columns": columns})


def generate_report(request, log_id, report_type):
    log = get_object_or_404(DroneLog, id=log_id, user=request.user)

    # Read CSV file
    df = pd.read_csv(log.file.path)

    # Get selected columns from form
    selected_columns = request.POST.getlist("columns")
    if not selected_columns:  # If no columns are selected, include all
        selected_columns = df.columns.tolist()

    if report_type == "pdf":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="log_report_{log_id}.pdf"'

        # ✅ Pass only selected columns to PDF report, including user
        generate_pdf_report(
            df[selected_columns],
            response,
            request.user,
            drone_model=log.drone_model,
            exhibit_no=log.exhibit_no,
        )
        
        return response
    
    return render(request, "logs/generate_reports.html", {"data": df.to_html(classes="table table-bordered"), "log": log})




def log_details(request):
    log_file_name = "logs/name.csv"  # Fetch from uploaded files dynamically
    columns = [
        "time(millisecond)", "datetime(utc)", "latitude", "longitude",
        "height_above_takeoff(feet)", "height_above_ground_at_drone_location(feet)",
        "ground_elevation_at_drone_location(feet)", "altitude_above_seaLevel(feet)",
        "height_sonar(feet)", "speed(mph)", "distance(feet)", "mileage(feet)",
        "satellites", "gpslevel", "voltage(v)", "max_altitude(feet)", "max_ascent(feet)",
        "max_speed(mph)", "max_distance(feet)", "xSpeed(mph)", "ySpeed(mph)",
        "zSpeed(mph)", "compass_heading(degrees)", "pitch(degrees)", "roll(degrees)",
        "isPhoto", "isVideo"
    ]
    
    return render(request, "log_details.html", {"log_file_name": log_file_name, "columns": columns})


from bs4 import BeautifulSoup

# 🚀 Upload Telemetry File
def upload_telemetry(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        if not uploaded_file.name.endswith(".csv"):
            return render(request, "logs/upload_telemetry.html", {
                "form": TelemetryUploadForm(),
                "error": "Only .csv files are allowed."
            })

        form = TelemetryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.drone_model = form.cleaned_data["drone_model"]
            file_instance.exhibit_no = form.cleaned_data["exhibit_no"]
            file_instance.save()
            return redirect("select_telemetry_column", file_id=file_instance.id)
    else:
        form = TelemetryUploadForm()
    return render(request, "logs/upload_telemetry.html", {"form": form})






# 📊 Select Column for Visualization
def select_telemetry_column(request, file_id):
    file_instance = get_object_or_404(TelemetryLog, id=file_id, user=request.user)
    file_path = file_instance.file.path

    try:
        df = pd.read_csv(file_path, low_memory=False)
        columns = list(enumerate(df.columns.tolist()))

        if request.method == "POST":
           selected_indexes = request.POST.getlist("column_indexes")
        #    selected_indexes = request.POST.getlist("column_indexes")
           if selected_indexes:
                return redirect(f"{reverse('plot_telemetry_graph', args=[file_id])}?cols={','.join(selected_indexes)}")



    except Exception as e:
        return render(request, "logs/select_column.html", {
            "error": f"Error reading file: {e}"
        })

    return render(request, "logs/select_column.html", {
        "columns": columns,
        "file_id": file_id
    })



# 📈 Generate Telemetry Graph
from mpl_toolkits.mplot3d import Axes3D  # 3D plotting support
import json
def plot_telemetry_graph(request, file_id):
    file_instance = get_object_or_404(TelemetryLog, id=file_id, user=request.user)
    df = pd.read_csv(file_instance.file.path)

    col_indexes = request.GET.get("cols")
    if not col_indexes:
        return render(request, "logs/show_graph.html", {"error": "No columns selected."})

    try:
        selected_indexes = [int(i) for i in col_indexes.split(",")]
        graph_urls = []

        df.columns = [col.lower().strip() for col in df.columns]

        # ✅ 3D Coordinates (if exist)
        lat = df["latitude"].dropna().astype(float) if "latitude" in df.columns else None
        lon = df["longitude"].dropna().astype(float) if "longitude" in df.columns else None
        alt = df["altitude(feet)"].dropna().astype(float) if "altitude(feet)" in df.columns else None

        coords_3d = None
        if lat is not None and lon is not None and alt is not None:
            max_points = 1000
            if len(lat) > max_points:
                idx = np.linspace(0, len(lat) - 1, max_points).astype(int)
                lat, lon, alt = lat.iloc[idx], lon.iloc[idx], alt.iloc[idx]

            coords_3d = {
                "lat": lat.tolist(),
                "lon": lon.tolist(),
                "alt": alt.tolist(),
            }

        # 🔹 Generate 2D graphs as before
        for col_index in selected_indexes:
            col_name = df.columns[col_index]
            data = df[col_name].dropna().astype(float)

            if len(data) > 100:
                indices = np.linspace(0, len(data) - 1, 100).astype(int)
                data = data.iloc[indices]

            plt.figure(figsize=(10, 5))
            plt.plot(data, marker='o', linestyle='-', color='cyan')
            plt.title(f"Graph for: {col_name}")
            plt.xlabel("Index")
            plt.ylabel(col_name)
            plt.grid(True)

            graph_folder = os.path.join(settings.MEDIA_ROOT, "graphs", f"file_{file_id}")
            os.makedirs(graph_folder, exist_ok=True)
            img_path = os.path.join(graph_folder, f"{col_name}.png")
            plt.savefig(img_path)
            plt.close()

            graph_urls.append({
                "url": f"/media/graphs/file_{file_id}/{col_name}.png",
                "column": col_name
            })

        return render(request, "logs/show_graph.html", {
            "graph_urls": graph_urls,
            "file_id": file_id,
            "selected_indexes": col_indexes,
            "coords_3d": coords_3d,
        })

    except Exception as e:
        return render(request, "logs/show_graph.html", {"error": str(e)})




# 📝 Generate Report (PDF/HTML)
def generate_report_telemetry(request, file_id, report_type):
    file_instance = get_object_or_404(TelemetryLog, id=file_id, user=request.user)
    df = pd.read_csv(file_instance.file.path)
    col_indexes = request.GET.get("cols")

    if not col_indexes:
        return HttpResponse("No columns selected.", status=400)

    selected_indexes = [int(i) for i in col_indexes.split(",")]
    graphs = []
    sample_data_html = df.head(10).to_html(classes="table")

    for idx in selected_indexes:
        column = df.columns[idx]
        data = df[column].dropna().astype(float)

        if len(data) > 100:
            data = data.iloc[np.linspace(0, len(data) - 1, 100).astype(int)]

        plt.figure(figsize=(10, 5))
        plt.plot(data, marker='o', linestyle='-', color='cyan')
        plt.title(f"Graph for: {column}")
        plt.xlabel("Index")
        plt.ylabel(column)
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        graphs.append({
            "column": column,
            "image_base64": base64.b64encode(buffer.read()).decode()
        })
        buffer.close()
        plt.close()

    context = {
        "file_instance": file_instance,
        "telemetry_data": sample_data_html,
        "telemetry_graphs": graphs,
        "user": request.user
    }

    if report_type == "html":
        return render(request, "logs/report_template.html", context)

    return generate_pdf_report_telemetry(context)



# 📄 Generate PDF Report Function for Telemetry
def generate_pdf_report_telemetry(context):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Dronify - EXIF Metadata Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"File: {context['file_instance'].file.name}", ln=True)
    pdf.cell(0, 10, f"Generated By: {context['user'].username}", ln=True)
    pdf.cell(0, 10, f"Drone Model: {context['file_instance'].drone_model}", ln=True)
    pdf.cell(0, 10, f"Exhibit No.: {context['file_instance'].exhibit_no}", ln=True)
    pdf.ln(10)


    soup = BeautifulSoup(context["telemetry_data"], "html.parser")
    for row in soup.find_all("tr"):
        text = " | ".join([col.text.strip() for col in row.find_all(["td", "th"])])
        pdf.cell(0, 10, text[:100], ln=True)

    for graph in context["telemetry_graphs"]:
        image_data = base64.b64decode(graph["image_base64"])
        img_path = os.path.join(settings.MEDIA_ROOT, "temp_graph.png")
        with open(img_path, "wb") as f:
            f.write(image_data)
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Graph for: {graph['column']}", ln=True)
        pdf.image(img_path, x=10, w=180)
        os.remove(img_path)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="telemetry_report.pdf"'
    response.write(pdf.output(dest="S").encode("latin1"))
    return response




def telemetry_reports_page(request):
    telemetry_logs = TelemetryLog.objects.filter(user=request.user)  # 👈 Only user's telemetry
    return render(request, "logs/telemetry_reports.html", {"telemetry_logs": telemetry_logs})





@login_required
def generate_reports_page(request):
    logs = DroneLog.objects.filter(user=request.user)  # 👈 Only user's logs
    return render(request, "logs/generate_reports.html", {"logs": logs})




from django.utils import timezone

def generate_pdf_report(dataframe, response, user, drone_model="N/A", exhibit_no="N/A"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Dronify - Forensic Log Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    metadata = {
        "Username": user.username,
        "Drone Model": drone_model,
        "Exhibit No.": exhibit_no,
        "Report Generated On": timezone.now().strftime("%d-%b-%Y %I:%M %p"),
    }
    for key, value in metadata.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    col_width = pdf.w / (len(dataframe.columns) + 1)
    for col in dataframe.columns:
        pdf.cell(col_width, 8, str(col), border=1)
    pdf.ln()

    pdf.set_font("Arial", '', 9)
    for row in dataframe.itertuples(index=False):
        for cell in row:
            text = str(cell)
            if len(text) > 20:
                text = text[:17] + "..."
            pdf.cell(col_width, 8, text, border=1)
        pdf.ln()

    response.write(pdf.output(dest="S").encode("latin1"))



#ExifAnalysis
import exiftool

def exif_analysis(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        image_path = os.path.join(settings.MEDIA_ROOT, "exif_uploads", image_file.name)

        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, "wb+") as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        metadata = {}
        with exiftool.ExifTool() as et:
            meta = et.execute_json(image_path)[0]
            metadata = {k: str(v) for k, v in meta.items()}

        request.session["exif_metadata"] = metadata
        request.session["exif_filename"] = image_file.name

        return render(request, "logs/exif_output.html", {
            "metadata": metadata,
            "filename": image_file.name
        })

    return render(request, "logs/exif_upload.html")


from django.utils import timezone

def generate_pdf_report_exif(request, metadata, filename, user):
    pdf = FPDF()
    pdf.add_page()

    # Report header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Dronify - EXIF Metadata Report", ln=True, align="C")
    pdf.ln(10)

    # Metadata block (username only)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Filename: {filename}", ln=True)
    pdf.cell(0, 10, f"Generated On: {timezone.now().strftime('%d-%b-%Y %I:%M %p')}", ln=True)
    pdf.cell(0, 10, f"Analyst: {user.username}", ln=True)  # Only username
    # pdf.cell(0, 10, f"Location: "", ln=True)
    pdf.ln(10)

    # EXIF content
    pdf.set_font("Arial", "", 10)
    for key, value in metadata.items():
        line = f"{key}: {value}"
        if len(line) > 100:
            line = line[:97] + "..."
        pdf.cell(0, 8, line, ln=True)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="exif_report_{filename}.pdf"'
    response.write(pdf.output(dest="S").encode("latin1"))
    return response



def download_exif_pdf(request):
    metadata = request.session.get("exif_metadata")
    filename = request.session.get("exif_filename")

    if not metadata or not filename:
        return HttpResponse("No EXIF data available to generate PDF.", status=400)

    return generate_pdf_report_exif(request, metadata, filename, request.user)



def exif_reports_page(request):
    filename = request.session.get("exif_filename")
    has_data = filename is not None
    return render(request, "logs/exif_reports.html", {"has_data": has_data, "filename": filename})



# @login_required
# def generate_reports_page(request): 
#     logs = DroneLog.objects.all()
#     return render(request, "logs/generate_reports.html", {"logs": logs})


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from .forms import CustomUserCreationForm  # import the new form

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want to go after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})




@login_required
def dashboard_view(request):
    return render(request, "logs/dashboard.html")

@login_required
def reports_dashboard_view(request):
    return render(request, "logs/reports_dashboard.html")


@login_required
def clear_user_logs(request):
    if request.method == "POST":
        user_logs = DroneLog.objects.filter(user=request.user)
        count = user_logs.count()
        user_logs.delete()
        messages.success(request, f"{count} log(s) successfully deleted.")
        
        #Telemetry
        user_logs = TelemetryLog.objects.filter(user=request.user)
        count = user_logs.count()
        user_logs.delete()
        messages.success(request, f"{count} log(s) successfully deleted.")
        
        return redirect("log_list")  # or dashboard
    return HttpResponse("Invalid request method", status=405)
