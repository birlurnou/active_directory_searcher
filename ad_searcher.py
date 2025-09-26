from ldap3 import Server, Connection, ALL
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import sys
import os
import logging
from datetime import datetime

# function for connecting to AD
def ad_connect(domain, user_login, user_password, user_to_find):
    try:
        server = Server(domain, get_info=ALL)
        conn = Connection(
            server,
            user=f'{user_login}@{domain}',
            password=user_password,
            authentication='SIMPLE',
            auto_bind=True
        )
        if conn.bind():
            dcs = domain.split('.')
            conn.search(f'dc={dcs[0]},dc={dcs[1]},dc={dcs[2]}', f'(sAMAccountName={user_to_find})', attributes=['displayName'])
            result = ""
            for entry in conn.entries:
                display_name = entry.displayName.value
                result += f'{display_name}\n'
            if not conn.entries:
                result = 'User not found'
            conn.unbind()
            return result
        else:
            return f"Connection error: {conn.result}"
    except Exception as e:
        return f"Error: {str(e)}"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search for users")
        self.setGeometry(100, 100, 300, 100)
        self.setWindowIcon(QIcon('icon.ico'))

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Input field with 7 character limit
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter Global User ID")
        self.input_field.setMaxLength(7)
        layout.addWidget(self.input_field)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        layout.addWidget(self.search_button)

        # Field for outputting the result
        self.result_field = QTextEdit()
        self.result_field.setReadOnly(True)
        layout.addWidget(self.result_field)

        # Styles
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QTextEdit {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)

    def perform_search(self):
        user_to_find = self.input_field.text().strip()
        if not user_to_find:
            self.result_field.setText("Error: Enter user ID")
            return

        domain, user_login, user_password = 'domain.local', 'user_id', 'user_password'
        if not domain or not user_login or not user_password:
            self.result_field.setText("Error: Failed to read data")
            return

        result = ad_connect(domain, user_login, user_password, user_to_find)
        self.result_field.setText(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(app.font())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())