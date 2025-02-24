import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from routine_generator import RoutineGenerator
import json
import os

class RoutineGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Routine Generator")
        self.root.geometry("800x600")
        
        # Configure colors for dark theme
        self.style = ttk.Style()
        self.style.configure("Treeview", background="#2c2c2c", foreground="white", fieldbackground="#2c2c2c")
        self.style.configure("Treeview.Heading", background="#2c2c2c", foreground="white")
        self.style.map('Treeview', background=[('selected', '#0d6efd')])
        
        # Configure Listbox colors
        self.listbox_config = {
            'bg': '#2c2c2c',
            'fg': 'white',
            'selectbackground': '#0d6efd',
            'selectforeground': 'white'
        }
        
        # Data storage
        self.subjects_list = []
        self.teachers_data = {}  # {teacher_name: [subject1, subject2, ...]}
        self.classes_data = {}   # {class_name: [subject1, subject2, ...]}
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_subjects_tab()
        self.create_teachers_tab()
        self.create_classes_tab()
        self.create_generate_tab()
        
        # Load saved data if exists
        self.load_data()

    def create_subjects_tab(self):
        subjects_frame = ttk.Frame(self.notebook)
        self.notebook.add(subjects_frame, text="Subjects")
        
        # Subject input section
        input_frame = ttk.LabelFrame(subjects_frame, text="Add Subject", padding=10)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Subject Name:").grid(row=0, column=0, padx=5, pady=5)
        self.subject_name = ttk.Entry(input_frame)
        self.subject_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Add Subject", style='primary.TButton', 
                  command=self.add_subject).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Subjects list
        list_frame = ttk.LabelFrame(subjects_frame, text="Subjects List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.subjects_tree = ttk.Treeview(list_frame, columns=(), show="tree")
        self.subjects_tree.pack(fill='both', expand=True)
        
        ttk.Button(list_frame, text="Remove Selected", style='danger.TButton',
                  command=self.remove_subject).pack(pady=5)

    def create_teachers_tab(self):
        teachers_frame = ttk.Frame(self.notebook)
        self.notebook.add(teachers_frame, text="Teachers")
        
        # Teacher input section
        input_frame = ttk.LabelFrame(teachers_frame, text="Add Teacher", padding=10)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Teacher Name:").grid(row=0, column=0, padx=5, pady=5)
        self.teacher_name = ttk.Entry(input_frame)
        self.teacher_name.grid(row=0, column=1, padx=5, pady=5)
        
        # Subjects selection
        ttk.Label(input_frame, text="Select Subjects:").grid(row=1, column=0, padx=5, pady=5)
        self.subjects_listbox = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, height=5, **self.listbox_config)
        self.subjects_listbox.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(input_frame, text="Add Teacher", style='primary.TButton',
                  command=self.add_teacher).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Teachers list
        list_frame = ttk.LabelFrame(teachers_frame, text="Teachers List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.teachers_tree = ttk.Treeview(list_frame, show="tree")
        self.teachers_tree.pack(fill='both', expand=True)
        
        ttk.Button(list_frame, text="Remove Selected", style='danger.TButton',
                  command=self.remove_teacher).pack(pady=5)

    def create_classes_tab(self):
        classes_frame = ttk.Frame(self.notebook)
        self.notebook.add(classes_frame, text="Classes")
        
        # Class input section
        input_frame = ttk.LabelFrame(classes_frame, text="Add Class", padding=10)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(input_frame, text="Class Name:").grid(row=0, column=0, padx=5, pady=5)
        self.class_name = ttk.Entry(input_frame)
        self.class_name.grid(row=0, column=1, padx=5, pady=5)
        
        # Subjects selection for class
        ttk.Label(input_frame, text="Select Subjects:").grid(row=1, column=0, padx=5, pady=5)
        self.class_subjects_listbox = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, height=5, **self.listbox_config)
        self.class_subjects_listbox.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(input_frame, text="Add Class", style='primary.TButton',
                  command=self.add_class).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Classes list
        list_frame = ttk.LabelFrame(classes_frame, text="Classes List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.classes_tree = ttk.Treeview(list_frame, show="tree")
        self.classes_tree.pack(fill='both', expand=True)
        
        ttk.Button(list_frame, text="Remove Selected", style='danger.TButton',
                  command=self.remove_class).pack(pady=5)

    def create_generate_tab(self):
        generate_frame = ttk.Frame(self.notebook)
        self.notebook.add(generate_frame, text="Generate Routine")
        
        # Settings frame
        settings_frame = ttk.LabelFrame(generate_frame, text="Settings", padding=10)
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # Working Days Selection
        days_frame = ttk.Frame(settings_frame)
        days_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(days_frame, text="Working Days:").pack(anchor='w')
        
        self.days_vars = {}
        all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days_checkframe = ttk.Frame(days_frame)
        days_checkframe.pack(fill='x', padx=20)
        
        for i, day in enumerate(all_days):
            var = tk.BooleanVar(value=True if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] else False)
            self.days_vars[day] = var
            ttk.Checkbutton(days_checkframe, text=day, variable=var).grid(row=i//3, column=i%3, padx=5, pady=2, sticky='w')
        
        # Periods per day
        periods_frame = ttk.Frame(settings_frame)
        periods_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(periods_frame, text="Periods per day:").pack(side='left', padx=5)
        self.periods_spinbox = ttk.Spinbox(periods_frame, from_=1, to=12, width=5)
        self.periods_spinbox.set(6)  # Default value
        self.periods_spinbox.pack(side='left', padx=5)
        
        # Time settings
        time_frame = ttk.Frame(settings_frame)
        time_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(time_frame, text="Start Time (HH:MM):").pack(side='left', padx=5)
        self.start_time = ttk.Entry(time_frame, width=10)
        self.start_time.insert(0, "08:30")
        self.start_time.pack(side='left', padx=5)
        
        # Output file name
        file_frame = ttk.Frame(settings_frame)
        file_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(file_frame, text="Output File Name:").pack(side='left', padx=5)
        self.output_filename = ttk.Entry(file_frame)
        self.output_filename.insert(0, "class_routines.xlsx")
        self.output_filename.pack(side='left', padx=5, fill='x', expand=True)
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(generate_frame, text="Schedule Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=8, **self.listbox_config)
        self.preview_text.pack(fill='both', expand=True)
        
        # Buttons
        button_frame = ttk.Frame(generate_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Preview Schedule", style='info.TButton',
                  command=self.preview_schedule).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Generate Routine", style='primary.TButton',
                  command=self.generate_routine).pack(side='right', padx=5)
        
        # Status label
        self.status_label = ttk.Label(generate_frame, text="")
        self.status_label.pack(pady=10)

    def add_subject(self):
        subject = self.subject_name.get().strip()
        
        if not subject:
            messagebox.showerror("Error", "Please enter a subject name!")
            return
            
        if subject in self.subjects_list:
            messagebox.showerror("Error", "Subject already exists!")
            return
            
        self.subjects_list.append(subject)
        self.subjects_tree.insert("", "end", subject, text=subject)
        
        # Update subjects in listboxes
        self.update_subject_listboxes()
        
        # Clear input
        self.subject_name.delete(0, tk.END)
        self.save_data()

    def remove_subject(self):
        selected = self.subjects_tree.selection()
        if not selected:
            return
            
        # Check if subject is in use
        for subject in selected:
            subject_name = self.subjects_tree.item(subject)['text']
            in_use = False
            
            # Check teachers
            for subjects in self.teachers_data.values():
                if subject_name in subjects:
                    in_use = True
                    break
                    
            # Check classes
            for subjects in self.classes_data.values():
                if subject_name in subjects:
                    in_use = True
                    break
            
            if in_use:
                messagebox.showerror("Error", f"Cannot remove subject '{subject_name}' as it is being used by teachers or classes!")
                continue
            
            self.subjects_list.remove(subject_name)
            self.subjects_tree.delete(subject)
        
        # Update subjects in listboxes
        self.update_subject_listboxes()
        self.save_data()

    def update_subject_listboxes(self):
        # Update teachers tab subject listbox
        self.subjects_listbox.delete(0, tk.END)
        for subject in sorted(self.subjects_list):
            self.subjects_listbox.insert(tk.END, subject)
            
        # Update classes tab subject listbox
        self.class_subjects_listbox.delete(0, tk.END)
        for subject in sorted(self.subjects_list):
            self.class_subjects_listbox.insert(tk.END, subject)

    def add_teacher(self):
        name = self.teacher_name.get().strip()
        selected_indices = self.subjects_listbox.curselection()
        subjects = [self.subjects_listbox.get(i) for i in selected_indices]
        
        if not name or not subjects:
            messagebox.showerror("Error", "Please enter teacher name and select subjects!")
            return
            
        self.teachers_data[name] = subjects
        
        # Add teacher to tree with subjects as children
        teacher_id = self.teachers_tree.insert("", "end", text=name)
        for subject in subjects:
            self.teachers_tree.insert(teacher_id, "end", text=subject)
        
        # Clear inputs
        self.teacher_name.delete(0, tk.END)
        self.subjects_listbox.selection_clear(0, tk.END)
        self.save_data()

    def add_class(self):
        name = self.class_name.get().strip()
        selected_indices = self.class_subjects_listbox.curselection()
        subjects = [self.class_subjects_listbox.get(i) for i in selected_indices]
        
        if not name or not subjects:
            messagebox.showerror("Error", "Please enter class name and select subjects!")
            return
            
        self.classes_data[name] = subjects
        
        # Add class to tree with subjects as children
        class_id = self.classes_tree.insert("", "end", text=name)
        for subject in subjects:
            self.classes_tree.insert(class_id, "end", text=subject)
        
        # Clear inputs
        self.class_name.delete(0, tk.END)
        self.class_subjects_listbox.selection_clear(0, tk.END)
        self.save_data()

    def remove_teacher(self):
        selected = self.teachers_tree.selection()
        if not selected:
            return
            
        for item in selected:
            # Only remove if parent item (teacher) is selected
            if not self.teachers_tree.parent(item):
                teacher_name = self.teachers_tree.item(item)['text']
                del self.teachers_data[teacher_name]
                self.teachers_tree.delete(item)
        self.save_data()

    def remove_class(self):
        selected = self.classes_tree.selection()
        if not selected:
            return
            
        for item in selected:
            # Only remove if parent item (class) is selected
            if not self.classes_tree.parent(item):
                class_name = self.classes_tree.item(item)['text']
                del self.classes_data[class_name]
                self.classes_tree.delete(item)
        self.save_data()

    def preview_schedule(self):
        try:
            working_days = [day for day, var in self.days_vars.items() if var.get()]
            periods = int(self.periods_spinbox.get())
            start_time = self.start_time.get()
            
            if not working_days:
                messagebox.showerror("Error", "Please select at least one working day!")
                return
                
            # Create a temporary generator to get time slots
            temp_generator = RoutineGenerator(
                working_days=working_days,
                periods_per_day=periods,
                time_slots=None  # Will generate based on start time
            )
            
            # Create preview text
            preview = "Schedule Overview:\n\n"
            preview += f"Working Days: {', '.join(working_days)}\n"
            preview += f"Periods per day: {periods}\n"
            preview += f"Time slots:\n"
            
            for slot in temp_generator.time_slots:
                preview += f"  • {slot}\n"
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, preview)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_routine(self):
        if not self.teachers_data or not self.classes_data:
            messagebox.showerror("Error", "Please add teachers and classes first!")
            return
        
        working_days = [day for day, var in self.days_vars.items() if var.get()]
        if not working_days:
            messagebox.showerror("Error", "Please select at least one working day!")
            return
            
        try:
            periods = int(self.periods_spinbox.get())
            start_time = self.start_time.get()
            
            # Convert data format for routine generator
            teachers = {}
            for teacher, teacher_subjects in self.teachers_data.items():
                for subject in teacher_subjects:
                    if subject not in teachers:
                        teachers[subject] = []
                    teachers[subject].append(teacher)
            
            generator = RoutineGenerator(
                working_days=working_days,
                periods_per_day=periods
            )
            
            routines = generator.generate_routine(
                list(self.classes_data.keys()),
                teachers,
                self.classes_data
            )
            
            output_file = self.output_filename.get()
            generator.save_to_excel(routines, output_file)
            
            self.status_label.config(
                text=f"Routine generated successfully!\nSaved as: {output_file}",
                foreground="green"
            )
            messagebox.showinfo("Success", f"Routine has been generated and saved as {output_file}")
            
        except Exception as e:
            self.status_label.config(
                text=f"Error: {str(e)}",
                foreground="red"
            )
            messagebox.showerror("Error", str(e))

    def save_data(self):
        data = {
            'subjects': self.subjects_list,
            'teachers': self.teachers_data,
            'classes': self.classes_data
        }
        with open('routine_data.json', 'w') as f:
            json.dump(data, f)

    def load_data(self):
        try:
            if os.path.exists('routine_data.json'):
                with open('routine_data.json', 'r') as f:
                    data = json.load(f)
                    
                self.subjects_list = data.get('subjects', [])
                self.teachers_data = data.get('teachers', {})
                self.classes_data = data.get('classes', {})
                
                # Update trees
                for subject in self.subjects_list:
                    self.subjects_tree.insert("", "end", subject, text=subject)
                    
                # Update teachers tree with hierarchical view
                for name, subjects in self.teachers_data.items():
                    teacher_id = self.teachers_tree.insert("", "end", text=name)
                    for subject in subjects:
                        self.teachers_tree.insert(teacher_id, "end", text=subject)
                    
                # Update classes tree with hierarchical view
                for name, subjects in self.classes_data.items():
                    class_id = self.classes_tree.insert("", "end", text=name)
                    for subject in subjects:
                        self.classes_tree.insert(class_id, "end", text=subject)
                    
                # Update subject listboxes
                self.update_subject_listboxes()
        except Exception as e:
            print(f"Error loading data: {e}")

def main():
    root = ttk.Window(themename="darkly")
    app = RoutineGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
