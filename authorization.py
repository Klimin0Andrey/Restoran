import sqlite3
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit

from client_window import WindowForClient
from admin_window import WindowForAdmin
from employee_window import WindowForEmployee


# Основное окно Авторизации
class PasswordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setGeometry(618, 357, 300, 150)

        layout = QVBoxLayout()  # Расположение основных виджетов в окне авторизации

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

    # Функция для проверки логина и пароля пользователя
    def check_password(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return

        try:
            conn = sqlite3.connect("restoran.db")
            cursor = conn.cursor()

            # Проверяем пользователя среди клиентов
            cursor.execute("""
                SELECT Customer_ID, Role FROM Customers WHERE Login = ? AND Password = ?
            """, (username, password))
            customer = cursor.fetchone()

            if customer:
                user_id, role = customer
                QMessageBox.information(self, "Успех", f"Добро пожаловать, {role}!")
                self.open_user_window(role, user_id)
                return

            # Проверяем пользователя среди сотрудников
            cursor.execute("""
                SELECT Employee_ID, Role FROM Employees WHERE Login = ? AND Password = ?
            """, (username, password))
            employee = cursor.fetchone()

            if employee:
                user_id, role = employee
                QMessageBox.information(self, "Успех", f"Добро пожаловать, {role}!")
                self.open_user_window(role, user_id)
                return

            # Если пользователь не найден, выводим диалоговое окно с информацией
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка работы с базой данных: {e}")
        finally:
            if conn:
                conn.close()

    # Функция для открытия окна пользователя в зависимости от роли
    def open_user_window(self, role, user_id):
        self.hide()  # Скрываем окно авторизации

        # Открываем соответствующее окно в зависимости от роли
        if role == "client":
            self.user_window = WindowForClient(user_id, parent=self)
        elif role == "admin":
            self.user_window = WindowForAdmin(parent=self)
        elif role == "employee":
            self.user_window = WindowForEmployee(user_id, parent=self)
        else:
            QMessageBox.warning(self, "Ошибка", f"Неизвестная роль: {role}")
            self.show()  # Снова показать окно авторизации, если роль не распознана
            return

        self.user_window.show()

    # Функция для сброса данных в окне авторизации при смене пользователя
    def reset(self):
        """Сбрасывает поля ввода."""
        self.username_input.clear()
        self.password_input.clear()

    # Функция открывает окно регистрации
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
        self.setGeometry(618, 250, 300, 250)

        layout = QVBoxLayout()  # Основные виджеты

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

        self.back_button = QPushButton("Назад")
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
        firstname = self.firstname_input.text().strip()
        lastname = self.lastname_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Проверка, что все поля заполнены
        if not all([firstname, lastname, phone, email, username, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Проверка, что имя и фамилия состоят только из букв
        if not (firstname.isalpha() and lastname.isalpha()):
            QMessageBox.warning(self, "Ошибка", "Поля 'Имя' и 'Фамилия' должны содержать только буквы!")
            return
        if len(firstname) >= 64 and len(lastname) >= 64:
            QMessageBox.warning(self, "Ошибка", "Некорректный ввод данных, проверьте данные")
            return

        # Подключение к базе данных
        try:
            conn = sqlite3.connect("restoran.db")
            cursor = conn.cursor()

            # Проверяем, нет ли уже такого логина или email
            cursor.execute("SELECT * FROM Customers WHERE Login = ? OR Email = ?", (username, email))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином или e-mail уже существует!")
                return

            # Вставка нового пользователя
            cursor.execute("""
                    INSERT INTO Customers (First_name, Last_name, Phone_num, Email, Login, Password)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (firstname, lastname, phone, email, username, password))

            # Фиксируем изменения
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")

            # Закрываем текущее окно регистрации
            self.close()

            # Возвращаемся к родительскому окну, если оно задано
            if self.parent:
                self.parent.reset()  # Сбрасываем поля родительского окна
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
