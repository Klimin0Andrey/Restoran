from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QDialog, QDateEdit, QTableWidget,
    QTableWidgetItem, QTextEdit, QInputDialog, QApplication
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QDate
import sqlite3


# Окно Клиента
class WindowForClient(QMainWindow):
    def __init__(self, user_id, parent=None):
        super().__init__()
        self.parent = parent
        self.user_id = user_id  # Сохраняем текущего пользователя
        self.current_order = []
        self.setWindowTitle("Окно клиента")
        self.setGeometry(360, 150, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Основные виджеты
        layout = QVBoxLayout()

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Количество", "Название", "Цена за единицу, руб.", "Итого, руб."])
        self.result_table.setColumnWidth(0, 80)  # Количество
        self.result_table.setColumnWidth(1, 250)  # Название
        self.result_table.setColumnWidth(2, 150)  # Цена за единицу, руб.
        self.result_table.setColumnWidth(3, 100)  # Итого, руб.
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

        bill = QPushButton('Счёт заказа')
        bill.clicked.connect(self.bill_info)
        layout.addWidget(bill)

        central_widget.setLayout(layout)

        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        change_user_action = QAction('Сменить пользователя', self)
        change_user_action.triggered.connect(self.change_user)
        file_menu.addAction(change_user_action)

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "О программе"
        about_menu = menubar.addMenu('О программе')
        about_action = QAction('О приложении', self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)

    def show_about_dialog(self):
        QMessageBox.information(self, "О программе", "Система управления заказами в ресторане.\nВерсия: 1.0")

    def change_user(self):
        """Смена пользователя."""
        self.close()  # Закрываем текущее окно
        if self.parent:
            self.parent.reset()  # Очищаем поля ввода в окне авторизации
            self.parent.show()  # Показываем окно авторизации
        else:
            QMessageBox.warning(self, "Ошибка", "Окно авторизации недоступно.")

    def book_table_result(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Просмотр свободных столиков')
        dialog.setGeometry(578, 230, 365, 400)

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

    # Функция показывает свободные столики
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

            # Запрашиваем количество людей
            num_people, ok = QInputDialog.getInt(self, "Количество людей", "Введите количество людей:")
            if not ok or num_people <= 0:
                QMessageBox.warning(self, "Ошибка", "Введите корректное количество людей.")
                return

            # Вставляем запись о бронировании
            cursor.execute("""
                INSERT INTO Reservations (Customer_ID, Table_ID, Date, Amount_people)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, table_id, date_str, num_people))

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

    # Функция реализует кнопку "Сделать зказ"
    def order_maker(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Сделать заказ')
        dialog.setGeometry(485, 230, 550, 400)

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

    # Функция показывает меню ресторана по категориям
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
            menu_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Цена, руб."])

            menu_table.setColumnWidth(0, 40)  # ID
            menu_table.setColumnWidth(1, 215)  # Название
            menu_table.setColumnWidth(2, 150)  # Описание
            menu_table.setColumnWidth(3, 80)  # Цена

            for row_index, item in enumerate(menu_items):
                for col_index, value in enumerate(item):
                    if col_index == 3:  # Столбец "Цена"
                        formatted_value = f"{float(value):.2f}"  # Форматируем значение как число с плавающей точкой
                        menu_table.setItem(row_index, col_index, QTableWidgetItem(formatted_value))
                    else:
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

    # Функция добавления блюд в заказ
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
            """, (self.user_id, None, sum(item['Price'] * item['Quantity'] for item in self.current_order)))

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
        """Показывает текущую корзину для авторизованного пользователя."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Получение последнего заказа текущего клиента со статусом "Pending"
            cursor.execute("""
                SELECT Order_ID, Total_Amount, Order_date 
                FROM Orders
                WHERE Customer_ID = ? AND Order_status = 'Pending'
                ORDER BY Order_date DESC LIMIT 1
            """, (self.user_id,))
            order = cursor.fetchone()

            if not order:
                QMessageBox.information(self, "Корзина пуста", "На данный момент в корзине ничего нет.")
                self.result_table.setRowCount(0)  # Очистка таблицы
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

            # Заполнение таблицы
            self.result_table.setRowCount(len(order_items))
            for row_index, (quantity, name, price, total_price) in enumerate(order_items):
                self.result_table.setItem(row_index, 0, QTableWidgetItem(str(quantity)))
                self.result_table.setItem(row_index, 1, QTableWidgetItem(name))
                self.result_table.setItem(row_index, 2, QTableWidgetItem(f"{price:.2f}"))
                self.result_table.setItem(row_index, 3, QTableWidgetItem(f"{total_price:.2f}"))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    # Функция редактирования Корзины пользователя
    def edit_shop_crt(self):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            current_customer_id = self.user_id

            # Получение последнего заказа текущего клиента со статусом "Pending"
            cursor.execute("""
                SELECT Order_ID
                FROM Orders
                WHERE Customer_ID = ? AND Order_status = 'Pending'
                ORDER BY Order_date DESC LIMIT 1
            """, (self.user_id,))
            order = cursor.fetchone()

            if not order:
                QMessageBox.information(self, "Корзина пуста", "На данный момент в корзине ничего нет.")
                return

            order_id = order[0]

            # Получение позиций заказа
            cursor.execute("""
                SELECT oi.OrderItem_ID, mi.Name, oi.Quantity, oi.Price
                FROM OrderItems oi
                JOIN MenuItems mi ON oi.MenuItem_ID = mi.MenuItem_ID
                WHERE oi.Order_ID = ?
            """, (order_id,))
            order_items = cursor.fetchall()

            if not order_items:
                QMessageBox.information(self, "Корзина пуста", "На данный момент в корзине ничего нет.")
                return

            # Создаем диалог для редактирования
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать корзину")
            dialog.setGeometry(507, 290, 510, 300)
            layout = QVBoxLayout(dialog)

            # Таблица для отображения корзины
            cart_table = QTableWidget()
            cart_table.setColumnCount(4)
            cart_table.setHorizontalHeaderLabels(["ID позиции", "Название", "Количество", "Цена за единицу, руб."])
            cart_table.setColumnWidth(0, 80)  # ID позиции
            cart_table.setColumnWidth(1, 165)  # Название
            cart_table.setColumnWidth(2, 80)  # Количество
            cart_table.setColumnWidth(3, 130)  # Цена за единицу, руб.
            cart_table.setRowCount(len(order_items))

            # Заполняем таблицу
            for row_index, (item_id, name, qty, price) in enumerate(order_items):
                cart_table.setItem(row_index, 0, QTableWidgetItem(str(item_id)))
                cart_table.setItem(row_index, 1, QTableWidgetItem(name))
                cart_table.setItem(row_index, 2, QTableWidgetItem(str(qty)))
                cart_table.setItem(row_index, 3, QTableWidgetItem(f"{price:.2f}"))

            layout.addWidget(cart_table)

            # Кнопка для удаления позиции
            remove_button = QPushButton("Удалить позицию")
            remove_button.clicked.connect(lambda: self.remove_cart_item(cart_table, order_id))
            layout.addWidget(remove_button)

            # Кнопка для сохранения изменений
            save_button = QPushButton("Сохранить изменения")
            save_button.clicked.connect(lambda: self.save_cart_changes(cart_table, order_id))
            layout.addWidget(save_button)

            # Кнопка для закрытия
            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    # Функция удаления позиции зказа из Корзины пользователя
    def remove_cart_item(self, cart_table, order_id):
        try:
            selected_row = cart_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите позицию для удаления.")
                return

            # Получаем ID позиции для удаления
            item_id = int(cart_table.item(selected_row, 0).text())

            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Удаляем выбранную позицию
            cursor.execute("DELETE FROM OrderItems WHERE OrderItem_ID = ?", (item_id,))

            # Проверяем, остались ли блюда в заказе
            cursor.execute("""
                SELECT COUNT(*)
                FROM OrderItems
                WHERE Order_ID = ?
            """, (order_id,))
            items_left = cursor.fetchone()[0]

            if items_left == 0:
                # Удаляем заказ, если больше нет блюд
                cursor.execute("DELETE FROM Orders WHERE Order_ID = ?", (order_id,))
                QMessageBox.information(self, "Успех", "Все блюда удалены. Заказ удалён.")
                cart_table.clearContents()
                cart_table.setRowCount(0)
            else:
                # Пересчитываем общую стоимость заказа
                cursor.execute("""
                    SELECT SUM(Quantity * Price) AS TotalAmount
                    FROM OrderItems
                    WHERE Order_ID = ?
                """, (order_id,))
                new_total = cursor.fetchone()[0] or 0  # Если нет оставшихся блюд, устанавливаем 0

                # Обновляем общую стоимость заказа в таблице Orders
                cursor.execute("""
                    UPDATE Orders
                    SET Total_Amount = ?
                    WHERE Order_ID = ?
                """, (new_total, order_id))

                QMessageBox.information(self, "Успех", "Позиция удалена.")
                self.update_cart_table(cart_table, order_id)  # Обновляем таблицу корзины

            connection.commit()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    # Сохранение Корзины пользователя
    def save_cart_changes(self, cart_table, order_id):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            for row in range(cart_table.rowCount()):
                item_id = int(cart_table.item(row, 0).text())
                new_qty = int(cart_table.item(row, 2).text())

                if new_qty <= 0:
                    QMessageBox.warning(self, "Ошибка", "Количество должно быть больше нуля.")
                    return

                cursor.execute("""
                    UPDATE OrderItems
                    SET Quantity = ?
                    WHERE OrderItem_ID = ?
                """, (new_qty, item_id))

            connection.commit()
            QMessageBox.information(self, "Успех", "Изменения сохранены.")
            self.show_shopping_cart()  # Обновляем отображение корзины

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    # Обновление Корзины пользователя
    def update_cart_table(self, cart_table, order_id):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Загружаем данные корзины из базы данных
            cursor.execute("""
                SELECT oi.OrderItem_ID, mi.Name, oi.Quantity, oi.Price
                FROM OrderItems oi
                JOIN MenuItems mi ON oi.MenuItem_ID = mi.MenuItem_ID
                WHERE oi.Order_ID = ?
            """, (order_id,))
            order_items = cursor.fetchall()

            # Очищаем таблицу
            cart_table.clearContents()

            if not order_items:  # Если корзина пуста
                QMessageBox.information(self, "Корзина пуста", "Все позиции удалены.")
                cart_table.setRowCount(0)
                return

            # Обновляем содержимое таблицы
            cart_table.setRowCount(len(order_items))
            for row_index, (item_id, name, qty, price) in enumerate(order_items):
                cart_table.setItem(row_index, 0, QTableWidgetItem(str(item_id)))
                cart_table.setItem(row_index, 1, QTableWidgetItem(name))
                cart_table.setItem(row_index, 2, QTableWidgetItem(str(qty)))
                cart_table.setItem(row_index, 3, QTableWidgetItem(f"{price:.2f}"))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()

    def bill_info(self):
        """Показывает и обновляет счёт текущего заказа для авторизованного клиента."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Получаем информацию о клиенте
            cursor.execute("""
                SELECT First_name, Last_name
                FROM Customers
                WHERE Customer_ID = ?
            """, (self.user_id,))
            customer = cursor.fetchone()

            if not customer:
                QMessageBox.warning(self, "Ошибка", "Информация о клиенте не найдена.")
                return

            first_name, last_name = customer

            # Получаем текущий заказ
            cursor.execute("""
                SELECT Order_ID, Total_Amount
                FROM Orders
                WHERE Customer_ID = ? AND Order_status = 'Pending'
                ORDER BY Order_date DESC LIMIT 1
            """, (self.user_id,))
            order = cursor.fetchone()

            if not order:
                QMessageBox.information(self, "Счёт заказа", "У вас нет активного заказа.")
                return

            order_id, total_amount = order

            # Проверяем блюда заказа
            cursor.execute("""
                SELECT oi.OrderItem_ID, oi.Quantity, oi.Price, (oi.Quantity * oi.Price) as TotalPrice
                FROM OrderItems oi
                WHERE oi.Order_ID = ?
            """, (order_id,))
            order_items = cursor.fetchall()

            # Если блюда в заказе отсутствуют, обновляем общую стоимость в базе данных
            if not order_items:
                total_amount = 0
                cursor.execute("""
                    UPDATE Orders
                    SET Total_Amount = ?
                    WHERE Order_ID = ?
                """, (total_amount, order_id))
                connection.commit()

            # Получаем информацию о забронированных столах
            cursor.execute("""
                SELECT t.Table_num, t.Capacity, r.Date
                FROM Reservations r
                JOIN Tables t ON r.Table_ID = t.Table_ID
                WHERE r.Customer_ID = ? AND strftime('%Y-%m-%d', r.Date) = strftime('%Y-%m-%d', datetime('now'))
            """, (self.user_id,))
            reservations = cursor.fetchall()

            # Формируем текст для отображения
            bill_text = f"Клиент: {last_name} {first_name}\n\n"

            if order_items:
                bill_text += "Блюда заказа:\n"
                for item_id, quantity, price, total in order_items:
                    bill_text += f" - ID: {item_id}, Количество: {quantity}, Цена: {price:.2f} руб., Итого: {total:.2f} руб.\n"
            else:
                bill_text += "Блюда заказа отсутствуют.\n"

            bill_text += f"\nОбщая стоимость: {total_amount:.2f} руб.\n\n"

            if reservations:
                bill_text += "Забронированные столы:\n"
                for table_num, capacity, date in reservations:
                    bill_text += f" - Стол №{table_num}, Вместимость: {capacity}, Дата: {date}\n"
            else:
                bill_text += "Забронированных столов нет.\n"

            # Отображаем текст в диалоговом окне
            dialog = QDialog(self)
            dialog.setWindowTitle("Счёт заказа")

            layout = QVBoxLayout(dialog)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setText(bill_text)
            layout.addWidget(text_edit)

            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            print(f"General Error: {e}")
        finally:
            if connection:
                connection.close()
