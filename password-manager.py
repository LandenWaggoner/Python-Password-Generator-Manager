import sys
import random
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox, QInputDialog, QLabel, QSlider, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QClipboard

# Password generation options
OPTIONS = {
    "uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "lowercase": "abcdefghijklmnopqrstuvwxyz",
    "numbers": "0123456789",
    "special": "!@#$%^&*()-_=+[]{}|;:,.<>?/"
}

# File to store passwords
PASSWORD_FILE = "passwords.json"

class PasswordManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager and Generator")
        self.setGeometry(100, 100, 800, 600)
        
        # Set the window icon
        self.setWindowIcon(QIcon("icon.png"))
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.generator_tab = QWidget()
        self.saved_passwords_tab = QWidget()
        
        self.tabs.addTab(self.generator_tab, "Password Generator")
        self.tabs.addTab(self.saved_passwords_tab, "Saved Passwords")
        
        self.create_generator_tab()
        self.create_saved_passwords_tab()
        
        self.load_passwords()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440;
                color: #D8DEE9;
            }
            QTabWidget::pane {
                border: 1px solid #4C566A;
            }
            QTabBar::tab {
                background: #4C566A;
                color: #D8DEE9;
                padding: 10px;
                border: 1px solid #4C566A;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #5E81AC;
                border-color: #5E81AC;
            }
            QWidget {
                background-color: #3B4252;
                color: #D8DEE9;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit, QTableWidget, QCheckBox, QPushButton, QSlider {
                background-color: #4C566A;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                padding: 5px;
            }
            QPushButton {
                background-color: #5E81AC;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QTableWidget {
                gridline-color: #4C566A;
            }
        """)
        
    def create_generator_tab(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.username_entry = QLineEdit()
        self.website_entry = QLineEdit()
        form_layout.addRow("Username:", self.username_entry)
        form_layout.addRow("Website:", self.website_entry)
        
        self.uppercase_checkbox = QCheckBox("Include Uppercase Letters")
        self.numbers_checkbox = QCheckBox("Include Numbers")
        self.special_checkbox = QCheckBox("Include Special Characters")
        
        layout.addLayout(form_layout)
        layout.addWidget(self.uppercase_checkbox)
        layout.addWidget(self.numbers_checkbox)
        layout.addWidget(self.special_checkbox)
        
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(32)
        self.length_slider.setValue(12)
        self.length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.length_slider.setTickInterval(1)
        layout.addWidget(QLabel("Password Length:"))
        layout.addWidget(self.length_slider)
        
        self.generate_button = QPushButton("Generate Password")
        self.generate_button.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_button)
        
        self.password_label = QLabel("")
        self.password_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.password_label)
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)
        
        self.strength_label = QLabel("")
        layout.addWidget(self.strength_label)
        
        self.generator_tab.setLayout(layout)
        
    def create_saved_passwords_tab(self):
        layout = QVBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_passwords)
        layout.addWidget(self.search_bar)
        
        self.password_table = QTableWidget()
        self.password_table.setColumnCount(3)
        self.password_table.setHorizontalHeaderLabels(["Username", "Website", "Password"])
        layout.addWidget(self.password_table)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.edit_button = QPushButton("Edit Entry")
        self.edit_button.clicked.connect(self.edit_entry)
        self.delete_button = QPushButton("Delete Entry")
        self.delete_button.clicked.connect(self.delete_entry)
        self.export_button = QPushButton("Export Passwords")
        self.export_button.clicked.connect(self.export_passwords)
        self.import_button = QPushButton("Import Passwords")
        self.import_button.clicked.connect(self.import_passwords)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)
        
        layout.addLayout(button_layout)
        self.saved_passwords_tab.setLayout(layout)
        
    def generate_password(self):
        length = self.length_slider.value()
        characters = OPTIONS["lowercase"]
        if self.uppercase_checkbox.isChecked():
            characters += OPTIONS["uppercase"]
        if self.numbers_checkbox.isChecked():
            characters += OPTIONS["numbers"]
        if self.special_checkbox.isChecked():
            characters += OPTIONS["special"]
        
        password = ''.join(random.choice(characters) for _ in range(length))
        
        username = self.username_entry.text()
        website = self.website_entry.text()
        
        if username and website:
            self.save_password(username, website, password)
            self.password_label.setText(f"Generated Password: {password}")
            self.strength_label.setText(f"Password Strength: {self.calculate_strength(password)}")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter both username and website.")
        
    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password_label.text().replace("Generated Password: ", ""))
        QMessageBox.information(self, "Copied", "Password copied to clipboard.")
        
    def save_password(self, username, website, password):
        passwords = self.load_passwords()
        passwords.append({"username": username, "website": website, "password": password})
        with open(PASSWORD_FILE, "w") as file:
            json.dump(passwords, file)
        self.load_passwords()
        
    def load_passwords(self):
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, "r") as file:
                passwords = json.load(file)
        else:
            passwords = []
        
        self.password_table.setRowCount(0)
        for entry in passwords:
            row_position = self.password_table.rowCount()
            self.password_table.insertRow(row_position)
            self.password_table.setItem(row_position, 0, QTableWidgetItem(entry["username"]))
            self.password_table.setItem(row_position, 1, QTableWidgetItem(entry["website"]))
            self.password_table.setItem(row_position, 2, QTableWidgetItem(entry["password"]))
        
        return passwords
    
    def add_entry(self):
        username, ok1 = QInputDialog.getText(self, "Add Entry", "Username:")
        website, ok2 = QInputDialog.getText(self, "Add Entry", "Website:")
        password, ok3 = QInputDialog.getText(self, "Add Entry", "Password:")
        
        if ok1 and ok2 and ok3:
            self.save_password(username, website, password)
        
    def edit_entry(self):
        selected_row = self.password_table.currentRow()
        if selected_row >= 0:
            username = self.password_table.item(selected_row, 0).text()
            website = self.password_table.item(selected_row, 1).text()
            password = self.password_table.item(selected_row, 2).text()
            
            new_username, ok1 = QInputDialog.getText(self, "Edit Entry", "Username:", text=username)
            new_website, ok2 = QInputDialog.getText(self, "Edit Entry", "Website:", text=website)
            new_password, ok3 = QInputDialog.getText(self, "Edit Entry", "Password:", text=password)
            
            if ok1 and ok2 and ok3:
                passwords = self.load_passwords()
                passwords[selected_row] = {"username": new_username, "website": new_website, "password": new_password}
                with open(PASSWORD_FILE, "w") as file:
                    json.dump(passwords, file)
                self.load_passwords()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select an entry to edit.")
    
    def delete_entry(self):
        selected_row = self.password_table.currentRow()
        if selected_row >= 0:
            passwords = self.load_passwords()
            passwords.pop(selected_row)
            with open(PASSWORD_FILE, "w") as file:
                json.dump(passwords, file)
            self.load_passwords()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select an entry to delete.")
    
    def filter_passwords(self):
        search_text = self.search_bar.text().lower()
        for row in range(self.password_table.rowCount()):
            username = self.password_table.item(row, 0).text().lower()
            website = self.password_table.item(row, 1).text().lower()
            if search_text in username or search_text in website:
                self.password_table.showRow(row)
            else:
                self.password_table.hideRow(row)
    
    def export_passwords(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Passwords", "", "JSON Files (*.json)")
        if file_name:
            passwords = self.load_passwords()
            with open(file_name, "w") as file:
                json.dump(passwords, file)
            QMessageBox.information(self, "Export Successful", "Passwords exported successfully.")
    
    def import_passwords(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Passwords", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, "r") as file:
                passwords = json.load(file)
            with open(PASSWORD_FILE, "w") as file:
                json.dump(passwords, file)
            self.load_passwords()
            QMessageBox.information(self, "Import Successful", "Passwords imported successfully.")
    
    def calculate_strength(self, password):
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in OPTIONS["special"] for c in password)
        
        strength = "Weak"
        if length >= 12 and has_upper and has_lower and has_digit and has_special:
            strength = "Strong"
        elif length >= 8 and ((has_upper and has_lower) or (has_digit and has_special)):
            strength = "Moderate"
        
        return strength

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManagerApp()
    window.show()
    sys.exit(app.exec())