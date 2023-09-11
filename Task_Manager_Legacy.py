import sys
import os
import json
import datetime
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, \
    QScrollArea, QMessageBox, QDialog
from PyQt5.QtCore import Qt


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.setGeometry(100, 100, 500, 400)

        self.tasks = []

        self.init_ui()

        self.create_directory("task")
        self.create_directory(os.path.join("task", "completed"))
        self.create_directory(os.path.join("task", "drafts"))  # Added 'drafts' directory

        self.load_existing_tasks()

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def init_ui(self):
        layout = QVBoxLayout()

        self.task_title_input = QLineEdit(self)
        self.task_details_input = QTextEdit(self)
        self.add_task_button = QPushButton("Add Task", self)
        self.view_completed_drafts_button = QPushButton("View Completed & Drafts", self)  # Added button

        layout.addWidget(QLabel("Task Title:"))
        layout.addWidget(self.task_title_input)
        layout.addWidget(QLabel("Task Details:"))
        layout.addWidget(self.task_details_input)
        layout.addWidget(self.add_task_button)
        layout.addWidget(self.view_completed_drafts_button)  # Added button

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.add_task_button.clicked.connect(self.add_task)
        self.view_completed_drafts_button.clicked.connect(self.view_completed_drafts)  # Connect the button

    def load_existing_tasks(self):
        task_dir = "task"
        completed_dir = os.path.join(task_dir, "completed")
        trash_dir = os.path.join(task_dir, "trash")

        for filename in os.listdir(task_dir):
            if filename.endswith(".json"):
                task_path = os.path.join(task_dir, filename)

                # Skip tasks in 'completed' and 'trash' directories
                if task_path.startswith(completed_dir) or task_path.startswith(trash_dir):
                    continue

                with open(task_path, "r") as f:
                    task = json.load(f)
                    self.tasks.insert(0, task)
                    self.add_task_title_label(task, at_top=True)

    def add_task(self):
        title = self.task_title_input.text()
        details = self.task_details_input.toPlainText()

        if title and details:
            task = {
                "title": title,
                "details": details,
                "timestamp": str(datetime.datetime.now()),
                "tags": []
            }
            self.tasks.insert(0, task)
            self.add_task_title_label(task, at_top=True)

            task_filename = os.path.join("task", f"{title}.json")
            with open(task_filename, "w") as f:
                json.dump(task, f, indent=4)

            self.task_title_input.clear()
            self.task_details_input.clear()

            QMessageBox.information(self, "Task Added", "Task has been added successfully.")

    def add_task_title_label(self, task, at_top=False):
        task_title_label = QLabel(task["title"])
        task_title_label.mousePressEvent = lambda event: self.show_task_details(task)

        if at_top:
            self.scroll_layout.insertWidget(0, task_title_label)
        else:
            self.scroll_layout.addWidget(task_title_label)

    def show_task_details(self, task):
        dialog = QDialog(self)
        dialog.setWindowTitle(task["title"])
        dialog.setGeometry(200, 200, 500, 300)  # Increase width for better text wrapping

        layout = QVBoxLayout()

        title_label = QLabel("Title: " + task["title"])
        details_label = QLabel("Details: " + task["details"])
        timestamp_label = QLabel("Timestamp: " + task["timestamp"])

        # Make text selectable
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        timestamp_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Set word wrap for details_label
        details_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(details_label)
        layout.addWidget(timestamp_label)

        complete_button = QPushButton("Complete", dialog)
        complete_button.clicked.connect(lambda: self.complete_task(task, dialog))

        draft_button = QPushButton("Draft", dialog)
        draft_button.clicked.connect(lambda: self.draft_task(task, dialog))

        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)

        layout.addWidget(complete_button)
        layout.addWidget(draft_button)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def complete_task(self, task, dialog):
        # Handle task completion here
        completed_filename = os.path.join("task", "completed", f"{task['title']}.json")
        with open(completed_filename, "w") as f:
            json.dump(task, f, indent=4)

        # Remove task from the current view
        self.remove_task_from_view(task)

        dialog.close()

    def draft_task(self, task, dialog):
        # Handle task drafting here
        drafts_directory = os.path.join("task", "drafts")

        # Ensure the drafts directory exists
        self.create_directory(drafts_directory)

        draft_filename = os.path.join(drafts_directory, f"{task['title']}.json")
        with open(draft_filename, "w") as f:
            json.dump(task, f, indent=4)

        # Remove task from the current view
        self.remove_task_from_view(task)

        dialog.close()

    def remove_task_from_view(self, task):
        # Remove the task label from the viewer
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                label_title = widget.text()
                if label_title == task["title"]:
                    self.scroll_layout.removeWidget(widget)
                    widget.deleteLater()
                    break

    def view_completed_drafts(self):
        completed_tasks = self.load_tasks_from_directory("task/completed")
        draft_tasks = self.load_tasks_from_directory("task/drafts")

        # Create a dialog to display completed and draft tasks
        dialog = QDialog(self)
        dialog.setWindowTitle("Completed & Draft Tasks")
        dialog.setGeometry(200, 200, 500, 300)  # Adjust size as needed

        layout = QVBoxLayout()

        scroll_area_completed = QScrollArea()
        completed_widget = QWidget()
        completed_layout = QVBoxLayout(completed_widget)
        completed_label = QLabel("Completed Tasks:")

        for task in completed_tasks:
            completed_layout.addWidget(QLabel(f"- {task['title']}"))

        scroll_area_completed.setWidget(completed_widget)
        scroll_area_completed.setWidgetResizable(True)

        scroll_area_drafts = QScrollArea()
        drafts_widget = QWidget()
        drafts_layout = QVBoxLayout(drafts_widget)
        draft_label = QLabel("Draft Tasks:")

        for task in draft_tasks:
            drafts_layout.addWidget(QLabel(f"- {task['title']}"))

        scroll_area_drafts.setWidget(drafts_widget)
        scroll_area_drafts.setWidgetResizable(True)

        layout.addWidget(completed_label)
        layout.addWidget(scroll_area_completed)
        layout.addWidget(draft_label)
        layout.addWidget(scroll_area_drafts)

        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)

        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def load_tasks_from_directory(self, directory):
        tasks = []

        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith(".json"):
                    task_path = os.path.join(directory, filename)

                    with open(task_path, "r") as f:
                        task = json.load(f)
                        tasks.append(task)

        return tasks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
