from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QDialog, QDateEdit, QTableWidget,
    QTableWidgetItem, QTextEdit, QApplication, QInputDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QDate
import sqlite3
import sys


class WindowForClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_order = []
        self.setWindowTitle("Окно клиента")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Количество", "Название", "Цена", "Итого"])
        layout.addWidget(self.result_table)

        book_table_button = QPushButton('Забронировать столик')
        book_table_button.clicked.connect(self.book_table_result)
        layout.addWidget(book_table_button)

        make_order = QPushButton('Сделать заказ')
        make_order.clicked.connect(self.order_maker)
        layout.addWidget(make_order)

        shopping_cart = QPushButton('Моя корзина')
        shopping_cart.clicked.connect(self.show_shopping_cart)
        layout.addWidget(shopping_cart)

        edit_shopping_cart = QPushButton('Редактировать корзину')
        edit_shopping_cart.clicked.connect(self.edit_shop_crt)
        layout.addWidget(edit_shopping_cart)

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
        book_table.clicked.connect(
            lambda: self.get_table_reservation(date_edit.date(), table_widget))  # Передаем дату и таблицу
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
        dialog = QDialog(self)
        dialog.setWindowTitle('Сделать заказ')

        layout = QVBoxLayout(dialog)
        info_label = QLabel("Просмотр меню ресторана:")
        layout.addWidget(info_label)

        menu_table = QTableWidget()
        layout.addWidget(menu_table)

        category_button = QPushButton("Выбрать категорию")
        category_button.clicked.connect(lambda: self.display_menu_by_category(menu_table))
        layout.addWidget(category_button)

        add_button = QPushButton("Добавить в заказ")
        add_button.clicked.connect(lambda: self.add_menu_item_to_order(menu_table))
        layout.addWidget(add_button)

        complete_button = QPushButton("Завершить заказ")
        complete_button.clicked.connect(lambda: self.complete_order(dialog))
        layout.addWidget(complete_button)

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

    def add_menu_item_to_order(self, menu_table):
        try:
            selected_row = menu_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите блюдо для добавления в заказ.")
                return

            menu_item_id = int(menu_table.item(selected_row, 0).text())
            menu_item_name = menu_table.item(selected_row, 1).text()
            menu_item_price = float(menu_table.item(selected_row, 3).text())

            quantity, ok = QInputDialog.getInt(self, "Количество", f"Введите количество для блюда '{menu_item_name}':",
                                               1, 1)
            if not ok:
                return

            # Добавляем в текущий заказ
            self.current_order.append({
                "MenuItem_ID": menu_item_id,
                "Name": menu_item_name,
                "Quantity": quantity,
                "Price": menu_item_price
            })

            QMessageBox.information(self, "Успех", f"Блюдо '{menu_item_name}' (x{quantity}) добавлено в заказ.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")

    def complete_order(self, dialog):
        if not self.current_order:
            QMessageBox.warning(self, "Ошибка", "Заказ пуст. Добавьте блюда перед завершением.")
            return

        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Вставляем новый заказ в таблицу Orders
            cursor.execute("""
                INSERT INTO Orders (Customer_ID, Employee_ID, Order_date, Total_Amount, Order_status)
                VALUES (?, ?, datetime('now'), ?, 'Pending')
            """, (1, None, sum(item['Price'] * item['Quantity'] for item in self.current_order)))
            order_id = cursor.lastrowid

            # Вставляем позиции заказа в таблицу OrderItems
            for item in self.current_order:
                cursor.execute("""
                    INSERT INTO OrderItems (Order_ID, MenuItem_ID, Quantity, Price)
                    VALUES (?, ?, ?, ?)
                """, (order_id, item['MenuItem_ID'], item['Quantity'], item['Price']))

            connection.commit()

            QMessageBox.information(self, "Успех", "Заказ успешно сохранен!")
            self.current_order = []  # Очищаем временный заказ
            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    def show_shopping_cart(self):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Замените на реальный ID текущего клиента
            current_customer_id = 1

            # Получение последнего заказа текущего клиента со статусом "Pending"
            cursor.execute("""
                SELECT Order_ID, Total_Amount, Order_date 
                FROM Orders
                WHERE Customer_ID = ? AND Order_status = 'Pending'
                ORDER BY Order_date DESC LIMIT 1
            """, (current_customer_id,))
            order = cursor.fetchone()

            if not order:
                QMessageBox.information(self, "Корзина пуста", "На данный момент в корзине ничего нет.")
                self.result_table.setRowCount(0)
                return

            order_id, total_amount, order_date = order

            # Получение позиций заказа
            cursor.execute("""
                SELECT oi.Quantity, mi.Name, oi.Price, (oi.Quantity * oi.Price) as TotalPrice
                FROM OrderItems oi
                JOIN MenuItems mi ON oi.MenuItem_ID = mi.MenuItem_ID
                WHERE oi.Order_ID = ?
            """, (order_id,))
            order_items = cursor.fetchall()

            # Заполняем таблицу
            self.result_table.setRowCount(len(order_items))
            for row_index, (quantity, name, price, total_price) in enumerate(order_items):
                self.result_table.setItem(row_index, 0, QTableWidgetItem(str(quantity)))
                self.result_table.setItem(row_index, 1, QTableWidgetItem(name))
                self.result_table.setItem(row_index, 2, QTableWidgetItem(f"{price:.2f}"))
                self.result_table.setItem(row_index, 3, QTableWidgetItem(f"{total_price:.2f}"))

            # Добавляем строку с общей суммой заказа
            self.result_table.setRowCount(len(order_items) + 1)
            self.result_table.setItem(len(order_items), 0, QTableWidgetItem("Общая сумма:"))
            self.result_table.setItem(len(order_items), 1, QTableWidgetItem(""))
            self.result_table.setItem(len(order_items), 2, QTableWidgetItem(""))
            self.result_table.setItem(len(order_items), 3, QTableWidgetItem(f"{total_amount:.2f}"))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    def edit_shop_crt(self):
        pass