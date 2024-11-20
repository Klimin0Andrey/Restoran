import sqlite3
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QTextEdit, QMainWindow, QMessageBox, QDialog, QPushButton, \
    QTableWidget, QTableWidgetItem, QInputDialog
from PyQt6.QtGui import QAction


# Окно Сотрудника
class WindowForEmployee(QMainWindow):
    def __init__(self, employee_id, parent=None):
        super().__init__()
        self.parent = parent
        self.employee_id = employee_id
        self.setWindowTitle("Окно сотрудника")
        self.setGeometry(360, 150, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Основные виджеты
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
        # Меню для окна сотрудника
        menubar = self.menuBar()

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

    # Функция смены пользователя
    def change_user(self):
        """Смена пользователя."""
        self.close()  # Закрываем текущее окно
        if self.parent:
            self.parent.reset()  # Очищаем поля ввода в окне авторизации
            self.parent.show()  # Показываем окно авторизации
        else:
            QMessageBox.warning(self, "Ошибка", "Окно авторизации недоступно.")

    # Функционал кнопки "Меню ресторана"
    def show_menu(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Меню ресторана')
        dialog.setGeometry(485, 220, 550, 400)

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

    # Функция отображения пунктов меню
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

            menu_table.setColumnWidth(0, 40)  # ID
            menu_table.setColumnWidth(1, 215)  # Название
            menu_table.setColumnWidth(2, 150)  # Описание
            menu_table.setColumnWidth(3, 80)  # Цена

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
            dialog.setGeometry(520, 210, 480, 400)
            layout = QVBoxLayout(dialog)

            table_widget = QTableWidget()
            table_widget.setRowCount(len(orders))
            table_widget.setColumnCount(4)
            table_widget.setHorizontalHeaderLabels(["ID заказа", "ID клиента", "Общая сумма", "Дата заказа"])
            table_widget.setColumnWidth(0, 100)  # ID
            table_widget.setColumnWidth(1, 100)  # Название
            table_widget.setColumnWidth(2, 100)  # Описание
            table_widget.setColumnWidth(3, 130)  # Цена

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

    # Функция позволяет сотруднику выбрать заказ из списка и закрепить его за собой
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

            # Проверяем, что заказ все еще доступен
            cursor.execute("""
                SELECT Employee_ID
                FROM Orders
                WHERE Order_ID = ?
            """, (order_id,))
            result = cursor.fetchone()

            if result is None:
                QMessageBox.warning(self, "Ошибка", "Выбранный заказ не существует.")
                return
            elif result[0] is not None:
                QMessageBox.warning(self, "Ошибка", "Этот заказ уже принят другим сотрудником.")
                return

            # Назначаем заказ текущему сотруднику
            cursor.execute("""
                UPDATE Orders
                SET Employee_ID = ?
                WHERE Order_ID = ?
            """, (employee_id, order_id))
            connection.commit()

            QMessageBox.information(self, "Успех", f"Заказ {order_id} успешно принят.")
            self.refresh_orders(table_widget)  # Обновляем таблицу заказов
            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    # Функция обновления заказов
    def refresh_orders(self, table_widget):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Получаем список заказов без назначенного сотрудника
            cursor.execute("""
                SELECT Order_ID, Customer_ID, Total_Amount, Order_date
                FROM Orders
                WHERE Employee_ID IS NULL
            """)
            orders = cursor.fetchall()

            # Обновляем таблицу заказов
            table_widget.setRowCount(len(orders))
            for row_index, (order_id, customer_id, total_amount, order_date) in enumerate(orders):
                table_widget.setItem(row_index, 0, QTableWidgetItem(str(order_id)))
                table_widget.setItem(row_index, 1, QTableWidgetItem(str(customer_id)))
                table_widget.setItem(row_index, 2, QTableWidgetItem(f"{total_amount:.2f}"))
                table_widget.setItem(row_index, 3, QTableWidgetItem(order_date))

            if not orders:
                QMessageBox.information(self, "Нет доступных заказов", "Все заказы уже приняты.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    # Функция для смены статуса заказа
    def change_status(self):
        try:
            # Подключение к базе данных
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Получение списка заказов, которые приняты текущим сотрудником
            cursor.execute("""
                SELECT Order_ID, Customer_ID, Total_Amount, Order_status, Order_date
                FROM Orders
                WHERE Employee_ID = ?
            """, (self.employee_id,))
            orders = cursor.fetchall()

            if not orders:
                QMessageBox.information(self, "Нет заказов", "У вас нет принятых заказов для изменения статуса.")
                return

            # Создаем диалог для выбора заказа
            dialog = QDialog(self)
            dialog.setWindowTitle("Изменить статус заказа")
            dialog.setGeometry(495, 280, 530, 300)
            layout = QVBoxLayout(dialog)

            table_widget = QTableWidget()
            table_widget.setRowCount(len(orders))
            table_widget.setColumnCount(5)
            table_widget.setHorizontalHeaderLabels(["ID заказа", "ID клиента", "Общая сумма", "Статус", "Дата заказа"])
            table_widget.setColumnWidth(0, 80)
            table_widget.setColumnWidth(1, 80)
            table_widget.setColumnWidth(4, 120)
            layout.addWidget(table_widget)

            # Заполнение таблицы принятых заказов
            for row_index, (order_id, customer_id, total_amount, order_status, order_date) in enumerate(orders):
                table_widget.setItem(row_index, 0, QTableWidgetItem(str(order_id)))
                table_widget.setItem(row_index, 1, QTableWidgetItem(str(customer_id)))
                table_widget.setItem(row_index, 2, QTableWidgetItem(f"{total_amount:.2f}"))
                table_widget.setItem(row_index, 3, QTableWidgetItem(order_status))
                table_widget.setItem(row_index, 4, QTableWidgetItem(order_date))

            # Кнопка для изменения статуса
            change_status_button = QPushButton("Изменить статус")
            change_status_button.clicked.connect(lambda: self.update_order_status(table_widget))
            layout.addWidget(change_status_button)

            # Кнопка для закрытия
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

    # Функция обновления статуса заказа
    def update_order_status(self, table_widget):
        try:
            selected_row = table_widget.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите заказ для изменения статуса.")
                return

            # Получаем ID выбранного заказа
            order_id = int(table_widget.item(selected_row, 0).text())

            # Получаем текущий статус
            current_status = table_widget.item(selected_row, 3).text()

            # Список доступных статусов
            status_options = ["Pending", "In Progress", "Completed", "Cancelled"]

            if current_status not in status_options:
                QMessageBox.warning(self, "Ошибка", "Неизвестный статус заказа.")
                return

            # Убираем текущий статус из доступных для выбора
            status_options.remove(current_status)

            # Диалог для выбора нового статуса
            new_status, ok = QInputDialog.getItem(
                self, "Изменить статус заказа", "Выберите новый статус:", status_options, editable=False
            )
            if not ok:  # Если пользователь закрыл диалог или передумал менять статус
                QMessageBox.information(self, "Отмена", "Изменение статуса заказа отменено.")
                return

            # Подключение к базе данных
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Обновляем статус заказа в базе данных
            cursor.execute("""
                UPDATE Orders
                SET Order_status = ?
                WHERE Order_ID = ? AND Employee_ID = ?
            """, (new_status, order_id, self.employee_id))
            connection.commit()

            QMessageBox.information(self, "Успех", f"Статус заказа {order_id} успешно изменен на '{new_status}'.")

            # Обновляем таблицу в диалоге
            table_widget.setItem(selected_row, 3, QTableWidgetItem(new_status))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    # Функция для выбора и отображения счётв для авторизованного сотрудника
    def issue_an_bill(self):
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Получаем список всех заказов с их статусами и ID
            cursor.execute("""
                SELECT Order_ID, Customer_ID, Total_Amount, Order_status
                FROM Orders
                WHERE Employee_ID = ? AND Order_status != 'Completed'
            """, (self.employee_id,))
            orders = cursor.fetchall()

            if not orders:
                QMessageBox.information(self, "Нет заказов", "Нет доступных заказов для отображения счета.")
                return

            # Создаем диалог для выбора заказа
            dialog = QDialog(self)
            dialog.setWindowTitle("Выбрать заказ для счета")
            dialog.setGeometry(535, 290, 460, 300)
            layout = QVBoxLayout(dialog)

            table_widget = QTableWidget()
            table_widget.setRowCount(len(orders))
            table_widget.setColumnCount(4)
            table_widget.setHorizontalHeaderLabels(["ID заказа", "ID клиента", "Общая сумма", "Статус заказа"])
            layout.addWidget(table_widget)

            # Заполняем таблицу заказов
            for row_index, (order_id, customer_id, total_amount, status) in enumerate(orders):
                table_widget.setItem(row_index, 0, QTableWidgetItem(str(order_id)))
                table_widget.setItem(row_index, 1, QTableWidgetItem(str(customer_id)))
                table_widget.setItem(row_index, 2, QTableWidgetItem(f"{total_amount:.2f} руб."))
                table_widget.setItem(row_index, 3, QTableWidgetItem(status))

            # Кнопка для подтверждения выбора
            select_button = QPushButton("Показать счёт")
            select_button.clicked.connect(lambda: self.show_order_bill(table_widget, dialog))
            layout.addWidget(select_button)

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

    # Функция отображает счёт для выбранного заказа.
    def show_order_bill(self, table_widget, dialog):
        try:
            selected_row = table_widget.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите заказ для отображения счета.")
                return

            # Получаем ID выбранного заказа и ID клиента
            order_id = int(table_widget.item(selected_row, 0).text())
            customer_id = int(table_widget.item(selected_row, 1).text())

            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            # Получаем информацию о клиенте
            cursor.execute("""
                SELECT First_name, Last_name
                FROM Customers
                WHERE Customer_ID = ?
            """, (customer_id,))
            customer = cursor.fetchone()

            if not customer:
                QMessageBox.warning(self, "Ошибка", "Информация о клиенте не найдена.")
                return

            first_name, last_name = customer

            # Получаем блюда заказа
            cursor.execute("""
                SELECT oi.OrderItem_ID, oi.Quantity, oi.Price, (oi.Quantity * oi.Price) as TotalPrice
                FROM OrderItems oi
                WHERE oi.Order_ID = ?
            """, (order_id,))
            order_items = cursor.fetchall()

            # Проверяем забронированные столы для клиента
            cursor.execute("""
                SELECT t.Table_num, t.Capacity, r.Date
                FROM Reservations r
                JOIN Tables t ON r.Table_ID = t.Table_ID
                WHERE r.Customer_ID = ?
            """, (customer_id,))
            reservations = cursor.fetchall()

            # Формируем текст для отображения
            bill_text = f"Клиент: {last_name} {first_name}\n\n"
            bill_text += f"ID заказа: {order_id}\n\n"

            if order_items:
                bill_text += "Блюда заказа:\n"
                for item_id, quantity, price, total in order_items:
                    bill_text += f" - ID: {item_id}, Количество: {quantity}, Цена: {price:.2f} руб., Итого: {total:.2f} руб.\n"
            else:
                bill_text += "Блюда заказа отсутствуют.\n"

            total_amount = sum(item[3] for item in order_items)
            bill_text += f"\nОбщая стоимость: {total_amount:.2f} руб.\n\n"

            if reservations:
                bill_text += "Забронированные столы:\n"
                for table_num, capacity, date in reservations:
                    bill_text += f" - Стол №{table_num}, Вместимость: {capacity}, Дата: {date}\n"
            else:
                bill_text += "Забронированных столов нет.\n"

            # Выводим текст в поле `self.result_table`
            self.result_table.clear()
            self.result_table.setText(bill_text)

            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
            print(f"SQLite Error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()
