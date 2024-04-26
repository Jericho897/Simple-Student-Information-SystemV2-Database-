import sys
import os.path
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QDialog, QLineEdit, QComboBox, QMessageBox, QFormLayout, QDialogButtonBox, QInputDialog
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Information System")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #ffffff;")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.database_dir = os.path.dirname(os.path.abspath(__file__))
        self.course_database = os.path.join(self.database_dir, 'Course_Table.db')
        self.student_database = os.path.join(self.database_dir, 'Student_Table.db')

        self.course_fields = ['Code', 'Name'] 
        self.student_fields = ['StudentID', 'StudentName', 'Gender', 'Year', 'CourseCode']

        self.initialize_ui()

    def initialize_ui(self):
        self.create_course_tab()
        self.create_student_tab()

        # Populate tables on startup
        self.populate_course_table()
        self.populate_student_table()

    def create_course_tab(self):
        course_tab = QWidget()
        course_tab_layout = QVBoxLayout(course_tab)

        title_label = QLabel("Courses Management", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;"
            "background-color: maroon;"
            "border-radius: 20px;"
            "border:1px solid black;"
        )
        course_tab_layout.addWidget(title_label)

        button_layout = QHBoxLayout()

        add_course_btn = QPushButton("Add Course")
        add_course_btn.clicked.connect(self.add_course)
        add_course_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(add_course_btn)

        delete_course_btn = QPushButton("Delete Course")
        delete_course_btn.clicked.connect(self.delete_course)
        delete_course_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(delete_course_btn)

        update_course_btn = QPushButton("Update Course")
        update_course_btn.clicked.connect(self.update_course)
        update_course_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(update_course_btn)

        course_tab_layout.addLayout(button_layout)

        # Filter layout
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by Code:", self)
        filter_layout.addWidget(filter_label)

        self.course_filter_input = QLineEdit()
        filter_layout.addWidget(self.course_filter_input)

        filter_button = QPushButton("Filter")
        filter_button.clicked.connect(self.filter_courses)
        filter_layout.addWidget(filter_button)

        course_tab_layout.addLayout(filter_layout)

        self.course_table = QTableWidget()
        course_tab_layout.addWidget(self.course_table)

        self.tabs.addTab(course_tab, "Courses")

    def filter_courses(self):
        filter_text = self.course_filter_input.text().strip()
        if not filter_text:
            self.populate_course_table()
            return

        connection = sqlite3.connect(self.course_database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM courses WHERE Code LIKE ?", ('%' + filter_text + '%',))
        filtered_courses = cursor.fetchall()
        connection.close()

        self.populate_course_table(filtered_courses)

    def populate_course_table(self, data=None):
        connection = sqlite3.connect(self.course_database)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS courses (Code TEXT, Name TEXT)")
        if data is None:
            cursor.execute("SELECT * FROM courses")
            data = cursor.fetchall()

        self.course_table.clearContents()
        self.course_table.setRowCount(len(data))
        self.course_table.setColumnCount(len(self.course_fields))
        self.course_table.setHorizontalHeaderLabels(self.course_fields)
        for row_index, row_data in enumerate(data):
            for column_index, field in enumerate(self.course_fields):
                item = QTableWidgetItem(row_data[column_index])
                self.course_table.setItem(row_index, column_index, item)

        connection.close()

    def add_course(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Course")

        layout = QVBoxLayout(dialog)

        course_name_input = QLineEdit()
        course_code_input = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Course Code:", course_code_input)
        form_layout.addRow("Course Name:", course_name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            course_name = course_name_input.text().strip()
            course_code = course_code_input.text().strip()

            if not course_name or not course_code:
                QMessageBox.warning(self, "Error", "Both course name and code are required!")
                return

            connection = sqlite3.connect(self.course_database)
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS courses (Name TEXT, Code TEXT)")
            cursor.execute("INSERT INTO courses (Name, Code) VALUES (?, ?)", (course_name, course_code))
            connection.commit()
            connection.close()

            QMessageBox.information(self, 'Success', 'Course added successfully!')
            self.populate_course_table()

    def delete_course(self):
        course_code, ok1 = QInputDialog.getText(self, 'Course Code', 'Enter course code:')
        if not ok1:
            return

        connection = sqlite3.connect(self.student_database)
        cursor = connection.cursor()
        cursor.execute("SELECT StudentID FROM students WHERE CourseCode=?", (course_code,))
        student_ids = cursor.fetchall()
        connection.close()

        connection = sqlite3.connect(self.student_database)
        cursor = connection.cursor()
        for student_id in student_ids:
            cursor.execute("UPDATE students SET CourseCode='N/A' WHERE StudentID=?", student_id)
        connection.commit()
        connection.close()

        connection = sqlite3.connect(self.course_database)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM courses WHERE Code=?", (course_code,))
        connection.commit()
        connection.close()

        self.populate_course_table()
        self.populate_student_table()

        QMessageBox.information(self, 'Success', 'Course deleted successfully!')

    def update_course(self):
        course_code, ok1 = QInputDialog.getText(self, 'Course Code', 'Enter course code:')
        if not ok1:
            return

        connection = sqlite3.connect(self.course_database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM courses WHERE Code=?", (course_code,))
        course_data = cursor.fetchone()
        connection.close()

        if not course_data:
            QMessageBox.warning(self, 'Error', 'No course found with the provided code.')
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Update Course")

        layout = QVBoxLayout(dialog)

        course_name_input = QLineEdit()
        course_name_input.setText(course_data[0])
        course_name_input.setReadOnly(True)

        course_code_input = QLineEdit()
        course_code_input.setText(course_data[1])

        form_layout = QFormLayout()
        form_layout.addRow("Course Code:", course_code_input)
        form_layout.addRow("Course Name:", course_name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_course_code = course_code_input.text().strip()

            if not new_course_code:
                QMessageBox.warning(self, "Error", "Course code cannot be empty!")
                return

            if new_course_code != course_code:
                connection = sqlite3.connect(self.student_database)
                cursor = connection.cursor()
                cursor.execute("UPDATE students SET CourseCode=? WHERE CourseCode=?", (new_course_code, course_code))
                connection.commit()
                connection.close()

            connection = sqlite3.connect(self.course_database)
            cursor = connection.cursor()
            cursor.execute("UPDATE courses SET Code=? WHERE Code=?", (new_course_code, course_code))
            connection.commit()
            connection.close()

            QMessageBox.information(self, 'Success', 'Course updated successfully!')
            self.populate_course_table()

    def create_student_tab(self):
        student_tab = QWidget()
        student_tab_layout = QVBoxLayout(student_tab)

        title_label = QLabel("Students Management", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;"
            "background-color: maroon;"
            "border-radius: 20px;"
            "border:1px solid black;"
        )
        student_tab_layout.addWidget(title_label)

        button_layout = QHBoxLayout()

        add_student_btn = QPushButton("Add Student")
        add_student_btn.clicked.connect(self.add_student)
        add_student_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(add_student_btn)

        delete_student_btn = QPushButton("Delete Student")
        delete_student_btn.clicked.connect(self.delete_student)
        delete_student_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(delete_student_btn)

        update_student_btn = QPushButton("Update Student")
        update_student_btn.clicked.connect(self.update_student)
        update_student_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(update_student_btn)

        refresh_student_btn = QPushButton("Refresh")
        refresh_student_btn.clicked.connect(self.refresh_students)
        refresh_student_btn.setStyleSheet(
            "QPushButton {"
            "background-color: maroon;"
            "color: white;"
            "border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #510400;"
            "}"
        )
        button_layout.addWidget(refresh_student_btn)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by:", self)
        filter_layout.addWidget(filter_label)

        self.filter_input = QComboBox()
        self.filter_input.addItem("All")
        self.filter_input.addItems(self.student_fields[:-1])  # Excluding CourseCode
        self.filter_input.addItem("CourseCode")
        filter_layout.addWidget(self.filter_input)

        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Enter filter value")
        filter_layout.addWidget(self.filter_text)

        filter_button = QPushButton("Filter")
        filter_button.clicked.connect(self.filter_students)
        filter_layout.addWidget(filter_button)

        student_tab_layout.addLayout(button_layout)
        student_tab_layout.addLayout(filter_layout)

        self.student_table = QTableWidget()
        student_tab_layout.addWidget(self.student_table)

        self.tabs.addTab(student_tab, "Students")

    def refresh_students(self):
        self.populate_student_table()

    def filter_students(self):
        filter_text = self.filter_text.text().strip()
        if not filter_text:
            self.populate_student_table()
            return

        filter_field = self.filter_input.currentText()

        if filter_field == 'All':
            connection = sqlite3.connect(self.student_database)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM students WHERE StudentID LIKE ? OR StudentName LIKE ? OR Gender LIKE ? OR Year LIKE ? OR CourseCode LIKE ?",
                           ('%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%'))
            filtered_students = cursor.fetchall()
            connection.close()
        else:
            connection = sqlite3.connect(self.student_database)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM students WHERE {filter_field} LIKE ?", ('%' + filter_text + '%',))
            filtered_students = cursor.fetchall()
            connection.close()

        self.populate_student_table(filtered_students)

    def populate_student_table(self, data=None):
        connection = sqlite3.connect(self.student_database)
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS students (StudentID TEXT, StudentName TEXT, Gender TEXT, Year TEXT, CourseCode TEXT)")
        if data is None:
            cursor.execute("SELECT * FROM students")
            data = cursor.fetchall()

        self.student_table.clearContents()
        self.student_table.setRowCount(len(data))
        self.student_table.setColumnCount(len(self.student_fields))
        self.student_table.setHorizontalHeaderLabels(self.student_fields)
        for row_index, row_data in enumerate(data):
            for column_index, field in enumerate(self.student_fields):
                item = QTableWidgetItem(row_data[column_index])
                self.student_table.setItem(row_index, column_index, item)

        connection.close()

    def add_student(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Student")

        layout = QVBoxLayout(dialog)

        student_id_input = QLineEdit()
        student_name_input = QLineEdit()
        gender_input = QComboBox()
        gender_input.addItems(["Male", "Female", "Other"])
        year_input = QComboBox()
        year_input.addItems(["First", "Second", "Third", "Fourth"])
        course_code_input = QComboBox()
        course_codes = self.get_course_codes()
        course_code_input.addItems(course_codes)

        form_layout = QFormLayout()
        form_layout.addRow("Student ID:", student_id_input)
        form_layout.addRow("Student Name:", student_name_input)
        form_layout.addRow("Gender:", gender_input)
        form_layout.addRow("Year:", year_input)
        form_layout.addRow("Course Code:", course_code_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            student_id = student_id_input.text().strip()
            student_name = student_name_input.text().strip()
            gender = gender_input.currentText()
            year = year_input.currentText()
            course_code = course_code_input.currentText()

            # Check if the student ID already exists
            connection = sqlite3.connect(self.student_database)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM students WHERE StudentID=?", (student_id,))
            existing_student = cursor.fetchone()
            connection.close()

        if existing_student:
            QMessageBox.warning(self, "Warning", f"Student with ID {student_id} already exists!")
            return

        if not (student_id and student_name):
            QMessageBox.warning(self, "Error", "Both student ID and name are required!")
            return

        connection = sqlite3.connect(self.student_database)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS students (StudentID TEXT, StudentName TEXT, Gender TEXT, Year TEXT, CourseCode TEXT)")
        cursor.execute("INSERT INTO students (StudentID, StudentName, Gender, Year, CourseCode) VALUES (?, ?, ?, ?, ?)", (student_id, student_name, gender, year, course_code))
        connection.commit()
        connection.close()

        QMessageBox.information(self, 'Success', 'Student added successfully!')
        self.populate_student_table()

    def delete_student(self):
        row_index = self.student_table.currentRow()
        if row_index == -1:
            QMessageBox.warning(self, 'Error', 'Please select a student to delete.')
            return

        student_id = self.student_table.item(row_index, 0).text()

        connection = sqlite3.connect(self.student_database)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE StudentID=?", (student_id,))
        connection.commit()
        connection.close()

        QMessageBox.information(self, 'Success', 'Student deleted successfully!')
        self.populate_student_table()

    def update_student(self):
        row_index = self.student_table.currentRow()
        if row_index == -1:
            QMessageBox.warning(self, 'Error', 'Please select a student to update.')
            return

        student_id = self.student_table.item(row_index, 0).text()

        connection = sqlite3.connect(self.student_database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE StudentID=?", (student_id,))
        student_data = cursor.fetchone()
        connection.close()

        if not student_data:
            QMessageBox.warning(self, 'Error', 'No student found with the provided ID.')
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Update Student")

        layout = QVBoxLayout(dialog)

        student_name_input = QLineEdit()
        student_name_input.setText(student_data[1])
        student_id_input = QLineEdit()
        student_id_input.setText(student_data[0])
        student_id_input.setReadOnly(True)
        gender_input = QComboBox()
        gender_input.addItems(["Male", "Female", "Other"])
        gender_input.setCurrentText(student_data[2])
        year_input = QComboBox()
        year_input.addItems(["First", "Second", "Third", "Fourth"])
        year_input.setCurrentText(student_data[3])
        course_code_input = QComboBox()
        course_codes = self.get_course_codes()
        course_code_input.addItems(course_codes)
        course_code_input.setCurrentText(student_data[4])

        form_layout = QFormLayout()
        form_layout.addRow("Student ID:", student_id_input)
        form_layout.addRow("Student Name:", student_name_input)
        form_layout.addRow("Gender:", gender_input)
        form_layout.addRow("Year:", year_input)
        form_layout.addRow("Course Code:", course_code_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            student_name = student_name_input.text().strip()
            gender = gender_input.currentText()
            year = year_input.currentText()
            course_code = course_code_input.currentText()

            if not student_name:
                QMessageBox.warning(self, "Error", "Student name cannot be empty!")
                return

            connection = sqlite3.connect(self.student_database)
            cursor = connection.cursor()
            cursor.execute("UPDATE students SET StudentName=?, Gender=?, Year=?, CourseCode=? WHERE StudentID=?", (student_name, gender, year, course_code, student_id))
            connection.commit()
            connection.close()

            QMessageBox.information(self, 'Success', 'Student updated successfully!')
            self.populate_student_table()

    def get_course_codes(self):
        connection = sqlite3.connect(self.course_database)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS courses (Code TEXT, Name TEXT)")
        cursor.execute("SELECT Code FROM courses")
        course_codes = cursor.fetchall()
        connection.close()

        return [code[0] for code in course_codes]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
