# Cecile_Legacy

---

# Task Manager Application Overview

## Objective

The purpose of this application is to manage tasks in a simple and intuitive user interface. Users can add, view, and delete tasks. The application handles these tasks through local storage, organizing tasks into different directories for better management. 

## Technologies Used

- Python for the backend logic
- PyQt5 for the GUI
- JSON for data storage
- Built-in libraries like `datetime` and `shutil` for additional functionalities

## Features

### Initialize Directories

Upon startup, the application checks for the existence of the `task`, `completed`, and `trash` directories. If these don't exist, they are created.

### User Interface

- **Task Title Input**: A text input field for entering the title of a new task.
- **Task Details Input**: A text box for entering detailed information about a new task.
- **Add Task Button**: A button that, when clicked, adds a new task to the system.
- **Scroll Area**: A scrollable area displaying the titles of all tasks stored in the `task` directory.

### Task Management

- **Adding Tasks**: Users can add new tasks by entering a title and details. These tasks are then saved as JSON files in the `task` directory.
- **Viewing Tasks**: Clicking on a task title in the scroll area brings up a dialog showing more details about the task, such as its timestamp.
- **Deleting Tasks**: From the details dialog, users can choose to delete a task. The corresponding JSON file is moved to the `trash` directory.

### Data Storage

- **Task Directory**: Holds the JSON files for active tasks.
- **Completed Directory**: Intended for tasks that have been marked as completed (not implemented in the current version).
- **Trash Directory**: Holds the JSON files for deleted tasks.

### Dynamic Updates

The UI updates dynamically to reflect the addition or deletion of tasks.

---

This detailed explanation should provide a comprehensive understanding of how the Task Manager application functions. Would you like additional details on any specific part of the code or feature?