🛰️ Dronify - A Drone Log Forensic and Telemetry Analysis Framework

Dronify is a Django-based forensic analysis tool designed to process, parse, and visualize logs collected from drones. It supports features like drone telemetry graphing, EXIF metadata extraction, and the generation of forensic-style PDF and HTML reports. The framework is aimed at aiding digital forensic investigators and security researchers in analyzing UAV data effectively.


📌 Features

- 🔍 **Drone Log Upload and Parsing**  
  Upload `.csv` drone logs and parse flight data in tabular view.

- 📈 **Telemetry Visualization**  
  Plot 2D and 3D telemetry graphs based on user-selected columns.

- 📄 **EXIF Metadata Analysis**  
  Upload images and extract EXIF information using `ExifTool`.

- 🧾 **PDF and HTML Report Generation**  
  Generate forensic-style reports for logs, telemetry, and EXIF analysis.

- 🔐 **User Authentication**  
  Each user has their own dashboard and analysis data separation.

- 🧹 **Clear Logs and Reports**  
  Easily delete your uploaded logs and generated reports.


🏗️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS (Glassmorphism UI)
- **Libraries Used:**
  - `pandas`, `matplotlib`, `numpy`
  - `fpdf` (for PDF reports)
  - `ExifTool` (for image metadata extraction)
- **Visualization:** Matplotlib (2D/3D plotting)
  

📂 Project Structure
dronify/
├── logs/
│ ├── models.py
│ ├── views.py
│ ├── forms.py
│ ├── templates/logs/
│ └── static/css/
├── media/
├── templates/
├── static/
├── manage.py



⚙️ Installation Instructions

   ```bash
   git clone https://github.com/kalp1801/dronify.git
   cd dronify
   python -m venv myenv
   source myenv/bin/activate   # or `myenv\Scripts\activate` on Windows
   pip install -r requirements.txt
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
  ```

🧪 Sample Log Files
You can test the platform using drone .csv logs from:
  AirData UAV
  DJI Assistant logs
  Synthetic logs generated for testing


🚀 Future Enhancements
Integration with map-based GPS visualization.
Real-time telemetry parsing from live feeds.
Threat detection from anomalous flight behavior.
QR code embedded metadata retrieval.
OTP/email-based secure log sharing.


📬 Contact
📧 Email: ghack618@gmail.com
🌐 LinkedIn: www.linkedin.com/in/kalp-prajapati-b3598b221






