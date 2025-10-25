# gui.py
"""
Interactive Multi-Page GUI for Timetable Viewing
Works with generated_timetable.csv from the CSP solver
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, font
from datetime import datetime


class ModernTimetableGUI:
    """Multi-page interactive GUI matching the PDF structure"""
    
    # Modern Color Scheme (matching PDF)
    COLORS = {
        'primary': '#2C3E50',           # Dark blue-gray
        'secondary': '#3498DB',         # Bright blue
        'accent': '#E74C3C',            # Coral red
        'success': '#27AE60',           # Green
        'warning': '#F39C12',           # Orange
        'background': '#ECF0F1',        # Light gray
        'header_bg': '#34495E',         # Darker blue-gray
        'cell_bg': '#EBF5FB',           # Light blue
        'border': '#BDC3C7',            # Gray border
        'text_dark': '#2C3E50',         # Dark text
        'text_light': '#FFFFFF',        # White text
        'sidebar': '#2C3E50',           # Sidebar background
        'sidebar_hover': '#34495E',     # Sidebar hover
        'active_page': '#3498DB',       # Active page indicator
    }
    
    # Activity type colors
    ACTIVITY_COLORS = {
        'Lecture': '#3498DB',               # Blue for lectures
        'Lab': '#27AE60',                   # Green for labs
        'Lecture and Lab': '#9B59B6',      # Purple for combined
        'Tutorial': '#F39C12',              # Orange for tutorials
    }
    
    def __init__(self, schedule_df):
        """Initialize GUI with schedule data"""
        self.schedule_df = schedule_df
        self.current_page = "summary"
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("University Timetable - Interactive Viewer")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.COLORS['background'])
        
        # Custom fonts
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.header_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.section_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=10)
        self.small_font = font.Font(family="Helvetica", size=9)
        
        # Setup UI
        self._setup_ui()
        self._show_page("summary")
    
    def _setup_ui(self):
        """Setup the main UI structure"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for navigation
        self._create_sidebar(main_container)
        
        # Right content area
        self.content_frame = tk.Frame(main_container, bg=self.COLORS['background'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = tk.Frame(parent, bg=self.COLORS['sidebar'], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo/Title area
        title_frame = tk.Frame(sidebar, bg=self.COLORS['sidebar'])
        title_frame.pack(fill=tk.X, padx=20, pady=30)
        
        title_label = tk.Label(
            title_frame,
            text="📅 Timetable",
            font=self.header_font,
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_light']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Interactive Viewer",
            font=self.small_font,
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['cell_bg']
        )
        subtitle_label.pack()
        
        # Separator
        separator = tk.Frame(sidebar, bg=self.COLORS['border'], height=2)
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Navigation buttons
        nav_items = [
            ("📊 Summary", "summary", "View schedule statistics"),
            ("📅 By Section", "sections", "Section timetables"),
            ("🗓️ Master Grid", "grid", "All sections overview"),
            ("👨‍🏫 Instructors", "instructors", "Instructor schedules"),
        ]
        
        self.nav_buttons = {}
        
        for label, page_id, tooltip in nav_items:
            btn_frame = tk.Frame(sidebar, bg=self.COLORS['sidebar'])
            btn_frame.pack(fill=tk.X, padx=15, pady=5)
            
            btn = tk.Button(
                btn_frame,
                text=label,
                command=lambda p=page_id: self._show_page(p),
                bg=self.COLORS['sidebar'],
                fg=self.COLORS['text_light'],
                font=self.normal_font,
                relief=tk.FLAT,
                cursor="hand2",
                anchor="w",
                padx=20,
                pady=12
            )
            btn.pack(fill=tk.X)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.COLORS['sidebar_hover']))
            btn.bind("<Leave>", lambda e, b=btn, p=page_id: b.config(
                bg=self.COLORS['active_page'] if self.current_page == p else self.COLORS['sidebar']
            ))
            
            self.nav_buttons[page_id] = btn
        
        # Footer info
        footer_frame = tk.Frame(sidebar, bg=self.COLORS['sidebar'])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        footer_label = tk.Label(
            footer_frame,
            text=f"Generated on\n{datetime.now().strftime('%B %d, %Y\n%I:%M %p')}",
            font=self.small_font,
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['cell_bg'],
            justify=tk.CENTER
        )
        footer_label.pack()
    
    def _update_nav_buttons(self):
        """Update navigation button states"""
        for page_id, btn in self.nav_buttons.items():
            if page_id == self.current_page:
                btn.config(bg=self.COLORS['active_page'])
            else:
                btn.config(bg=self.COLORS['sidebar'])
    
    def _show_page(self, page_id):
        """Show the selected page"""
        self.current_page = page_id
        self._update_nav_buttons()
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show appropriate page
        if page_id == "summary":
            self._show_summary_page()
        elif page_id == "sections":
            self._show_sections_page()
        elif page_id == "grid":
            self._show_grid_page()
        elif page_id == "instructors":
            self._show_instructors_page()
    
    def _show_summary_page(self):
        """Show summary statistics page"""
        # Header
        header = tk.Label(
            self.content_frame,
            text="University Timetable",
            font=self.title_font,
            bg=self.COLORS['background'],
            fg=self.COLORS['primary']
        )
        header.pack(pady=(0, 5))
        
        subtitle = tk.Label(
            self.content_frame,
            text=f"Academic Year 2025-2026 • Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            font=self.normal_font,
            bg=self.COLORS['background'],
            fg=self.COLORS['text_dark']
        )
        subtitle.pack(pady=(0, 30))
        
        # Statistics section
        stats_title = tk.Label(
            self.content_frame,
            text="📊 Schedule Summary",
            font=self.header_font,
            bg=self.COLORS['background'],
            fg=self.COLORS['secondary']
        )
        stats_title.pack(anchor="w", pady=(0, 15))
        
        # Calculate statistics
        total_classes = len(self.schedule_df)
        unique_courses = self.schedule_df['Course_Code'].nunique()
        unique_sections = self.schedule_df['Section_ID'].nunique()
        unique_instructors = self.schedule_df['Instructor'].nunique()
        
        # Count by activity type
        activity_counts = self.schedule_df['Activity_Type'].value_counts()
        
        # Statistics cards
        stats_frame = tk.Frame(self.content_frame, bg=self.COLORS['background'])
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        stats_data = [
            ("Total Classes Scheduled", total_classes, self.COLORS['secondary']),
            ("Unique Courses", unique_courses, self.COLORS['success']),
            ("Unique Sections", unique_sections, self.COLORS['warning']),
            ("Instructors Involved", unique_instructors, self.COLORS['accent']),
        ]
        
        # Add activity type counts
        for activity_type, count in activity_counts.items():
            stats_data.append((f"{activity_type} Sessions", count, self.ACTIVITY_COLORS.get(activity_type, self.COLORS['primary'])))
        
        for i, (label, value, color) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            card = tk.Frame(stats_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            value_label = tk.Label(
                card,
                text=str(value),
                font=font.Font(family="Helvetica", size=36, weight="bold"),
                bg='white',
                fg=color
            )
            value_label.pack(pady=(20, 5))
            
            text_label = tk.Label(
                card,
                text=label,
                font=self.normal_font,
                bg='white',
                fg=self.COLORS['text_dark']
            )
            text_label.pack(pady=(0, 20))
        
        # Configure grid weights
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        for i in range((len(stats_data) + 1) // 2):
            stats_frame.grid_rowconfigure(i, weight=1)
    
    def _show_sections_page(self):
        """Show section timetables page"""
        # Header
        header = tk.Label(
            self.content_frame,
            text="📅 Timetable by Section",
            font=self.header_font,
            bg=self.COLORS['background'],
            fg=self.COLORS['secondary']
        )
        header.pack(anchor="w", pady=(0, 15))
        
        # Create scrollable frame
        canvas = tk.Canvas(self.content_frame, bg=self.COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Get unique sections
        sections = sorted(self.schedule_df['Section_ID'].unique())
        
        for section_id in sections:
            section_data = self.schedule_df[self.schedule_df['Section_ID'] == section_id].copy()
            
            # Section frame
            section_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            section_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Section header
            section_header = tk.Label(
                section_frame,
                text=f"Section {section_id} ({len(section_data)} classes)",
                font=self.section_font,
                bg=self.COLORS['header_bg'],
                fg=self.COLORS['text_light'],
                anchor="w",
                padx=15,
                pady=10
            )
            section_header.pack(fill=tk.X)
            
            # Sort by day and time
            day_order = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4}
            section_data['Day_Order'] = section_data['Day'].map(day_order)
            section_data = section_data.sort_values(['Day_Order', 'Start_Time'])
            
            # Create treeview table
            tree_frame = tk.Frame(section_frame, bg='white')
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            columns = ('Day', 'Time', 'Course', 'Type', 'Instructor', 'Room')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=min(len(section_data), 8))
            
            # Configure columns
            tree.column('Day', width=100, anchor='center')
            tree.column('Time', width=150, anchor='center')
            tree.column('Course', width=200, anchor='center')
            tree.column('Type', width=120, anchor='center')
            tree.column('Instructor', width=200, anchor='center')
            tree.column('Room', width=100, anchor='center')
            
            # Headers
            for col in columns:
                tree.heading(col, text=col)
            
            # Add data
            for _, row in section_data.iterrows():
                time_str = f"{row['Start_Time']} - {row['End_Time']}"
                course_name = row.get('Course_Name', '')
                if course_name:
                    course_str = f"{row['Course_Code']}\n{course_name[:30]}"
                else:
                    course_str = row['Course_Code']
                
                values = (
                    row['Day'],
                    time_str,
                    course_str,
                    row['Activity_Type'],
                    row['Instructor'],
                    row['Room']
                )
                
                tree.insert('', 'end', values=values)
            
            tree.pack(fill=tk.BOTH, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _show_grid_page(self):
        """Show master timetable grid page"""
        # Header
        header = tk.Label(
            self.content_frame,
            text="🗓️ Master Timetable Grid",
            font=self.header_font,
            bg=self.COLORS['background'],
            fg=self.COLORS['secondary']
        )
        header.pack(anchor="w", pady=(0, 15))
        
        # Prepare pivot data
        df = self.schedule_df.copy()
        df['TimeSlot'] = df['Day'] + " " + df['Start_Time'].astype(str)
        df['CellContent'] = df['Course_Code'] + "\n" + df['Activity_Type']
        
        timetable_grid = df.pivot_table(
            index='TimeSlot',
            columns='Section_ID',
            values='CellContent',
            aggfunc='first'
        ).fillna('-')
        
        # Sort rows
        day_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        timetable_grid = timetable_grid.reset_index()
        timetable_grid['Day'] = timetable_grid['TimeSlot'].apply(lambda x: x.split(' ')[0])
        timetable_grid['Day'] = pd.Categorical(timetable_grid['Day'], categories=day_order, ordered=True)
        timetable_grid = timetable_grid.sort_values(['Day', 'TimeSlot']).drop('Day', axis=1).set_index('TimeSlot')
        
        # Sort columns
        sorted_columns = sorted(timetable_grid.columns)
        timetable_grid = timetable_grid[sorted_columns]
        
        # Create frame with scrollbars
        grid_frame = tk.Frame(self.content_frame, bg=self.COLORS['background'])
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ['Time Slot'] + [f'Sec {col}' for col in timetable_grid.columns]
        tree = ttk.Treeview(grid_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        tree.column('Time Slot', width=180, anchor='w')
        for col in columns[1:]:
            tree.column(col, width=120, anchor='center')
        
        # Headers
        for col in columns:
            tree.heading(col, text=col)
        
        # Add data
        for idx, row in timetable_grid.iterrows():
            values = [idx] + list(row)
            tree.insert('', 'end', values=values)
        
        # Scrollbars
        vsb = ttk.Scrollbar(grid_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(grid_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview", rowheight=50, font=self.small_font)
        style.configure("Treeview.Heading", font=self.normal_font)
    
    def _show_instructors_page(self):
        """Show instructor schedules page"""
        # Header
        header = tk.Label(
            self.content_frame,
            text="👨‍🏫 Instructor Schedules",
            font=self.header_font,
            bg=self.COLORS['background'],
            fg=self.COLORS['secondary']
        )
        header.pack(anchor="w", pady=(0, 15))
        
        # Create scrollable frame
        canvas = tk.Canvas(self.content_frame, bg=self.COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Get unique instructors
        instructors = sorted(self.schedule_df['Instructor'].unique())
        
        for instructor in instructors:
            instructor_data = self.schedule_df[self.schedule_df['Instructor'] == instructor].copy()
            
            # Instructor frame
            instructor_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            instructor_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Instructor header
            instructor_header = tk.Label(
                instructor_frame,
                text=f"{instructor} ({len(instructor_data)} classes)",
                font=self.section_font,
                bg=self.COLORS['secondary'],
                fg=self.COLORS['text_light'],
                anchor="w",
                padx=15,
                pady=10
            )
            instructor_header.pack(fill=tk.X)
            
            # Sort by day and time
            day_order = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4}
            instructor_data['Day_Order'] = instructor_data['Day'].map(day_order)
            instructor_data = instructor_data.sort_values(['Day_Order', 'Start_Time'])
            
            # Create treeview table
            tree_frame = tk.Frame(instructor_frame, bg='white')
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            columns = ('Day', 'Time', 'Course', 'Section', 'Room')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=min(len(instructor_data), 6))
            
            # Configure columns
            tree.column('Day', width=100, anchor='center')
            tree.column('Time', width=150, anchor='center')
            tree.column('Course', width=200, anchor='center')
            tree.column('Section', width=100, anchor='center')
            tree.column('Room', width=100, anchor='center')
            
            # Headers
            for col in columns:
                tree.heading(col, text=col)
            
            # Add data
            for _, row in instructor_data.iterrows():
                time_str = f"{row['Start_Time']} - {row['End_Time']}"
                course_str = f"{row['Course_Code']} ({row['Activity_Type']})"
                
                values = (
                    row['Day'],
                    time_str,
                    course_str,
                    str(row['Section_ID']),
                    row['Room']
                )
                
                tree.insert('', 'end', values=values)
            
            tree.pack(fill=tk.BOTH, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def launch_timetable_gui(schedule_df):
    """Launch the multi-page GUI"""
    app = ModernTimetableGUI(schedule_df)
    app.run()


# Standalone execution for testing
if __name__ == "__main__":
    # Load sample data (for testing)
    try:
        df = pd.read_csv("generated_timetable.csv")
        print("✅ Loaded generated_timetable.csv")
        print(f"📊 {len(df)} classes found")
        print("\n🚀 Launching Interactive GUI...")
        launch_timetable_gui(df)
    except FileNotFoundError:
        print("❌ Error: generated_timetable.csv not found!")
        print("   Run the CSP solver first to generate the timetable.")
        print("   Command: python csp.py  OR  python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
