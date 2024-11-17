from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMessageBox, QApplication, QDialog
import sys


class WindowForEmployee(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно сотрудника")
        self.setGeometry(100, 100, 800, 600)

        menubar = self.menuBar()  # Меню-бар

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')  # Меню "Файл"

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        # Меню "О программе"
        about_menu = menubar.addMenu('О программе')
        about_action = QAction('О приложении', self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)

    def show_about_dialog(self):
        """Показывает сообщение 'О программе'."""
        QMessageBox.information(self, "О программе", "Система управления заказами в ресторане.\nВерсия: 1.0")
