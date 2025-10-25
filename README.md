# University Timetable Generator
An intelligent and modular timetable management system that automates university schedule generation using a Constraint Satisfaction Problem (CSP) solver. It provides both professional-quality PDF reports and an interactive GUI viewer for visualization.
This project integrates four main components: data loading, constraint solving, report generation, and interactive visualization.

# Overview
The system automatically generates conflict-free university timetables given data about courses, instructors, rooms, sections, and time slots.
It ensures:
* No instructor, room, or section overlaps
* Room capacity checks
* Instructor qualification validation
* Visual reports and analytics

The result can be viewed either as:
* A multi-page PDF report (timetable_output.pdf)
*An interactive Tkinter GUI (gui.py window)
* Or as a raw CSV file (generated_timetable.csv)

# Features
* Constraint Satisfaction Problem (CSP) solver for conflict-free scheduling
* Visual & interactive timetable viewer built with Tkinter
* PDF report generator using ReportLab with modern design
* Automated data validation and room-compatibility analysis
* Modular architecture for easy customization and maintenance
* Color-coded timetable presentation for clarity

# Folder & File Structure
File	Description
 * data_loader.py	-> Loads core CSV datasets (Courses.csv, Instructor.csv, Rooms.csv, TimeSlots.csv, Sections.csv). Verifies data integrity and generates statistical & compatibility reports.
 * csp_solver.py -> Implements a CSP-based scheduling engine. Defines variables, domains, and constraints (no room/instructor/section conflicts). Uses backtracking with heuristics for optimization and outputs generated_timetable.csv.
 * generator.py	-> Uses ReportLab to generate a professional-grade PDF file summarizing all schedules. Produces pages by Section, by Day, and by Instructor, with color-coded tables and summary statistics.
 * gui.py	-> Interactive Tkinter GUI for timetable exploration. Displays multi-tab pages (Summary, Sections, Master Grid, Instructors) using the generated CSV. Provides intuitive filtering and modern layout design.
 * generated_timetable.csv	-> Output schedule with assigned rooms, instructors, days, and times. Serves as input for both the PDF generator and GUI viewer.
 * Courses.csv, Instructor.csv, Rooms.csv, Sections.csv, TimeSlots.csv	Core data inputs for generating the timetable.
# How It Works
1- Prepare Input Data
Place the following files in the project root (CSV format):
  * Courses.csv
  * Instructor.csv
  * Rooms.csv
  * Sections.csv
  * TimeSlots.csv

# Step 1: Load Data
  bash
  python data_loader.py
  Loads and validates all CSVs, printing reports about room capacity, instructor qualifications, and schedule feasibility.

# Step 2: Generate Timetable (CSP Solver)
  bash
  python csp_solver.py
Runs the CSP algorithm to produce generated_timetable.csv.
Conflicts are automatically avoided based on defined constraints.

# Step 3: Generate PDF Report

  bash
  python generator.py
Reads the generated CSV to create a professional multi-page PDF (timetable_output.pdf) with summary statistics, visual tables, and color-coded activities.

# Step 4: Launch the Interactive GUI
  bash
  python gui.py
Opens a modern interactive viewer allowing navigation by summary, section, instructor, or master timetable grid.

# Technical Highlights
* Constraint Solver:
  Uses backtracking with MRV (Minimum Remaining Values) heuristic for efficient search. Constraints ensure that:
    * No two sections overlap in the same timeslot.
    * Instructors are only assigned to qualified courses.
    * Rooms match capacity and type requirements.

# PDF Generator:
Uses ReportLab to produce structured and styled tables, with sections organized by day and instructor summaries.

# GUI Viewer:
Built using Tkinter and pandas; enables multi-tab navigation and automatic summary statistics generation.

# Requirements
Before running the system, install dependencies:

  bash
  pip install pandas reportlab
(Optionally, for GUI support, ensure Tkinter is installed — usually included with Python distributions.)

Example Workflow
bash
# Load and verify data
python data_loader.py

# Generate a conflict-free timetable
python csp_solver.py

# Create a PDF report
python generator.py

# View interactively
python gui.py
Output files:

generated_timetable.csv

timetable_output.pdf

License
Open-source project for educational and institutional use.
All components can be extended or integrated with external scheduling systems or databases.

Contributors
Developed as a modular academic scheduling solution integrating:

ReportLab for document generation

Tkinter for interactive visualization

Pandas for data processing

Algorithmic CSPs for intelligent timetable creation
