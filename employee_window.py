import sqlite3
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMessageBox, QApplication, QDialog, QPushButton, QTableWidget, \
    QTableWidgetItem, QInputDialog
import sys


class WindowForEmployee(QMainWindow):
    def __init__(self, employee_id):
        super().__init__()
        self.employee_id = employee_id
        self.setWindowTitle("Окно сотрудника")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.result_table = QTextEdit()
        layout.addWidget(self.result_table)

        menu = QPushButton('Меню ресторана')
        menu.clicked.connect(self.show_menu)
        layout.addWidget(menu)

        accept_order = QPushButton('Принять заказ')
        accept_order.clicked.connect(self.accept_user_order)
        layout.addWidget(accept_order)

        change_order_status = QPushButton('Изменить статус заказа')
        change_order_status.clicked.connect(self.change_status)
        layout.addWidget(change_order_status)

        bill = QPushButton('Выставить счёт')
        bill.clicked.connect(self.issue_an_bill)
        layout.addWidget(bill)

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

    def show_menu(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Меню ресторана')
        dialog.setGeometry(220, 165, 600, 400)

        layout = QVBoxLayout(dialog)
        info_label = QLabel("Просмотр меню ресторана:")
        layout.addWidget(info_label)

        menu_table = QTableWidget()
        layout.addWidget(menu_table)

        category_button = QPushButton("Выбрать категорию")
        category_button.clicked.connect(lambda: self.display_menu_by_category(menu_table))
        layout.addWidget(category_button)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

    def display_menu_by_category(self, menu_table):
        try:
            # Подключаемся к базе данных
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Запрашиваем доступные категории
            cursor.execute("SELECT DISTINCT Category FROM MenuItems")
            categories = [row[0] for row in cursor.fetchall()]

            if not categories:
                QMessageBox.information(self, "Информация", "В меню нет доступных категорий.")
                return

            # Диалог для выбора категории
            category, ok = QInputDialog.getItem(self, "Выбор категории", "Выберите категорию:", categories,
                                                editable=False)
            if not ok:
                return

            # Запрашиваем блюда выбранной категории
            query = "SELECT MenuItem_ID, Name, Description, Price FROM MenuItems WHERE Category = ?"
            cursor.execute(query, (category,))
            menu_items = cursor.fetchall()

            # Настраиваем таблицу
            menu_table.setRowCount(len(menu_items))
            menu_table.setColumnCount(4)
            menu_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Цена"])
            menu_table.setColumnWidth(1, 220)  # Устанавливаем ширину столбца "Название" (индекс 1) в 200 пикселей
            menu_table.setColumnWidth(2, 150)  # Устанавливаем ширину столбца "Название" (индекс 1) в 200 пикселей

            for row_index, item in enumerate(menu_items):
                for col_index, value in enumerate(item):
                    menu_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    def accept_user_order(self):
        try:
            # Подключение к базе данных
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Выбор заказов без назначенного сотрудника
            cursor.execute("""
                SELECT Order_ID, Customer_ID, Total_Amount, Order_date
                FROM Orders
                WHERE Employee_ID IS NULL
            """)
            orders = cursor.fetchall()

            if not orders:
                QMessageBox.information(self, "Нет доступных заказов", "Все заказы уже приняты.")
                return

            # Создаем диалог для выбора заказа
            dialog = QDialog(self)
            dialog.setWindowTitle("Принять заказ")
            layout = QVBoxLayout(dialog)

            table_widget = QTableWidget()
            table_widget.setRowCount(len(orders))
            table_widget.setColumnCount(4)
            table_widget.setHorizontalHeaderLabels(["ID заказа", "ID клиента", "Общая сумма", "Дата заказа"])
            layout.addWidget(table_widget)

            # Заполнение таблицы доступных заказов
            for row_index, (order_id, customer_id, total_amount, order_date) in enumerate(orders):
                table_widget.setItem(row_index, 0, QTableWidgetItem(str(order_id)))
                table_widget.setItem(row_index, 1, QTableWidgetItem(str(customer_id)))
                table_widget.setItem(row_index, 2, QTableWidgetItem(f"{total_amount:.2f}"))
                table_widget.setItem(row_index, 3, QTableWidgetItem(order_date))

            accept_button = QPushButton("Принять выбранный заказ")
            accept_button.clicked.connect(lambda: self.assign_order_to_employee(table_widget, dialog))
            layout.addWidget(accept_button)

            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def assign_order_to_employee(self, table_widget, dialog):
        try:
            selected_row = table_widget.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите заказ для принятия.")
                return

            # Получаем ID выбранного заказа
            order_id = int(table_widget.item(selected_row, 0).text())

            # Используем ID текущего авторизованного сотрудника
            employee_id = self.employee_id

            # Подключение к базе данных
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Назначаем заказ текущему сотруднику
            cursor.execute("""
                UPDATE Orders
                SET Employee_ID = ?
                WHERE Order_ID = ?
            """, (employee_id, order_id))
            connection.commit()

            QMessageBox.information(self, "Успех", f"Заказ {order_id} успешно принят.")
            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def change_status(self):
        pass

    def issue_an_bill(self):
        pass
