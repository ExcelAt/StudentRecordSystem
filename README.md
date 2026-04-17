# 🎓 Student Records Management System

## 📌 Overview

This project is a **Student Records Management System** developed as a group project. It demonstrates skills in **database design, ETL pipelines, and data visualization** using modern tools.

The system allows users to manage and analyze:

* Student information
* Course enrollments
* Grades and performance
* Attendance records

It also includes a **Streamlit dashboard** for interactive data exploration and reporting.

---

## 🛠️ Technologies Used

* **Python** (Data processing & ETL)
* **PostgreSQL / Azure Database** (Database)
* **SQL** (Queries & data modeling)
* **Streamlit** (Frontend dashboard)
* **Pandas & NumPy** (Data manipulation)

---

## 📁 Project Structure

```
StudentRecordSystem/
│
├── .venv/                     # Virtual environment
├── .env                      # Environment variables (DB credentials, etc.)
├── .gitignore                # Git ignore file
│
├── app/                      # Core application logic
├── docs/                     # Project documentation
├── sql/                      # SQL scripts and queries
├── SR_DatabaseSetup/         # Database setup resources
│
├── streamlit_app/            # Streamlit frontend application
│   ├── components/           # Reusable UI components
│   ├── pages/                # Application pages
│   │   ├── 02_dashboard.py   # Dashboard view
│   │   ├── 03_students.py    # Student management
│   │   ├── 04_courses.py     # Course management
│   │   ├── 05_grades.py      # Grades tracking
│   │   ├── 06_attendance.py  # Attendance tracking
│   │   └── 07_reports.py     # Reports and analytics
│   │
│   ├── styles/               # Custom styling
│   │   └── main.css
│   │
│   ├── utils/                # Helper functions
│   └── main.py               # Streamlit app entry point
│
├── student_dataset/          # Sample or raw data
│
├── create_database.py        # Script to create database
├── create_tables.py          # Script to create tables
├── create_user_accounts.py   # Script to create users
├── create_users_table.py     # Script to create users table
│
├── etl_pipeline.py           # ETL pipeline script
├── load_data.py              # Data loading script
├── etl_pipeline.log          # ETL logs
│
├── tests.py                  # Test scripts
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd StudentRecordSystem
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and add:

```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
DB_SSLMODE=require
```

---

## 🗄️ Database Setup

Run the following scripts in order:

```bash
python create_database.py
python create_tables.py
python create_users_table.py
python create_user_accounts.py
```

---

## 🔄 Running the ETL Pipeline

```bash
python etl_pipeline.py
```

This will:

* Extract data from source files
* Transform data into required format
* Load data into the database

---

## 📊 Running the Streamlit App

```bash
cd streamlit_app
streamlit run main.py
```

Then open the provided local URL in your browser.

---

## ✨ Features

* Manage student records
* Track course enrollments
* Monitor grades and performance
* Record attendance
* Generate reports and dashboards
* Interactive UI with Streamlit

---

## 🧪 Testing

Run tests using:

```bash
python tests.py
```

---

## 👥 Project Type

* **Format:** Group Project
* **Focus Areas:** Database Design, ETL, Data Analytics, Dashboarding

---

## 📌 Notes

* Ensure your database connection is correct before running scripts
* Keep your `.env` file secure and do not commit it to GitHub

---

## 📄 License

This project is for educational purposes.

---

## 🙌 Acknowledgements

Developed as part of a learning program to build practical skills in **data engineering and analytics**.
