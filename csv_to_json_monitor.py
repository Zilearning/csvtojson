import csv
import json
import sys
from datetime import datetime

PATIENT_INFO = {
    "pid": "ANON123456",
    "vid": "",
    "name": "ANON PATIENT",
    "gender": "male"
}

DEVICE_ID = "ANONDEVICE001"

COLUMN_MAP = {
    "ECG/HR": {"test_name": "hr", "label": "Heart Rate (ECG)", "unit": "bpm", "ref_range": "60-100"},
    "ECG/PVCs": {"test_name": "ecg_pvcs", "label": "PVCs", "unit": "/min"},
    "ECG/PAUSE_MIN": {"test_name": "ecg_pause", "label": "ECG Pause Min", "unit": "/min"},
    "SpO2_A/SpO2": {"test_name": "spo2_a", "label": "Oxygen Saturation (A)", "unit": "%", "ref_range": "95-100"},
    "SpO2_B/SpO2": {"test_name": "spo2_b", "label": "Oxygen Saturation (B)", "unit": "%", "ref_range": "95-100"},
    "SpO2_B/SpO2Delta": {"test_name": "spo2_delta", "label": "SpO2 Delta", "unit": "%"},
    "PR/PR": {"test_name": "pr", "label": "Pulse Rate", "unit": "bpm", "ref_range": "60-100"},
    "RR/RR": {"test_name": "rr", "label": "Respiratory Rate", "unit": "rpm", "ref_range": "12-20"},
    "TEMP/T1": {"test_name": "temp_t1", "label": "Body Temperature T1", "unit": "°C", "ref_range": "36.0-37.5", "equipid": "ANONDEVICE002"},
    "TEMP/T2": {"test_name": "temp_t2", "label": "Body Temperature T2", "unit": "°C", "ref_range": "36.0-37.5", "equipid": "ANONDEVICE002"},
    "TEMP/TD": {"test_name": "temp_td", "label": "Temperature Difference", "unit": "°C", "equipid": "ANONDEVICE002"},
    "CNBP/SYS": {"test_name": "bp_sys", "label": "Blood Pressure Systolic", "unit": "mmHg", "ref_range": "90-140"},
    "CNBP/DIA": {"test_name": "bp_dia", "label": "Blood Pressure Diastolic", "unit": "mmHg", "ref_range": "60-90"},
    "CNBP/BPVI": {"test_name": "bp_mean", "label": "Mean Arterial Pressure", "unit": "mmHg"},
    "Art/SYS": {"test_name": "art_sys", "label": "Arterial Pressure Systolic", "unit": "mmHg"},
    "Art/DIA": {"test_name": "art_dia", "label": "Arterial Pressure Diastolic", "unit": "mmHg"},
    "Art/MAP": {"test_name": "art_map", "label": "Arterial Mean Pressure", "unit": "mmHg"},
}

def is_valid_value(val):
    if val is None: return False
    return str(val).strip() not in ("-?-", "", "N/A", "null", "?", "--")

def parse_datetime(dt_str):
    dt_str = dt_str.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return dt_str

def csv_to_json(csv_filepath, output_filepath=None, skip_invalid=True):
    with open(csv_filepath, newline='', encoding='latin-1') as f:
        all_rows = list(csv.reader(f))

    headers = all_rows[0]
    units_row = all_rows[1]
    data_rows = all_rows[3:]  # skip baris unit & "value"

    units_dict = {h.strip(): units_row[i].strip() for i, h in enumerate(headers) if h.strip() and i < len(units_row)}

    print(f"✅ Kolom ditemukan  : {[h for h in headers if h.strip()]}")
    print(f"📊 Total baris data : {len(data_rows)}\n")

    results = []
    for row in data_rows:
        if not row or not row[0].strip(): continue
        timestamp = parse_datetime(row[0])
        vitals = []

        for col_name, config in COLUMN_MAP.items():
            col_idx = next((i for i, h in enumerate(headers) if h.strip() == col_name), None)
            if col_idx is None or col_idx >= len(row): continue

            raw_value = row[col_idx].strip()
            if skip_invalid and not is_valid_value(raw_value): continue

            unit = units_dict.get(col_name, "")
            if not unit or not unit.isascii(): unit = config["unit"]

            entry = {
                "test_name": config["test_name"],
                "label": config["label"],
                "value": raw_value if is_valid_value(raw_value) else None,
                "unit": unit,
                "date_time": timestamp,
                "equipid": config.get("equipid", DEVICE_ID)
            }
            if "ref_range" in config:
                entry["ref_range"] = config["ref_range"]
            vitals.append(entry)

        if vitals:
            results.append({"patient": PATIENT_INFO, "result": {"data_vital_sign": vitals}})

    print(f"✅ Record valid dihasilkan: {len(results)}")

    output = results[0] if len(results) == 1 else results
    json_str = json.dumps(output, indent=2, ensure_ascii=False)

    if output_filepath:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"💾 JSON disimpan ke : {output_filepath}")
    else:
        print(json_str)

    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python csv_to_json_monitor.py <input.csv> [output.json]")
        sys.exit(1)
    csv_to_json(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)