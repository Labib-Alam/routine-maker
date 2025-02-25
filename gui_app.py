from textwrap import fill
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from routine_generator import RoutineGenerator
import json
import os
import subprocess
import time
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Set icon for splash screen
        icon_path = get_resource_path('logo.ico')
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        # Set window dimensions
        self.width = 400
        self.height = 200
        
        # Configure style
        style = ttk.Style()
        style.configure("Splash.TLabel", font=("Helvetica", 16, "bold"), foreground="#1F4E78")
        style.configure("Sub.TLabel", font=("Helvetica", 10), foreground="#666666")
        
        # Create frame with padding
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Add title
        title = ttk.Label(frame, text="Class Routine Maker", style="Splash.TLabel")
        title.pack(pady=(20,5))
        
        # Add sub heading
        sub_heading = ttk.Label(frame, text="by Labib Technology", style="Sub.TLabel")
        sub_heading.pack(pady=(0,20))
        
        # Add progress bar
        self.progress = ttk.Progressbar(frame, length=300, mode='determinate', 
                                      style='info.Horizontal.TProgressbar')
        self.progress.pack(pady=10)
        
        # Make window floating
        self.lift()
        self.attributes('-topmost', True)
        
        # Center the window after all widgets are added
        self.update_idletasks()  # Ensure window size is updated
        self.center_window()
        
        # Start progress
        self.progress_value = 0
        self.update_progress()
    
    def center_window(self):
        """Center the window on the screen"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.geometry(f'{self.width}x{self.height}+{x}+{y}')
        
    def update_progress(self):
        if self.progress_value < 100:
            self.progress_value += 4
            self.progress['value'] = self.progress_value
            self.after(50, self.update_progress)  # Update every 50ms
        else:
            self.after(200, self.destroy)  # Close after 0.2 seconds when full

class RoutineGeneratorApp:
    def __init__(self, root):
        # Show splash screen first
        splash = SplashScreen(root)
        root.withdraw()  # Hide main window
        
        # Set icon for main window
        icon_path = get_resource_path('logo.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        
        # Set window dimensions
        self.width = 800
        self.height = 600
        
        self.root = root
        self.root.title("Class Routine Generator")
        
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
        
        # Configure grid weights for main window
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Data storage
        self.subjects_list = []
        self.teachers_data = {}  # {teacher_name: [subject1, subject2, ...]}
        self.classes_data = {}   # {class_name: [subject1, subject2, ...]}
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        
        # Create tabs
        self.create_subjects_tab()
        self.create_teachers_tab()
        self.create_classes_tab()
        self.create_generate_tab()
        
        # Load saved data if exists
        self.load_data()
        
        # Center the window after all widgets are added
        root.update_idletasks()
        self.center_window()
        
        # Wait for splash screen
        root.after(1000, lambda: self.show_main_window(root))

    def show_main_window(self, root):
        root.deiconify()  # Show main window

    def center_window(self):
        """Center the window on the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f'{self.width}x{self.height}+{x}+{y}')

    def create_subjects_tab(self):
        subjects_frame = ttk.Frame(self.notebook)
        self.notebook.add(subjects_frame, text="Subjects")
        
        # Configure grid weights
        subjects_frame.grid_columnconfigure(0, weight=1)
        subjects_frame.grid_rowconfigure(1, weight=1)
        
        # Subject input section
        input_frame = ttk.LabelFrame(subjects_frame, text="Add Subject", padding=10)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        input_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Label(input_frame, text="Subject Name:").grid(row=0, column=0, padx=5, pady=5)
        self.subject_name = ttk.Entry(input_frame, width=80)
        self.subject_name.grid(row=0, column=2, padx=10, pady=5, sticky='ew')
        
        ttk.Button(input_frame, text="Add Subject", style='primary.TButton', 
                  command=self.add_subject).grid(row=0, column=3, columnspan=2, pady=10)
        
        # Subjects list
        list_frame = ttk.LabelFrame(subjects_frame, text="Subjects List", padding=10)
        list_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.subjects_tree = ttk.Treeview(list_frame, columns=(), show="tree")
        self.subjects_tree.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbar to tree
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.subjects_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky='ns')
        self.subjects_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        ttk.Button(list_frame, text="Remove Selected", style='danger.TButton',
                  command=self.remove_subject).grid(row=1, column=0, columnspan=2, pady=5, sticky='e')

    def create_teachers_tab(self):
        teachers_frame = ttk.Frame(self.notebook)
        self.notebook.add(teachers_frame, text="Teachers")
        
        # Configure grid weights
        teachers_frame.grid_columnconfigure(0, weight=1)
        teachers_frame.grid_rowconfigure(1, weight=1)
        
        # Teacher input section
        input_frame = ttk.LabelFrame(teachers_frame, text="Add Teacher", padding=10)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Label(input_frame, text="Teacher Name:").grid(row=0, column=0, padx=5, pady=5)
        self.teacher_name = ttk.Entry(input_frame, width=40)
        self.teacher_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Subjects selection
        ttk.Label(input_frame, text="Select Subjects:").grid(row=0, column=2, padx=5, pady=5)
        
        # Create a frame to hold listbox and scrollbar
        subjects_frame = ttk.Frame(input_frame)
        subjects_frame.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        subjects_frame.grid_columnconfigure(0, weight=1)
        
        # Create listbox and scrollbar
        self.subjects_listbox = tk.Listbox(subjects_frame, selectmode=tk.MULTIPLE, height=4, width=40, **self.listbox_config)
        scrollbar = ttk.Scrollbar(subjects_frame, orient="vertical", command=self.subjects_listbox.yview)
        self.subjects_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Pack listbox and scrollbar
        self.subjects_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        ttk.Button(input_frame, text="Add Teacher", style='primary.TButton',
                  command=self.add_teacher).grid(row=1, column=3, pady=10, sticky='e')
        
        # Teachers list
        list_frame = ttk.LabelFrame(teachers_frame, text="Teachers List", padding=10)
        list_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.teachers_tree = ttk.Treeview(list_frame, show="tree")
        self.teachers_tree.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbar to tree
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.teachers_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky='ns')
        self.teachers_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        ttk.Button(list_frame, text="Remove Selected", style='danger.TButton',
                  command=self.remove_teacher).grid(row=1, column=0, columnspan=2, pady=5, sticky='e')

    def create_classes_tab(self):
        classes_frame = ttk.Frame(self.notebook)
        self.notebook.add(classes_frame, text="Classes")
        
        # Configure grid weights
        classes_frame.grid_columnconfigure(0, weight=1)
        classes_frame.grid_rowconfigure(1, weight=1)
        
        # Class input section
        input_frame = ttk.LabelFrame(classes_frame, text="Add Class", padding=10)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Label(input_frame, text="Class Name:").grid(row=0, column=0, padx=5, pady=5)
        self.class_name = ttk.Entry(input_frame, width=40)
        self.class_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Subjects selection for class
        ttk.Label(input_frame, text="Select Subjects:").grid(row=0, column=2, padx=5, pady=5)
        
        # Create a frame to hold listbox and scrollbar
        class_subjects_frame = ttk.Frame(input_frame)
        class_subjects_frame.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        class_subjects_frame.grid_columnconfigure(0, weight=1)
        
        # Create listbox and scrollbar
        self.class_subjects_listbox = tk.Listbox(class_subjects_frame, selectmode=tk.MULTIPLE, height=4, width=40, **self.listbox_config)
        class_scrollbar = ttk.Scrollbar(class_subjects_frame, orient="vertical", command=self.class_subjects_listbox.yview)
        self.class_subjects_listbox.configure(yscrollcommand=class_scrollbar.set)
        
        # Pack listbox and scrollbar
        self.class_subjects_listbox.pack(side='left', fill='both', expand=True)
        class_scrollbar.pack(side='right', fill='y')
        
        ttk.Button(input_frame, text="Add Class", style='primary.TButton',
                  command=self.add_class).grid(row=1, column=3, pady=10, sticky='e')
        
        # Classes list
        list_frame = ttk.LabelFrame(classes_frame, text="Classes List", padding=10)
        list_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.classes_tree = ttk.Treeview(list_frame, show="tree")
        self.classes_tree.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbar to tree
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.classes_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky='ns')
        self.classes_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        ttk.Button(list_frame, text="Remove Selected", style='danger.TButton',
                  command=self.remove_class).grid(row=1, column=0, columnspan=2, pady=5, sticky='e')

    def create_generate_tab(self):
        generate_frame = ttk.Frame(self.notebook)
        self.notebook.add(generate_frame, text="Generate Routine")
        
        # Settings frame
        settings_frame = ttk.LabelFrame(generate_frame, text="Settings", padding=10)
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # Working Days Selection
        days_frame = ttk.Frame(settings_frame)
        days_frame.pack(fill='x', padx=5, pady=15)
        ttk.Label(days_frame, text="Working Days:", font=('Helvetica', 10, 'bold')).pack(anchor='w')
        
        self.days_vars = {}
        all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days_checkframe = ttk.Frame(days_frame)
        days_checkframe.pack(fill='x', padx=20, pady=10)
        
        for i, day in enumerate(all_days):
            var = tk.BooleanVar(value=True if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] else False)
            self.days_vars[day] = var
            ttk.Checkbutton(days_checkframe, text=day, variable=var).grid(row=0, column=i, padx=5, pady=5, sticky='w')
        
        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', padx=5, pady=6)
        
        # Periods and Time settings in same row
        settings_row_frame = ttk.Frame(settings_frame)
        settings_row_frame.pack(fill='x', padx=5, pady=15)
        
        # Periods per day
        ttk.Label(settings_row_frame, text="Periods per day:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=5, pady=10)
        self.periods_spinbox = ttk.Spinbox(settings_row_frame, from_=1, to=12, width=20)
        self.periods_spinbox.set(6)  # Default value
        self.periods_spinbox.grid(row=0, column=1, padx=5, pady=10)
        
        # Time settings
        ttk.Label(settings_row_frame, text="Start Time (HH:MM):", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=(20,5), pady=10)
        self.start_time = ttk.Entry(settings_row_frame, width=20)
        self.start_time.insert(0, "08:30")
        self.start_time.grid(row=0, column=3, padx=5, pady=10)
        
        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', padx=5, pady=6)
        
        # Output file settings
        file_frame = ttk.Frame(settings_frame)
        file_frame.pack(fill='x', padx=5, pady=15)
        
        ttk.Label(file_frame, text="Output File:", font=('Helvetica', 10, 'bold')).pack(side='left', padx=5)
        self.output_filename = ttk.Entry(file_frame)
        self.output_filename.insert(0, "class_routines.xlsx")
        self.output_filename.pack(side='left', padx=5, fill='x', expand=True)
        
        # Browse button
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_save_location,
                  style='secondary.TButton').pack(side='right', padx=5)
        
        # Auto-open checkbox
        self.auto_open_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, 
                       text="Automatically open file after generation",
                       variable=self.auto_open_var,
                       style='primary.TCheckbutton').pack(anchor='w', padx=5, pady=5)
        
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

    def browse_save_location(self):
        initial_file = self.output_filename.get()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=initial_file,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.output_filename.delete(0, tk.END)
            self.output_filename.insert(0, file_path)

    def open_file(self, filepath):
        if os.path.exists(filepath):
            try:
                os.startfile(filepath)
            except AttributeError:  # For non-Windows systems
                subprocess.call(['xdg-open', filepath])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

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
            
            success_message = f"Routine has been generated and saved as {output_file}"
            self.status_label.config(
                text=f"Routine generated successfully!\nSaved as: {output_file}",
                foreground="green"
            )
            
            if self.auto_open_var.get():
                self.open_file(output_file)
                success_message += "\nFile has been opened automatically."
            
            messagebox.showinfo("Success", success_message)
            
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
