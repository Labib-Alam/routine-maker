# Class Routine Generator

This Python project generates class routines for multiple classes while ensuring that teachers don't have overlapping schedules.

## Features

- Generates routines for multiple classes
- Prevents teacher scheduling conflicts
- Exports routines to Excel file with separate sheets for each class
- Customizable time slots and days

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the routine generator:
```bash
python routine_generator.py
```

## Customization

You can modify the following in the `routine_generator.py` file:

- Class names
- Teachers and their subjects
- Subjects for each class
- Time slots
- Days of the week

## Output

The program generates an Excel file named `class_routines.xlsx` with separate sheets for each class's routine.
