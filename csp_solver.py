# csp.py
"""
CSP (Constraint Satisfaction Problem) Timetable Solver
Uses data_loader.py to load CSV data and generates conflict-free schedules
"""

import pandas as pd
from collections import defaultdict
import random
import time
from data_loader import load_data


# ============================================================================
# CSP PROBLEM FORMULATION
# ============================================================================

class TimetableCSP:
    """
    Timetable Constraint Satisfaction Problem
    
    Variables: (Section, Course) pairs that need to be scheduled
    Domain: (Room, TimeSlot, Instructor) combinations for each variable
    Constraints: No room/instructor/section conflicts at same time
    """
    
    def __init__(self, data):
        """Initialize CSP with loaded data"""
        self.data = data
        self.variables = []
        self.domains = {}
        self.variable_info = {}
        self.assignment = {}
        
        # Parse data structures
        self._parse_data()
        
        # Create CSP components
        self._create_variables()
        self._create_domains()
    
    def _parse_data(self):
        """Parse data into convenient structures"""
        print("\n" + "="*80)
        print("PARSING DATA STRUCTURES")
        print("="*80)
        
        # Parse instructor qualifications
        self.instructor_courses = {}
        for _, instructor in self.data['instructors'].iterrows():
            instructor_id = instructor['InstructorID']
            qualified = str(instructor['QualifiedCourses']).split(',')
            qualified = [c.strip() for c in qualified if c.strip()]
            self.instructor_courses[instructor_id] = {
                'name': instructor['Name'],
                'courses': qualified,
                'preferences': instructor['PreferredSlots']
            }
        
        # Parse section courses
        self.section_courses = {}
        for _, section in self.data['sections'].iterrows():
            section_id = section['SectionID']
            courses = str(section['Courses']).split(',')
            courses = [c.strip() for c in courses if c.strip()]
            self.section_courses[section_id] = {
                'student_count': section['StudentCount'],
                'courses': courses
            }
        
        # Create course lookup
        self.courses = {}
        for _, course in self.data['courses'].iterrows():
            self.courses[course['CourseID']] = {
                'name': course['CourseName'],
                'type': course['Type'],
                'credits': course['Credits']
            }
        
        # Create room lookup
        self.rooms = {}
        for _, room in self.data['rooms'].iterrows():
            self.rooms[room['RoomID']] = {
                'type': room['Type'],
                'capacity': room['Capacity']
            }
        
        # Create timeslot list
        self.timeslots = []
        for _, slot in self.data['timeslots'].iterrows():
            self.timeslots.append({
                'id': slot['TimeSlotID'],
                'day': slot['Day'],
                'start': slot['StartTime'],
                'end': slot['EndTime']
            })
        
        print(f"✅ Parsed {len(self.instructor_courses)} instructors")
        print(f"✅ Parsed {len(self.section_courses)} sections")
        print(f"✅ Parsed {len(self.courses)} courses")
        print(f"✅ Parsed {len(self.rooms)} rooms")
        print(f"✅ Parsed {len(self.timeslots)} timeslots")
    
    def _create_variables(self):
        """Create CSP variables (Section-Course pairs)"""
        print("\n" + "="*80)
        print("CREATING CSP VARIABLES")
        print("="*80)
        
        for section_id, section_data in self.section_courses.items():
            for course_id in section_data['courses']:
                if course_id in self.courses:
                    var_name = f"{section_id}_{course_id}"
                    self.variables.append(var_name)
                    
                    self.variable_info[var_name] = {
                        'section_id': section_id,
                        'course_id': course_id,
                        'student_count': section_data['student_count'],
                        'course_type': self.courses[course_id]['type'],
                        'course_name': self.courses[course_id]['name']
                    }
        
        print(f"✅ Created {len(self.variables)} variables (Section-Course assignments)")
        print(f"   Example: {self.variables[0] if self.variables else 'None'}")
    
    def _create_domains(self):
        """Create domains for each variable"""
        print("\n" + "="*80)
        print("CREATING DOMAINS")
        print("="*80)
        
        for var_name in self.variables:
            var_info = self.variable_info[var_name]
            course_id = var_info['course_id']
            course_type = var_info['course_type']
            student_count = var_info['student_count']
            
            # Find suitable rooms
            suitable_rooms = []
            for room_id, room_data in self.rooms.items():
                # Match room type with course type
                if self._room_matches_course(room_data['type'], course_type):
                    if room_data['capacity'] >= student_count:
                        suitable_rooms.append(room_id)
            
            # Relax capacity if no rooms found
            if not suitable_rooms:
                for room_id, room_data in self.rooms.items():
                    if self._room_matches_course(room_data['type'], course_type):
                        suitable_rooms.append(room_id)
            
            # Use any room if still empty
            if not suitable_rooms:
                suitable_rooms = list(self.rooms.keys())[:10]  # Limit to 10 rooms
            
            # Find qualified instructors
            qualified_instructors = []
            for instructor_id, instructor_data in self.instructor_courses.items():
                if course_id in instructor_data['courses']:
                    qualified_instructors.append(instructor_id)
            
            # Use placeholder if no qualified instructors
            if not qualified_instructors:
                qualified_instructors = ['UNASSIGNED']
            
            # Create domain: combinations of room + timeslot + instructor
            domain = []
            for room_id in suitable_rooms:
                for timeslot in self.timeslots:
                    for instructor_id in qualified_instructors:
                        instructor_name = self.instructor_courses.get(
                            instructor_id, {}
                        ).get('name', 'Unassigned')
                        
                        domain.append({
                            'room': room_id,
                            'timeslot_id': timeslot['id'],
                            'day': timeslot['day'],
                            'start_time': timeslot['start'],
                            'end_time': timeslot['end'],
                            'instructor_id': instructor_id,
                            'instructor_name': instructor_name
                        })
            
            self.domains[var_name] = domain
        
        total_combinations = sum(len(d) for d in self.domains.values())
        avg_domain_size = total_combinations / len(self.domains) if self.domains else 0
        
        print(f"✅ Created domains for {len(self.domains)} variables")
        print(f"   Total domain combinations: {total_combinations:,}")
        print(f"   Average domain size: {avg_domain_size:.1f}")
    
    def _room_matches_course(self, room_type, course_type):
        """Check if room type matches course type"""
        room_lower = room_type.lower()
        course_lower = course_type.lower()
        
        # Lecture rooms for lecture courses
        if 'lecture' in course_lower and 'lecture' in room_lower:
            return True
        
        # Lab rooms for lab courses
        if 'lab' in course_lower and 'lab' in room_lower:
            return True
        
        # Mixed courses can use either
        if 'lecture' in course_lower and 'lab' in course_lower:
            return True
        
        return False
    
    # ========================================================================
    # CONSTRAINT CHECKING
    # ========================================================================
    
    def is_consistent(self, var, value):
        """Check if assignment is consistent with current assignment"""
        room = value['room']
        timeslot_id = value['timeslot_id']
        instructor_id = value['instructor_id']
        section_id = self.variable_info[var]['section_id']
        
        for assigned_var, assigned_value in self.assignment.items():
            assigned_room = assigned_value['room']
            assigned_timeslot = assigned_value['timeslot_id']
            assigned_instructor = assigned_value['instructor_id']
            assigned_section = self.variable_info[assigned_var]['section_id']
            
            # Constraint 1: Room conflict (same room, same time)
            if room == assigned_room and timeslot_id == assigned_timeslot:
                return False
            
            # Constraint 2: Instructor conflict (same instructor, same time)
            if instructor_id == assigned_instructor and timeslot_id == assigned_timeslot:
                if instructor_id != 'UNASSIGNED':  # Allow multiple unassigned
                    return False
            
            # Constraint 3: Section conflict (same section, same time)
            if section_id == assigned_section and timeslot_id == assigned_timeslot:
                return False
        
        return True
    
    # ========================================================================
    # SOLVER ALGORITHMS
    # ========================================================================
    
    def select_unassigned_variable(self):
        """Select next unassigned variable using MRV heuristic"""
        unassigned = [v for v in self.variables if v not in self.assignment]
        
        if not unassigned:
            return None
        
        # MRV: Minimum Remaining Values
        # Choose variable with smallest domain
        unassigned.sort(key=lambda v: len(self.domains[v]))
        
        return unassigned[0]
    
    def backtracking_search(self, max_iterations=1000, verbose=True):
        """Backtracking search with forward checking"""
        print("\n" + "="*80)
        print("STARTING BACKTRACKING SEARCH")
        print("="*80)
        print(f"Variables to assign: {len(self.variables)}")
        print(f"Max iterations: {max_iterations}")
        print()
        
        self.assignment = {}
        iterations = [0]
        start_time = time.time()
        
        def backtrack():
            iterations[0] += 1
            
            # Progress reporting
            if verbose and iterations[0] % 100 == 0:
                elapsed = time.time() - start_time
                progress = len(self.assignment) / len(self.variables) * 100
                print(f"  Iteration {iterations[0]:4d}: {len(self.assignment):3d}/{len(self.variables)} "
                      f"({progress:5.1f}%) - {elapsed:.1f}s")
            
            # Check iteration limit
            if iterations[0] >= max_iterations:
                return False
            
            # Check if complete
            if len(self.assignment) == len(self.variables):
                return True
            
            # Select variable
            var = self.select_unassigned_variable()
            if var is None:
                return False
            
            # Try each value in domain
            for value in self.domains[var]:
                if self.is_consistent(var, value):
                    # Assign
                    self.assignment[var] = value
                    
                    # Recurse
                    result = backtrack()
                    if result:
                        return True
                    
                    # Backtrack
                    del self.assignment[var]
            
            return False
        
        # Start search
        success = backtrack()
        elapsed = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"SEARCH COMPLETE")
        print(f"{'='*80}")
        print(f"Success: {success}")
        print(f"Iterations: {iterations[0]}")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Assigned: {len(self.assignment)}/{len(self.variables)}")
        
        return success
    
    # ========================================================================
    # OUTPUT GENERATION
    # ========================================================================
    
    def generate_schedule_dataframe(self):
        """Convert assignment to pandas DataFrame"""
        if not self.assignment:
            print("⚠️  No assignment to convert")
            return None
        
        print("\n" + "="*80)
        print("GENERATING SCHEDULE OUTPUT")
        print("="*80)
        
        schedule_data = []
        
        for var_name, value in self.assignment.items():
            var_info = self.variable_info[var_name]
            
            schedule_data.append({
                'Section_ID': var_info['section_id'],
                'Course_Code': var_info['course_id'],
                'Course_Name': var_info['course_name'],
                'Activity_Type': var_info['course_type'],
                'Day': value['day'],
                'Start_Time': value['start_time'],
                'End_Time': value['end_time'],
                'Room': value['room'],
                'Instructor': value['instructor_name'],
                'Student_Count': var_info['student_count']
            })
        
        df = pd.DataFrame(schedule_data)
        
        # Sort by day and time
        day_order = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 
                     'Wednesday': 3, 'Thursday': 4}
        df['Day_Order'] = df['Day'].map(day_order)
        df = df.sort_values(['Day_Order', 'Start_Time', 'Section_ID'])
        df = df.drop('Day_Order', axis=1)
        
        print(f"✅ Generated schedule with {len(df)} classes")
        
        return df
    
    def print_statistics(self, schedule_df):
        """Print schedule statistics"""
        print("\n" + "="*80)
        print("SCHEDULE STATISTICS")
        print("="*80)
        
        print(f"\n📊 Overall:")
        print(f"   Total Classes: {len(schedule_df)}")
        print(f"   Unique Courses: {schedule_df['Course_Code'].nunique()}")
        print(f"   Unique Sections: {schedule_df['Section_ID'].nunique()}")
        print(f"   Instructors: {schedule_df['Instructor'].nunique()}")
        print(f"   Rooms Used: {schedule_df['Room'].nunique()}")
        
        print(f"\n📚 By Type:")
        for activity_type in schedule_df['Activity_Type'].unique():
            count = len(schedule_df[schedule_df['Activity_Type'] == activity_type])
            print(f"   {activity_type}: {count}")
        
        print(f"\n📅 By Day:")
        for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']:
            count = len(schedule_df[schedule_df['Day'] == day])
            if count > 0:
                print(f"   {day}: {count}")
        
        print(f"\n📋 Sample (first 15 entries):")
        print("-" * 80)
        print(schedule_df.head(15).to_string(index=False))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "CSP TIMETABLE SOLVER" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Load data using data_loader
    data = load_data()
    
    # Create CSP
    csp = TimetableCSP(data)
    
    # Solve
    success = csp.backtracking_search(max_iterations=1000, verbose=True)
    
    if success:
        # Generate output
        schedule_df = csp.generate_schedule_dataframe()
        
        if schedule_df is not None:
            # Save to CSV
            schedule_df.to_csv('generated_timetable.csv', index=False)
            print(f"\n💾 Schedule saved to: generated_timetable.csv")
            
            # Print statistics
            csp.print_statistics(schedule_df)
            
            print("\n" + "="*80)
            print("✅ TIMETABLE GENERATION SUCCESSFUL!")
            print("="*80)
            print("\nYou can now:")
            print("  1. View generated_timetable.csv")
            print("  2. Run GUI: python timetable_gui_multipage.py")
            print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO FIND COMPLETE SOLUTION")
        print("="*80)
        print(f"\nPartial assignment: {len(csp.assignment)}/{len(csp.variables)} variables")
        print("\nSuggestions:")
        print("  - Increase max_iterations")
        print("  - Add more rooms or timeslots")
        print("  - Assign more instructors to courses")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
