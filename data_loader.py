# data_loader.py
"""
Data Loader for CSV-based Timetable Dataset
Works with: Courses.csv, Instructor.csv, Rooms.csv, TimeSlots.csv, Sections.csv
"""

import pandas as pd


def load_data():
    """
    Load all CSV data files
    Returns a dictionary with 5 dataframes: courses, instructors, rooms, timeslots, sections
    """
    print("="*80)
    print("LOADING DATA FROM CSV FILES")
    print("="*80)
    
    data = {}
    
    try:
        # Load Courses
        data['courses'] = pd.read_csv('Courses.csv')
        print(f"✅ Courses.csv: {len(data['courses'])} records loaded")
        
        # Load Instructors
        data['instructors'] = pd.read_csv('Instructor.csv')
        print(f"✅ Instructor.csv: {len(data['instructors'])} records loaded")
        
        # Load Rooms
        data['rooms'] = pd.read_csv('Rooms.csv')
        print(f"✅ Rooms.csv: {len(data['rooms'])} records loaded")
        
        # Load TimeSlots
        data['timeslots'] = pd.read_csv('TimeSlots.csv')
        print(f"✅ TimeSlots.csv: {len(data['timeslots'])} records loaded")
        
        # Load Sections
        data['sections'] = pd.read_csv('Sections.csv')
        print(f"✅ Sections.csv: {len(data['sections'])} records loaded")
        
        # Normalize column names (strip whitespace)
        for key, df in data.items():
            df.columns = df.columns.str.strip()
            data[key] = df
        
        print(f"\n📊 All data loaded successfully!\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure these CSV files are in the same directory:")
        print("  - Courses.csv")
        print("  - Instructor.csv")
        print("  - Rooms.csv")
        print("  - TimeSlots.csv")
        print("  - Sections.csv\n")
        raise
    
    return data


def generate_section_room_compatibility_report(data):
    """
    Check which rooms can host each section based on capacity
    """
    rooms = data['rooms']
    sections = data['sections']
    
    print("="*80)
    print("SECTION-ROOM COMPATIBILITY REPORT")
    print("="*80)
    
    report_rows = []
    
    for _, section in sections.iterrows():
        section_id = section['SectionID']
        student_count = int(section['StudentCount'])
        
        # Find rooms with sufficient capacity
        valid_rooms = rooms[rooms['Capacity'] >= student_count]
        
        if valid_rooms.empty:
            print(f"⚠️  {section_id} (Students: {student_count}) - No suitable rooms found")
            report_rows.append({
                'Section_ID': section_id,
                'Student_Count': student_count,
                'Available_Rooms': 'None',
                'Room_Count': 0
            })
        else:
            room_list = ", ".join(valid_rooms['RoomID'].astype(str).tolist())
            print(f"✅ {section_id} (Students: {student_count}) - {len(valid_rooms)} suitable rooms")
            report_rows.append({
                'Section_ID': section_id,
                'Student_Count': student_count,
                'Available_Rooms': room_list[:50] + '...' if len(room_list) > 50 else room_list,
                'Room_Count': len(valid_rooms)
            })
    
    report_df = pd.DataFrame(report_rows)
    
    print(f"\n📊 Summary:")
    print(f"   Total Sections: {len(sections)}")
    print(f"   Sections with No Valid Rooms: {len(report_df[report_df['Available_Rooms'] == 'None'])}")
    print(f"   Sections with Valid Rooms: {len(report_df[report_df['Available_Rooms'] != 'None'])}\n")
    
    return report_df


def generate_room_type_summary(data):
    """
    Compare number of courses by type vs available room types
    """
    courses = data['courses']
    rooms = data['rooms']
    
    print("="*80)
    print("ROOM TYPE vs COURSE TYPE SUMMARY")
    print("="*80)
    
    # Count courses by type
    lecture_courses = courses[courses['Type'].str.lower().str.contains('lecture', na=False)]
    lab_courses = courses[courses['Type'].str.lower().str.contains('lab', na=False)]
    
    # Count rooms by type
    lecture_rooms = rooms[rooms['Type'].str.lower().str.contains('lecture', na=False)]
    lab_rooms = rooms[rooms['Type'].str.lower().str.contains('lab', na=False)]
    
    print(f"\n📚 Courses:")
    print(f"   Lecture Courses: {len(lecture_courses)}")
    print(f"   Lab Courses: {len(lab_courses)}")
    print(f"   Total Courses: {len(courses)}")
    
    print(f"\n🏫 Rooms:")
    print(f"   Lecture Rooms: {len(lecture_rooms)}")
    print(f"   Lab Rooms: {len(lab_rooms)}")
    print(f"   Total Rooms: {len(rooms)}")
    
    print(f"\n🔍 Analysis:")
    
    # Check for potential issues
    if len(lab_rooms) == 0 and len(lab_courses) > 0:
        print(f"   ⚠️  WARNING: No lab rooms found, but {len(lab_courses)} lab courses exist!")
    elif len(lab_courses) > len(lab_rooms) * 3:
        print(f"   ⚠️  WARNING: Many lab courses ({len(lab_courses)}) vs few lab rooms ({len(lab_rooms)})")
    else:
        print(f"   ✅ Lab room capacity appears adequate")
    
    if len(lecture_rooms) == 0:
        print(f"   ⚠️  WARNING: No lecture rooms found!")
    else:
        print(f"   ✅ {len(lecture_rooms)} lecture rooms available")
    
    print()


def generate_instructor_qualification_report(data):
    """
    Check instructor qualifications and course coverage
    """
    instructors = data['instructors']
    courses = data['courses']
    
    print("="*80)
    print("INSTRUCTOR QUALIFICATION REPORT")
    print("="*80)
    
    total_qualifications = 0
    courses_covered = set()
    
    for _, instructor in instructors.iterrows():
        instructor_name = instructor['Name']
        qualified_str = str(instructor['QualifiedCourses'])
        qualified_courses = [c.strip() for c in qualified_str.split(',') if c.strip()]
        total_qualifications += len(qualified_courses)
        courses_covered.update(qualified_courses)
        
        print(f"👤 {instructor_name:30s} | Qualified for {len(qualified_courses):2d} courses")
    
    all_courses = set(courses['CourseID'].tolist())
    uncovered_courses = all_courses - courses_covered
    
    print(f"\n📊 Summary:")
    print(f"   Total Instructors: {len(instructors)}")
    print(f"   Total Qualifications: {total_qualifications}")
    print(f"   Average Qualifications per Instructor: {total_qualifications / len(instructors):.1f}")
    print(f"   Courses Covered: {len(courses_covered)}/{len(all_courses)}")
    
    if uncovered_courses:
        print(f"\n   ⚠️  Courses with NO qualified instructors:")
        for course in sorted(uncovered_courses):
            print(f"      - {course}")
    else:
        print(f"\n   ✅ All courses have at least one qualified instructor!")
    
    print()


def generate_timeslot_summary(data):
    """
    Display timeslot information
    """
    timeslots = data['timeslots']
    
    print("="*80)
    print("TIMESLOT SUMMARY")
    print("="*80)
    
    days = timeslots['Day'].unique()
    
    print(f"\n📅 Available Days: {len(days)}")
    for day in days:
        day_slots = timeslots[timeslots['Day'] == day]
        print(f"   {day}: {len(day_slots)} time slots")
    
    print(f"\n🕒 Total Time Slots: {len(timeslots)}")
    print(f"\n📋 Sample Time Slots:")
    print(timeslots.head(10).to_string(index=False))
    print()


def display_dataset_overview(data):
    """
    Display comprehensive overview of all datasets
    """
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "DATASET OVERVIEW" + " "*37 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    print("="*80)
    print("DETAILED DATA PREVIEW")
    print("="*80)
    
    for name, df in data.items():
        print(f"\n📄 {name.upper()}")
        print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   Sample Data (first 3 rows):")
        print(df.head(3).to_string(index=False))
        print("-" * 80)


# Main execution
if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "DATA LOADER TEST" + " "*37 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    try:
        # Load data
        data = load_data()
        
        # Display overview
        display_dataset_overview(data)
        
        # Generate reports
        print("\n")
        section_room_report = generate_section_room_compatibility_report(data)
        
        generate_room_type_summary(data)
        
        generate_instructor_qualification_report(data)
        
        generate_timeslot_summary(data)
        
        # Save reports
        section_room_report.to_csv('section_room_compatibility.csv', index=False)
        print("="*80)
        print("💾 Section-Room compatibility report saved to: section_room_compatibility.csv")
        print("="*80)
        
        print("\n✅ Data loading and validation complete!\n")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}\n")
        import traceback
        traceback.print_exc()
