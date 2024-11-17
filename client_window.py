from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QTextEdit,QApplication
)
from PyQt6.QtGui import QAction
import sqlite3
import sys


class WindowForClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно клиента")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.result_text_edit = QTextEdit()
        layout.addWidget(self.result_text_edit)

        book_table_button = QPushButton('Забронировать столик')
        book_table_button.clicked.connect(self.book_table_result)
        layout.addWidget(book_table_button)

        make_order = QPushButton('Сделать заказ')
        make_order.clicked.connect(self.order_maker)
        layout.addWidget(make_order)

        central_widget.setLayout(layout)

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

    def book_table_result(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Бронирование столика')

        layout = QVBoxLayout(dialog)

        info_label = QLabel("Свободные столики:")
        layout.addWidget(info_label)

        table_widget = QTableWidget()
        layout.addWidget(table_widget)

        check_button = QPushButton('Показать свободные столики')
        check_button.clicked.connect(lambda: self.display_available_tables(table_widget))
        layout.addWidget(check_button)

        close_button = QPushButton('Закрыть')
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

    def display_available_tables(self, table_widget):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = """
                SELECT Table_num, Capacity
                FROM Tables
                WHERE Table_ID NOT IN (
                    SELECT Table_ID
                    FROM Reservations
                    WHERE strftime('%Y-%m-%d', Date) = Date('now')
                );
            """
            cursor.execute(query)
            available_tables = cursor.fetchall()

            # Устанавливаем количество строк и столбцов в QTableWidget
            table_widget.setRowCount(len(available_tables))
            table_widget.setColumnCount(2)
            table_widget.setHorizontalHeaderLabels(["Номер стола", "Вместимость"])

            # Заполняем таблицу данными
            for row_index, table in enumerate(available_tables):
                table_widget.setItem(row_index, 0, QTableWidgetItem(str(table[0])))
                table_widget.setItem(row_index, 1, QTableWidgetItem(str(table[1])))

            if not available_tables:
                QMessageBox.information(table_widget, "Информация", "На сегодня свободных столиков нет.")
        except sqlite3.Error as e:
            QMessageBox.critical(table_widget, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(table_widget, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    def order_maker(self):
        pass
