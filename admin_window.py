import sqlite3
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QDialog, QInputDialog, QLineEdit, \
    QHBoxLayout
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMessageBox, QApplication, QDialog, QPushButton, QTextEdit
import sys


class WindowForAdmin(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # Сохраняем ссылку на родительское окно
        self.setWindowTitle("Окно администратора")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.result_table = QTableWidget()
        layout.addWidget(self.result_table)

        users = QPushButton('Пользователи')
        users.clicked.connect(self.edit_user)
        layout.addWidget(users)

        menu = QPushButton('Меню')
        menu.clicked.connect(self.edit_menu)
        layout.addWidget(menu)

        orders = QPushButton('Просмотр заказов')
        orders.clicked.connect(self.view_orders)
        layout.addWidget(orders)

        reports = QPushButton('Отчеты и аналитика')
        reports.clicked.connect(self.reports_in_excel)
        layout.addWidget(reports)

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

    def edit_user(self):
        """Управление пользователями: создание и удаление профилей."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Управление пользователями")
            dialog.setGeometry(200, 150, 600, 400)

            layout = QVBoxLayout(dialog)

            # Выбор типа пользователя
            user_type_label = QLabel("Выберите тип пользователя:")
            layout.addWidget(user_type_label)

            user_type_buttons = QHBoxLayout()
            client_button = QPushButton("Клиенты")
            client_button.clicked.connect(lambda: self.load_users("Customers", table))
            user_type_buttons.addWidget(client_button)

            employee_button = QPushButton("Сотрудники")
            employee_button.clicked.connect(lambda: self.load_users("Employees", table))
            user_type_buttons.addWidget(employee_button)

            layout.addLayout(user_type_buttons)

            # Таблица для отображения пользователей
            table = QTableWidget()
            layout.addWidget(table)

            # Кнопки управления
            buttons_layout = QHBoxLayout()

            add_button = QPushButton("Добавить")
            add_button.clicked.connect(lambda: self.add_user(table))
            buttons_layout.addWidget(add_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda: self.delete_selected_user(table))
            buttons_layout.addWidget(delete_button)

            layout.addLayout(buttons_layout)

            # Кнопка закрытия
            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def load_users(self, user_type, table):
        """Загрузка пользователей в таблицу."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            if user_type == "Customers":
                query = "SELECT Customer_ID, First_name, Last_name, Email, Phone_num FROM Customers"
            elif user_type == "Employees":
                query = "SELECT Employee_ID, First_name, Last_name, Role, Login FROM Employees"
            else:
                return

            cursor.execute(query)
            users = cursor.fetchall()

            # Настраиваем таблицу
            table.setRowCount(len(users))
            table.setColumnCount(len(users[0]))
            table.setHorizontalHeaderLabels([desc[0] for desc in cursor.description])

            for row_index, user in enumerate(users):
                for col_index, value in enumerate(user):
                    table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def add_user(self, table):
        """Добавление нового пользователя."""
        try:
            user_type, ok = QInputDialog.getItem(self, "Выбор типа", "Выберите тип пользователя:",
                                                 ["Клиент", "Сотрудник"])
            if not ok:
                return

            if user_type == "Клиент":
                self.add_client()
            elif user_type == "Сотрудник":
                self.add_employee()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def add_client(self):
        """Добавление нового клиента."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            dialog = QDialog(self)
            dialog.setWindowTitle("Добавление клиента")

            layout = QVBoxLayout(dialog)

            # Поля ввода
            first_name = QLineEdit()
            first_name.setPlaceholderText("Имя")
            layout.addWidget(first_name)

            last_name = QLineEdit()
            last_name.setPlaceholderText("Фамилия")
            layout.addWidget(last_name)

            email = QLineEdit()
            email.setPlaceholderText("Email")
            layout.addWidget(email)

            phone_num = QLineEdit()
            phone_num.setPlaceholderText("Телефон")
            layout.addWidget(phone_num)

            login = QLineEdit()
            login.setPlaceholderText("Логин")
            layout.addWidget(login)

            password = QLineEdit()
            password.setPlaceholderText("Пароль")
            password.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(password)

            # Кнопки
            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(
                lambda: self.save_client(first_name, last_name, email, phone_num, login, password, dialog))
            layout.addWidget(save_button)

            dialog.setLayout(layout)
            dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def save_client(self, first_name, last_name, email, phone_num, login, password, dialog):
        """Сохранение нового клиента в базе данных."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = """
                INSERT INTO Customers (First_name, Last_name, Email, Phone_num, Login, Password)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                first_name.text(), last_name.text(), email.text(), phone_num.text(), login.text(), password.text()))
            connection.commit()

            QMessageBox.information(self, "Успех", "Клиент успешно добавлен.")
            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def delete_selected_user(self, table):
        """Удаление выбранного пользователя."""
        try:
            selected_row = table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления.")
                return

            user_id = int(table.item(selected_row, 0).text())
            user_type = "Customers" if "Customer_ID" in table.horizontalHeaderItem(0).text() else "Employees"

            confirmation = QMessageBox.question(self, "Подтверждение",
                                                f"Вы уверены, что хотите удалить пользователя с ID {user_id}?")
            if confirmation != QMessageBox.StandardButton.Yes:
                return

            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = f"DELETE FROM {user_type} WHERE {user_type[:-1]}_ID = ?"
            cursor.execute(query, (user_id,))
            connection.commit()

            QMessageBox.information(self, "Успех", "Пользователь успешно удалён.")
            self.load_users(user_type, table)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def add_employee(self):
        """Добавление нового сотрудника."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            dialog = QDialog(self)
            dialog.setWindowTitle("Добавление сотрудника")

            layout = QVBoxLayout(dialog)

            # Поля ввода
            first_name = QLineEdit()
            first_name.setPlaceholderText("Имя")
            layout.addWidget(first_name)

            last_name = QLineEdit()
            last_name.setPlaceholderText("Фамилия")
            layout.addWidget(last_name)

            role = QLineEdit()
            role.setPlaceholderText("Роль (например, официант, администратор)")
            layout.addWidget(role)

            login = QLineEdit()
            login.setPlaceholderText("Логин")
            layout.addWidget(login)

            password = QLineEdit()
            password.setPlaceholderText("Пароль")
            password.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(password)

            # Кнопки
            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(
                lambda: self.save_employee(first_name, last_name, role, login, password, dialog))
            layout.addWidget(save_button)

            dialog.setLayout(layout)
            dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def save_employee(self, first_name, last_name, role, login, password, dialog):
        """Сохранение нового сотрудника в базе данных."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = """
                INSERT INTO Employees (First_name, Last_name, Role, Login, Password)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (first_name.text(), last_name.text(), role.text(), login.text(), password.text()))
            connection.commit()

            QMessageBox.information(self, "Успех", "Сотрудник успешно добавлен.")
            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def edit_menu(self):
        """Управление меню: добавление, удаление и обновление блюд."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Управление меню")
            dialog.setGeometry(200, 150, 700, 500)

            layout = QVBoxLayout(dialog)

            # Таблица для отображения меню
            table = QTableWidget()
            layout.addWidget(table)

            # Загрузка данных меню
            self.load_menu(table)

            # Кнопки управления
            buttons_layout = QHBoxLayout()

            add_button = QPushButton("Добавить блюдо")
            add_button.clicked.connect(lambda: self.add_menu_item(table))
            buttons_layout.addWidget(add_button)

            edit_button = QPushButton("Редактировать блюдо")
            edit_button.clicked.connect(lambda: self.edit_menu_item(table))
            buttons_layout.addWidget(edit_button)

            delete_button = QPushButton("Удалить блюдо")
            delete_button.clicked.connect(lambda: self.delete_menu_item(table))
            buttons_layout.addWidget(delete_button)

            layout.addLayout(buttons_layout)

            # Кнопка закрытия
            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def load_menu(self, table):
        """Загрузка данных меню в таблицу."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = "SELECT MenuItem_ID, Name, Description, Price, Category FROM MenuItems"
            cursor.execute(query)
            menu_items = cursor.fetchall()

            # Настраиваем таблицу
            table.setRowCount(len(menu_items))
            table.setColumnCount(len(menu_items[0]))
            table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Цена", "Категория"])

            for row_index, item in enumerate(menu_items):
                for col_index, value in enumerate(item):
                    table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def add_menu_item(self, table):
        """Добавление нового блюда в меню."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Добавить блюдо")

            layout = QVBoxLayout(dialog)

            # Поля ввода
            name = QLineEdit()
            name.setPlaceholderText("Название блюда")
            layout.addWidget(name)

            description = QLineEdit()
            description.setPlaceholderText("Описание")
            layout.addWidget(description)

            price = QLineEdit()
            price.setPlaceholderText("Цена")
            layout.addWidget(price)

            category = QLineEdit()
            category.setPlaceholderText("Категория")
            layout.addWidget(category)

            # Кнопка сохранения
            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(
                lambda: self.save_menu_item(name, description, price, category, dialog, table))
            layout.addWidget(save_button)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def save_menu_item(self, name, description, price, category, dialog, table):
        """Сохранение нового блюда в базе данных."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = """
                INSERT INTO MenuItems (Name, Description, Price, Category)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (name.text(), description.text(), float(price.text()), category.text()))
            connection.commit()

            QMessageBox.information(self, "Успех", "Блюдо успешно добавлено.")
            dialog.close()
            self.load_menu(table)  # Обновляем таблицу

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def edit_menu_item(self, table):
        """Редактирование выбранного блюда."""
        try:
            selected_row = table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите блюдо для редактирования.")
                return

            menu_item_id = int(table.item(selected_row, 0).text())

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать блюдо")

            layout = QVBoxLayout(dialog)

            # Поля ввода
            name = QLineEdit(table.item(selected_row, 1).text())
            layout.addWidget(name)

            description = QLineEdit(table.item(selected_row, 2).text())
            layout.addWidget(description)

            price = QLineEdit(table.item(selected_row, 3).text())
            layout.addWidget(price)

            category = QLineEdit(table.item(selected_row, 4).text())
            layout.addWidget(category)

            # Кнопка сохранения
            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(
                lambda: self.update_menu_item(menu_item_id, name, description, price, category, dialog, table))
            layout.addWidget(save_button)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def update_menu_item(self, menu_item_id, name, description, price, category, dialog, table):
        """Обновление информации о блюде в базе данных."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = """
                UPDATE MenuItems
                SET Name = ?, Description = ?, Price = ?, Category = ?
                WHERE MenuItem_ID = ?
            """
            cursor.execute(query, (name.text(), description.text(), float(price.text()), category.text(), menu_item_id))
            connection.commit()

            QMessageBox.information(self, "Успех", "Информация о блюде успешно обновлена.")
            dialog.close()
            self.load_menu(table)  # Обновляем таблицу

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def delete_menu_item(self, table):
        """Удаление выбранного блюда."""
        try:
            selected_row = table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите блюдо для удаления.")
                return

            menu_item_id = int(table.item(selected_row, 0).text())

            confirmation = QMessageBox.question(self, "Подтверждение",
                                                f"Вы уверены, что хотите удалить блюдо с ID {menu_item_id}?")
            if confirmation != QMessageBox.StandardButton.Yes:
                return

            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = "DELETE FROM MenuItems WHERE MenuItem_ID = ?"
            cursor.execute(query, (menu_item_id,))
            connection.commit()

            QMessageBox.information(self, "Успех", "Блюдо успешно удалено.")
            self.load_menu(table)  # Обновляем таблицу

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def view_orders(self):
        """Просмотр всех заказов."""
        try:
            self.load_orders(self.result_table)  # Загружаем данные в таблицу
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def load_orders(self, table):
        """Загрузка данных заказов в таблицу."""
        try:
            connection = sqlite3.connect("restoran.db")
            cursor = connection.cursor()

            query = """
                SELECT 
                    o.Order_ID, 
                    c.First_name || ' ' || c.Last_name AS Customer,
                    e.First_name || ' ' || e.Last_name AS Employee,
                    o.Order_date, 
                    o.Total_Amount, 
                    o.Order_status
                FROM Orders o
                LEFT JOIN Customers c ON o.Customer_ID = c.Customer_ID
                LEFT JOIN Employees e ON o.Employee_ID = e.Employee_ID
            """
            cursor.execute(query)
            orders = cursor.fetchall()

            # Настраиваем таблицу
            table.setRowCount(len(orders))
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([
                "ID заказа", "Клиент", "Сотрудник", "Дата заказа", "Сумма", "Статус"
            ])

            for row_index, order in enumerate(orders):
                for col_index, value in enumerate(order):
                    table.setItem(row_index, col_index, QTableWidgetItem(str(value) if value else "Нет данных"))

            table.resizeColumnsToContents()  # Автоматически подгоняем ширину столбцов

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {e}")
        finally:
            if connection:
                connection.close()

    def reports_in_excel(self):
        pass
