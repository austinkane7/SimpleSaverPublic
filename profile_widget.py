from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout,
    QInputDialog, QMessageBox
)
from user_manager import UserManager
from data_manager import DataManager

class ProfileWidget(QWidget):
    def __init__(self, email, user_id, parent=None):
        super().__init__(parent)
        self.email = email
        self.user_id = user_id
        self.um = UserManager()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        formLayout = QFormLayout()

        self.emailEdit = QLineEdit(self.email)
        self.emailEdit.setReadOnly(True)
        self.firstNameEdit = QLineEdit()
        self.lastNameEdit = QLineEdit()

        formLayout.addRow("Email:", self.emailEdit)
        formLayout.addRow("First Name:", self.firstNameEdit)
        formLayout.addRow("Last Name:", self.lastNameEdit)

        updateProfileButton = QPushButton("Update Profile")
        updateProfileButton.clicked.connect(self.updateProfile)

        changePasswordButton = QPushButton("Change Password")
        changePasswordButton.clicked.connect(self.changePassword)

        logoutButton = QPushButton("Logout")
        logoutButton.clicked.connect(self.logout)

        layout.addLayout(formLayout)
        layout.addWidget(updateProfileButton)
        layout.addWidget(changePasswordButton)
        layout.addWidget(logoutButton)

        self.setLayout(layout)
        self.loadUserInfo()

    def loadUserInfo(self):
        user = self.um.get_user(self.email)
        if user:
            self.firstNameEdit.setText(user[2])
            self.lastNameEdit.setText(user[3])

    def updateProfile(self):
        first_name = self.firstNameEdit.text()
        last_name = self.lastNameEdit.text()
        if self.um.update_user_info(self.email, first_name, last_name):
            QMessageBox.information(self, "Profile Updated", "Profile information updated successfully.")
        else:
            QMessageBox.warning(self, "Update Failed", "Failed to update profile.")

    def changePassword(self):
        new_password, ok = QInputDialog.getText(self, "Change Password", "Enter new password:", QLineEdit.Password)
        if ok and new_password:
            first_name = self.firstNameEdit.text()
            last_name = self.lastNameEdit.text()
            if self.um.update_user_info(self.email, first_name, last_name, new_password):
                QMessageBox.information(self, "Password Updated", "Password changed successfully.")
            else:
                QMessageBox.warning(self, "Update Failed", "Failed to change password.")

    def logout(self):
        self.window().switchToLogin()

