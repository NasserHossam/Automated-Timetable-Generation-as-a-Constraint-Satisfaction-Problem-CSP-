# pdf_generator.py
"""
PDF Timetable Generator
Creates professional timetable PDFs from generated_timetable.csv
Uses reportlab for PDF generation
"""

import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class TimetablePDFGenerator:
    """Generate professional PDF timetables"""
    
    # Modern Color Scheme
    COLORS = {
        'primary': colors.HexColor('#2C3E50'),
        'secondary': colors.HexColor('#3498DB'),
        'accent': colors.HexColor('#E74C3C'),
        'success': colors.HexColor('#27AE60'),
        'warning': colors.HexColor('#F39C12'),
        'background': colors.HexColor('#ECF0F1'),
        'header_bg': colors.HexColor('#34495E'),
        'border': colors.HexColor('#BDC3C7'),
        'text_dark': colors.HexColor('#2C3E50'),
        'text_light': colors.white,
    }
    
    # Activity type colors
    ACTIVITY_COLORS = {
        'Lecture': colors.HexColor('#3498DB'),
        'Lab': colors.HexColor('#27AE60'),
        'Lecture and Lab': colors.HexColor('#9B59B6'),
        'Tutorial': colors.HexColor('#F39C12'),
    }
    
    def __init__(self, filename='timetable_output.pdf'):
        """Initialize PDF generator"""
        self.filename = filename
        self.pagesize = landscape(A4)
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=self.pagesize,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.story = []
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.COLORS['secondary'],
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['text_dark'],
            alignment=TA_LEFT
        ))
    
    def add_title_page(self, schedule_df):
        """Add title page with summary"""
        # Title
        title_para = Paragraph('University Timetable', self.styles['CustomTitle'])
        self.story.append(title_para)
        
        # Subtitle
        subtitle_text = f"Academic Year 2025-2026 • Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        subtitle_para = Paragraph(subtitle_text, self.styles['InfoText'])
        self.story.append(subtitle_para)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        self._add_summary_statistics(schedule_df)
    
    def _add_summary_statistics(self, schedule_df):
        """Add summary statistics"""
        section_para = Paragraph('📊 Schedule Summary', self.styles['SectionHeader'])
        self.story.append(section_para)
        
        # Calculate statistics
        total_classes = len(schedule_df)
        unique_courses = schedule_df['Course_Code'].nunique()
        unique_sections = schedule_df['Section_ID'].nunique()
        unique_instructors = schedule_df['Instructor'].nunique()
        rooms_used = schedule_df['Room'].nunique()
        
        # Count by type
        type_counts = {}
        for activity_type in schedule_df['Activity_Type'].unique():
            type_counts[activity_type] = len(schedule_df[schedule_df['Activity_Type'] == activity_type])
        
        # Create summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Classes Scheduled', str(total_classes)],
            ['Unique Courses', str(unique_courses)],
            ['Unique Sections', str(unique_sections)],
            ['Instructors Involved', str(unique_instructors)],
            ['Rooms Used', str(rooms_used)],
        ]
        
        # Add type breakdown
        for activity_type, count in type_counts.items():
            summary_data.append([f'{activity_type} Sessions', str(count)])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['header_bg']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['text_light']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['background']])
        ]))
        
        self.story.append(summary_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_timetable_by_section(self, schedule_df):
        """Add timetable organized by section"""
        section_para = Paragraph('📅 Timetable by Section', self.styles['SectionHeader'])
        self.story.append(section_para)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Get unique sections
        sections = sorted(schedule_df['Section_ID'].unique())
        
        for i, section_id in enumerate(sections):
            section_data = schedule_df[schedule_df['Section_ID'] == section_id].copy()
            
            # Section header
            section_title = f"Section {section_id}"
            section_header = Paragraph(section_title, self.styles['InfoText'])
            self.story.append(section_header)
            
            # Sort by day and time
            day_order = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4}
            section_data['Day_Order'] = section_data['Day'].map(day_order)
            section_data = section_data.sort_values(['Day_Order', 'Start_Time'])
            
            # Create table data
            table_data = [['Day', 'Time', 'Course', 'Type', 'Instructor', 'Room']]
            
            for _, row in section_data.iterrows():
                time_str = f"{row['Start_Time']}-{row['End_Time']}"
                course_str = f"{row['Course_Code']}"
                
                table_data.append([
                    row['Day'],
                    time_str,
                    course_str,
                    row['Activity_Type'],
                    row['Instructor'],
                    row['Room']
                ])
            
            # Create table
            col_widths = [0.9*inch, 1.1*inch, 1*inch, 1.2*inch, 2*inch, 0.8*inch]
            section_table = Table(table_data, colWidths=col_widths)
            
            # Apply styling
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['header_bg']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['text_light']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['background']]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]
            
            # Color activity types
            for j, row in enumerate(section_data.iterrows(), start=1):
                activity_type = row[1]['Activity_Type']
                if activity_type in self.ACTIVITY_COLORS:
                    style_commands.append(
                        ('TEXTCOLOR', (3, j), (3, j), self.ACTIVITY_COLORS[activity_type])
                    )
                    style_commands.append(
                        ('FONTNAME', (3, j), (3, j), 'Helvetica-Bold')
                    )
            
            section_table.setStyle(TableStyle(style_commands))
            self.story.append(section_table)
            self.story.append(Spacer(1, 0.15*inch))
            
            # Page break after every 4 sections
            if (i + 1) % 4 == 0 and i < len(sections) - 1:
                self.story.append(PageBreak())
    def add_timetable_by_day(self, schedule_df):
        """Add timetable organized by day"""
        self.story.append(PageBreak())
        
        section_para = Paragraph('📆 Timetable by Day', self.styles['SectionHeader'])
        self.story.append(section_para)
        self.story.append(Spacer(1, 0.1*inch))
        
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
        
        for day in days:
            day_data = schedule_df[schedule_df['Day'] == day].copy()
            
            if len(day_data) == 0:
                continue
            
            # Day header
            day_header = Paragraph(f"<b>{day}</b> ({len(day_data)} classes)", self.styles['InfoText'])
            self.story.append(day_header)
            
            # Sort by time
            day_data = day_data.sort_values(['Start_Time', 'Section_ID'])
            
            # Create table
            table_data = [['Time', 'Section', 'Course', 'Type', 'Instructor', 'Room']]
            
            for _, row in day_data.iterrows():
                time_str = f"{row['Start_Time']}-{row['End_Time']}"
                
                table_data.append([
                    time_str,
                    row['Section_ID'],
                    row['Course_Code'],
                    row['Activity_Type'],
                    row['Instructor'],
                    row['Room']
                ])
            
            col_widths = [1*inch, 1*inch, 1*inch, 1.2*inch, 2*inch, 0.8*inch]
            day_table = Table(table_data, colWidths=col_widths)
            
            day_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['text_light']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['background']]),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            self.story.append(day_table)
            self.story.append(Spacer(1, 0.2*inch))
    
    def add_instructor_schedules(self, schedule_df):
        """Add instructor schedules"""
        self.story.append(PageBreak())
        
        section_para = Paragraph('👨‍🏫 Instructor Schedules', self.styles['SectionHeader'])
        self.story.append(section_para)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Get unique instructors
        instructors = sorted(schedule_df['Instructor'].unique())
        
        for i, instructor in enumerate(instructors):
            instructor_data = schedule_df[schedule_df['Instructor'] == instructor].copy()
            
            # Instructor header
            instructor_header = Paragraph(
                f"<b>{instructor}</b> ({len(instructor_data)} classes)",
                self.styles['InfoText']
            )
            self.story.append(instructor_header)
            
            # Sort by day and time
            day_order = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4}
            instructor_data['Day_Order'] = instructor_data['Day'].map(day_order)
            instructor_data = instructor_data.sort_values(['Day_Order', 'Start_Time'])
            
            # Create table
            table_data = [['Day', 'Time', 'Course', 'Section', 'Room']]
            
            for _, row in instructor_data.iterrows():
                time_str = f"{row['Start_Time']}-{row['End_Time']}"
                course_str = f"{row['Course_Code']} ({row['Activity_Type']})"
                
                table_data.append([
                    row['Day'],
                    time_str,
                    course_str,
                    str(row['Section_ID']),
                    row['Room']
                ])
            
            col_widths = [1*inch, 1.1*inch, 1.8*inch, 1*inch, 0.8*inch]
            instructor_table = Table(table_data, colWidths=col_widths)
            
            instructor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['success']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['text_light']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['background']]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            self.story.append(instructor_table)
            self.story.append(Spacer(1, 0.15*inch))
            
            # Page break after every 6 instructors
            if (i + 1) % 6 == 0 and i < len(instructors) - 1:
                self.story.append(PageBreak())
    
    def generate(self, schedule_df):
        """Generate the complete PDF"""
        print("\n" + "="*80)
        print("GENERATING PDF TIMETABLE")
        print("="*80)
        
        # Add all sections
        self.add_title_page(schedule_df)
        self.add_timetable_by_section(schedule_df)
        self.add_timetable_by_day(schedule_df)
        self.add_instructor_schedules(schedule_df)
        
        # Build PDF
        self.doc.build(self.story)
        
        print(f"\n✅ PDF generated successfully: {self.filename}")
        print(f"   Pages: Title + Sections + Days + Instructors")
        print(f"   File size: Check {self.filename}")
        
        return self.filename


def generate_timetable_pdf(csv_file='generated_timetable.csv', pdf_file='timetable_output.pdf'):
    """Convenience function to generate PDF from CSV"""
    print("\n" + "="*80)
    print("PDF TIMETABLE GENERATOR")
    print("="*80)
    
    try:
        # Load CSV
        print(f"\n📂 Loading: {csv_file}")
        schedule_df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(schedule_df)} classes")
        
        # Generate PDF
        pdf_gen = TimetablePDFGenerator(pdf_file)
        result_file = pdf_gen.generate(schedule_df)
        
        print("\n" + "="*80)
        print("✅ PDF GENERATION COMPLETE!")
        print("="*80)
        print(f"\nOutput file: {result_file}")
        print("\nThe PDF includes:")
        print("  📊 Summary statistics")
        print("  📅 Timetables by section")
        print("  📆 Timetables by day")
        print("  👨‍🏫 Instructor schedules")
        print("="*80 + "\n")
        
        return result_file
        
    except FileNotFoundError:
        print(f"\n❌ Error: {csv_file} not found!")
        print("   Please run csp.py first to generate the timetable CSV.")
        return None
    except Exception as e:
        print(f"\n❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


# Main execution
if __name__ == "__main__":
    generate_timetable_pdf()
