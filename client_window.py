from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QDialog, QDateEdit, QTableWidget, QTableWidgetItem, QTextEdit, QApplication, QInputDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QDate
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
        dialog.setWindowTitle('Просмотр свободных столиков')

        layout = QVBoxLayout(dialog)

        info_label = QLabel("Выберите дату для просмотра свободных столиков:")
        layout.addWidget(info_label)

        # Добавляем QDateEdit для выбора даты
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        layout.addWidget(date_edit)

        table_widget = QTableWidget()
        layout.addWidget(table_widget)

        check_button = QPushButton('Показать свободные столики')
        book_table = QPushButton('Забронировать столик')
        book_table.clicked.connect(lambda: self.get_table_reservation(date_edit.date(), table_widget))  # Передаем дату и таблицу
        check_button.clicked.connect(lambda: self.display_available_tables(date_edit.date(), table_widget))
        layout.addWidget(check_button)
        layout.addWidget(book_table)

        close_button = QPushButton('Закрыть')
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

    def display_available_tables(self, selected_date, table_widget):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Преобразуем дату в строку формата 'YYYY-MM-DD'
            date_str = selected_date.toString("yyyy-MM-dd")

            # Запрос для поиска свободных столов на указанную дату
            query = """
                SELECT t.Table_num, t.Capacity, t.Table_ID
                FROM Tables t
                WHERE t.Table_ID NOT IN (
                    SELECT r.Table_ID
                    FROM Reservations r
                    WHERE strftime('%Y-%m-%d', r.Date) = ?
                );
            """
            cursor.execute(query, (date_str,))
            available_tables = cursor.fetchall()

            # Устанавливаем количество строк и столбцов в QTableWidget
            table_widget.setRowCount(len(available_tables))
            table_widget.setColumnCount(3)
            table_widget.setHorizontalHeaderLabels(["Номер стола", "Вместимость", "ID стола"])

            # Заполняем таблицу данными
            for row_index, table in enumerate(available_tables):
                table_widget.setItem(row_index, 0, QTableWidgetItem(str(table[0])))
                table_widget.setItem(row_index, 1, QTableWidgetItem(str(table[1])))
                table_widget.setItem(row_index, 2, QTableWidgetItem(str(table[2])))

            if not available_tables:
                QMessageBox.information(table_widget, "Информация", f"На дату {date_str} свободных столиков нет.")
        except sqlite3.Error as e:
            QMessageBox.critical(table_widget, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(table_widget, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    def get_table_reservation(self, selected_date, table_widget):
        try:
            selected_row = table_widget.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите столик для бронирования.")
                return

            table_id = table_widget.item(selected_row, 2).text()  # Используем ID стола
            date_str = selected_date.toString("yyyy-MM-dd")

            # Подключаемся к базе данных
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Запрашиваем количество людей (можно добавить отдельный ввод)
            num_people, ok = QInputDialog.getInt(self, "Количество людей", "Введите количество людей:")
            if not ok or num_people <= 0:
                QMessageBox.warning(self, "Ошибка", "Введите корректное количество людей.")
                return

            # Вставляем запись о бронировании
            cursor.execute("""
                INSERT INTO Reservations (Customer_ID, Table_ID, Date, Amount_people)
                VALUES (?, ?, ?, ?)
            """, (1, table_id, date_str, num_people))  # Здесь "1" - это ID клиента, вы можете его получить из сессии

            connection.commit()
            QMessageBox.information(self, "Успех", f"Столик №{table_id} успешно забронирован на {date_str}.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def order_maker(self):
        pass
