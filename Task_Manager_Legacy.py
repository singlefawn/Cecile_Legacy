# task_manager.py
# Julia Task Manager Legacy
# 1997 admin POD



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
        self.create_directory(os.path.join("task", "trash"))

        self.load_existing_tasks()

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def init_ui(self):
        layout = QVBoxLayout()

        self.task_title_input = QLineEdit(self)
        self.task_details_input = QTextEdit(self)
        self.add_task_button = QPushButton("Add Task", self)
        self.scroll_area = QScrollArea(self)

        layout.addWidget(QLabel("Task Title:"))
        layout.addWidget(self.task_title_input)
        layout.addWidget(QLabel("Task Details:"))
        layout.addWidget(self.task_details_input)
        layout.addWidget(self.add_task_button)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(self.scroll_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.add_task_button.clicked.connect(self.add_task)

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
        dialog.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        title_label = QLabel("Title: " + task["title"])
        details_label = QLabel("Details: " + task["details"])
        timestamp_label = QLabel("Timestamp: " + task["timestamp"])

        # Make text selectable
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        timestamp_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(title_label)
        layout.addWidget(details_label)
        layout.addWidget(timestamp_label)

        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)

        delete_button = QPushButton("Delete", dialog)
        delete_button.clicked.connect(lambda: self.delete_task(task, dialog))

        layout.addWidget(delete_button)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def delete_task(self, task, dialog):
        trash_path = os.path.join("task", "trash", f"{task['title']}.json")
        original_path = os.path.join("task", f"{task['title']}.json")

        shutil.move(original_path, trash_path)

        # Clear all task labels from the viewer
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()

        # Reload tasks from directory
        self.load_existing_tasks()

        dialog.close()


class TaskDetailsDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle(task["title"])
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Title: " + task["title"]))
        layout.addWidget(QLabel("Details: " + task["details"]))
        layout.addWidget(QLabel("Timestamp: " + task["timestamp"]))

        complete_button = QPushButton("Complete", self)
        close_button = QPushButton("Close", self)

        complete_button.clicked.connect(self.complete_task)
        close_button.clicked.connect(self.close)

        layout.addWidget(complete_button)
        layout.addWidget(close_button)

        self.setLayout(layout)

        self.task = task

    def complete_task(self):
        # Handle task completion here
        completed_filename = os.path.join("task", "completed", f"{self.task['title']}.json")
        with open(completed_filename, "w") as f:
            json.dump(self.task, f, indent=4)

        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
