import sqlite3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit


from client_window import WindowForClient
from admin_window import WindowForAdmin
from employee_window import WindowForEmployee


class PasswordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.username_label = QLabel("Логин:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин...")
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_password)

        self.signup_button = QPushButton("Регистрация")
        self.signup_button.clicked.connect(self.registration)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def check_password(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return

        try:
            conn = sqlite3.connect("restoran.db")  # Замените на путь к вашей базе данных
            cursor = conn.cursor()

            # Проверяем пользователя среди клиентов
            cursor.execute("""
                SELECT Role FROM Customers WHERE Login = ? AND Password = ?
            """, (username, password))
            customer = cursor.fetchone()

            if customer:
                role = customer[0]
                QMessageBox.information(self, "Успех", f"Добро пожаловать, {role}!")
                self.open_user_window(role)
                return

            # Проверяем пользователя среди сотрудников
            cursor.execute("""
                SELECT Role FROM Employees WHERE Login = ? AND Password = ?
            """, (username, password))
            employee = cursor.fetchone()

            if employee:
                role = employee[0]
                QMessageBox.information(self, "Успех", f"Добро пожаловать, {role}!")
                self.open_user_window(role)
                return

            # Если пользователь не найден
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка работы с базой данных: {e}")
        finally:
            if conn:
                conn.close()

    def open_user_window(self, role):
        self.close()  # Закрываем окно авторизации

        # Храним ссылку на новое окно в атрибуте self
        if role == "client":
            self.user_window = WindowForClient()
        elif role == "admin":
            self.user_window = WindowForAdmin()
        elif role == "employee":
            self.user_window = WindowForEmployee()
        else:
            QMessageBox.warning(self, "Ошибка", f"Неизвестная роль: {role}")
            self.show()  # Снова показать окно авторизации, если роль не распознана
            return

        self.user_window.show()

    def registration(self):
        self.hide()  # Скрываем окно авторизации
        self.register_window = RegisterWindow(self)  # Создаем окно регистрации
        self.register_window.show()


# Окно регистрации
class RegisterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # Передаем родительское окно (авторизацию)

        self.setWindowTitle("Регистрация")
        self.setGeometry(100, 100, 300, 250)

        layout = QVBoxLayout()

        self.firstname_label = QLabel("Имя:")
        self.firstname_input = QLineEdit()
        self.lastname_label = QLabel("Фамилия:")
        self.lastname_input = QLineEdit()
        self.phone_label = QLabel("Телефон:")
        self.phone_input = QLineEdit()
        self.email_label = QLabel("E-mail:")
        self.email_input = QLineEdit()
        self.username_label = QLabel("Логин:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register_user)

        self.back_button = QPushButton("Назад")  # Кнопка "Назад"
        self.back_button.clicked.connect(self.go_back)

        layout.addWidget(self.firstname_label)
        layout.addWidget(self.firstname_input)
        layout.addWidget(self.lastname_label)
        layout.addWidget(self.lastname_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def register_user(self):
        firstname = self.firstname_input.text()
        lastname = self.lastname_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        # Здесь можно добавить код для регистрации в базу данных (например, SQLite)
        # Для простоты предполагаем, что регистрация прошла успешно:
        if not all([firstname, lastname, phone, email, username, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

            # Подключение к базе данных
        try:
            conn = sqlite3.connect("restoran.db")  # Замените на путь к вашей базе данных
            cursor = conn.cursor()

            # Проверяем, нет ли уже такого логина или email
            cursor.execute("SELECT * FROM Customers WHERE Login = ? OR Email = ?", (username, email))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином или email уже существует!")
                return

            # Вставка нового пользователя
            cursor.execute("""
                    INSERT INTO Customers (First_name, Last_name, Phone_num, Email, Login, Password)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (firstname, lastname, phone, email, username, password))

            # Фиксируем изменения
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")

            # Закрываем окно регистрации
            self.close()
            if self.parent:
                self.parent.show()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка работы с базой данных: {e}")
        finally:
            if conn:
                conn.close()

    def go_back(self):
        self.close()  # Закрыть окно регистрации
        if self.parent:
            self.parent.show()  # Отобразить окно авторизации


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PasswordWindow()
    main_window.show()
    sys.exit(app.exec())
