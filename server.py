import csv
import json
import os
import socket
import threading
import webbrowser
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
ALLOWED_EXTENSIONS = {"csv"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

# ─────────────────────────────────────────────
#  PATIENT & DEVICE INFO (bisa diubah)
# ─────────────────────────────────────────────
PATIENT_INFO = {
    "pid": "ANON123456",
    "vid": "",
    "name": "ANON PATIENT",
    "gender": "male"
}
DEVICE_ID = "ANONDEVICE001"

COLUMN_MAP = {
    "ECG/HR":        {"test_name": "hr",        "label": "Heart Rate (ECG)",          "unit": "bpm",   "ref_range": "60-100"},
    "ECG/PVCs":      {"test_name": "ecg_pvcs",  "label": "PVCs",                      "unit": "/min"},
    "ECG/PAUSE_MIN": {"test_name": "ecg_pause", "label": "ECG Pause Min",             "unit": "/min"},
    "SpO2_A/SpO2":   {"test_name": "spo2_a",    "label": "Oxygen Saturation (A)",     "unit": "%",     "ref_range": "95-100"},
    "SpO2_B/SpO2":   {"test_name": "spo2_b",    "label": "Oxygen Saturation (B)",     "unit": "%",     "ref_range": "95-100"},
    "SpO2_B/SpO2Delta":{"test_name":"spo2_delta","label":"SpO2 Delta",                "unit": "%"},
    "PR/PR":         {"test_name": "pr",         "label": "Pulse Rate",               "unit": "bpm",   "ref_range": "60-100"},
    "RR/RR":         {"test_name": "rr",         "label": "Respiratory Rate",         "unit": "rpm",   "ref_range": "12-20"},
    "TEMP/T1":       {"test_name": "temp_t1",    "label": "Body Temperature T1",      "unit": "°C",    "ref_range": "36.0-37.5", "equipid": "ANONDEVICE002"},
    "TEMP/T2":       {"test_name": "temp_t2",    "label": "Body Temperature T2",      "unit": "°C",    "ref_range": "36.0-37.5", "equipid": "ANONDEVICE002"},
    "TEMP/TD":       {"test_name": "temp_td",    "label": "Temperature Difference",   "unit": "°C",    "equipid": "ANONDEVICE002"},
    "CNBP/SYS":      {"test_name": "bp_sys",     "label": "Blood Pressure Systolic",  "unit": "mmHg",  "ref_range": "90-140"},
    "CNBP/DIA":      {"test_name": "bp_dia",     "label": "Blood Pressure Diastolic", "unit": "mmHg",  "ref_range": "60-90"},
    "CNBP/BPVI":     {"test_name": "bp_mean",    "label": "Mean Arterial Pressure",   "unit": "mmHg"},
    "Art/SYS":       {"test_name": "art_sys",    "label": "Arterial Pressure Systolic","unit": "mmHg"},
    "Art/DIA":       {"test_name": "art_dia",    "label": "Arterial Pressure Diastolic","unit":"mmHg"},
    "Art/MAP":       {"test_name": "art_map",    "label": "Arterial Mean Pressure",   "unit": "mmHg"},
}

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def get_local_ip():
    """Deteksi IP lokal secara dinamis."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_value(val):
    if val is None:
        return False
    return str(val).strip() not in ("-?-", "", "N/A", "null", "?", "--")

def parse_datetime(dt_str):
    dt_str = dt_str.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return dt_str

def csv_to_json(csv_filepath, skip_invalid=True):
    with open(csv_filepath, newline="", encoding="latin-1") as f:
        all_rows = list(csv.reader(f))

    if len(all_rows) < 4:
        raise ValueError("File CSV tidak cukup baris (minimal 4 baris: header, unit, label, data).")

    headers   = all_rows[0]
    units_row = all_rows[1]
    data_rows = all_rows[3:]  # baris 0=header, 1=unit, 2=label/type, 3+=data

    units_dict = {
        h.strip(): units_row[i].strip()
        for i, h in enumerate(headers)
        if h.strip() and i < len(units_row)
    }

    results = []
    for row in data_rows:
        if not row or not row[0].strip():
            continue
        timestamp = parse_datetime(row[0])
        vitals = []

        for col_name, config in COLUMN_MAP.items():
            col_idx = next((i for i, h in enumerate(headers) if h.strip() == col_name), None)
            if col_idx is None or col_idx >= len(row):
                continue

            raw_value = row[col_idx].strip()
            if skip_invalid and not is_valid_value(raw_value):
                continue

            unit = units_dict.get(col_name, "")
            if not unit or not unit.isascii():
                unit = config["unit"]

            entry = {
                "test_name": config["test_name"],
                "label":     config["label"],
                "value":     raw_value if is_valid_value(raw_value) else None,
                "unit":      unit,
                "date_time": timestamp,
                "equipid":   config.get("equipid", DEVICE_ID),
            }
            if "ref_range" in config:
                entry["ref_range"] = config["ref_range"]
            vitals.append(entry)

        if vitals:
            results.append({"patient": PATIENT_INFO, "result": {"data_vital_sign": vitals}})

    return results[0] if len(results) == 1 else results

# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/info")
def api_info():
    return jsonify({"ip": get_local_ip(), "port": PORT})

@app.route("/api/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang dikirim."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nama file kosong."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Hanya file .csv yang diizinkan."}), 400

    filename  = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        result = csv_to_json(save_path)
        # Simpan hasil ke folder results
        out_name = os.path.splitext(filename)[0] + ".json"
        out_path = os.path.join(RESULT_FOLDER, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        record_count = len(result) if isinstance(result, list) else 1
        return jsonify({
            "success": True,
            "filename": out_name,
            "records": record_count,
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download/<filename>")
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
PORT = 5000

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 55)
    print("  🚀  CSV → JSON Converter  |  Server Running")
    print("=" * 55)
    print(f"  Local   : http://127.0.0.1:{PORT}")
    print(f"  Network : http://{local_ip}:{PORT}")
    print("=" * 55)
    print("  Tekan Ctrl+C untuk menghentikan server.")
    print()

    # Buka browser otomatis setelah 1 detik
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    app.run(host="0.0.0.0", port=PORT, debug=False)
