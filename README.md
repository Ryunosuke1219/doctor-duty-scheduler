# Doctor Duty Scheduler

A lightweight Streamlit web app that automatically assigns duty and on‑call shifts for doctors from a simple CSV of availability.

---

## 🚀 Live Demo

▶ **[https://doctor-duty-scheduler-ms2fup9dultfhpjn9jzzk9.streamlit.app/](https://doctor-duty-scheduler-ms2fup9dultfhpjn9jzzk9.streamlit.app/)**

Upload your `*.csv` availability file (0 = can work, 1 = NG) and instantly download the calculated schedule as Excel.

---

## Features

| Feature                      | Details                                                                                                                                                                                                                                                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📄 **CSV Upload**            | Accepts a matrix with `Group`, `Name`, and day‑columns like `1-1(Sun)`, `1-2(Sun)`, `2(Mon)`…                                                                                                                                                                                                                                               |
| 🤖 **Auto‑assignment**       | *Group 1* doctors get exactly **2 duty shifts** each.<br>*Group 0* doctors get **1‑2 duty shifts**.<br>  – Holiday **‑1** columns demand both a Group 0 and Group 1 doctor.<br>  – If duty is Group 1 on a single‑shift day, a Group 0 doctor is auto‑assigned on‑call.<br>  – Minimum 4‑day interval between any duty/on‑call assignments. |
| 📥 **Excel Export**          | One‑click download of an `.xlsx` with two sheets: `Schedule` & `Summary`.                                                                                                                                                                                                                                                                   |
| 🌐 **Streamlit Cloud‑ready** | Deployed on the free Community tier; no server management needed.                                                                                                                                                                                                                                                                           |

---

## Getting Started Locally

```bash
# 1. Clone the repo
$ git clone https://github.com/your‑username/doctor-duty-scheduler-app.git
$ cd doctor-duty-scheduler-app

# 2. Install dependencies
$ pip install -r requirements.txt

# 3. Run locally
$ streamlit run app.py
```

Navigate to [http://localhost:8501](http://localhost:8501), upload your CSV, and download the schedule.

---

## CSV Format

```
Group,Name,1-1(Sun),1-2(Sun),2(Mon),3(Tue),...
0,山田太郎,0,1,0,0,...
1,佐藤花子,1,1,0,0,...
...
```

* **Group**: `0` = duty only, `1` = duty + on‑call capability
* **0** = *can work*, **1** = *cannot work/NG*

---

## Folder Structure

```
├── app.py               # Streamlit application
├── requirements.txt     # Python deps (pandas, streamlit, openpyxl)
└── .streamlit/
    └── config.toml      # (optional) theme tuning
```

---

## Customising Rules

Most parameters live near the top of **`app.py`**:

```python
SPACE = 4              # minimum days between shifts
# Duty distribution logic is in build_schedule()
```

Change the logic, commit, and Streamlit Cloud auto‑deploys the update.

---

## License

MIT © 2025 Ryunosuke Noda
