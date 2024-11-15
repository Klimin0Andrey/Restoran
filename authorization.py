import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit


# from user1_window import WindowForUser1
# from user2_window import WindowForUser1


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

        # Здесь можно добавить код для проверки логина и пароля из базы данных
        if username == "admin" and password == "admin":
            QMessageBox.information(self, "Успех", "Добро пожаловать, администратор!")
        elif username == "user" and password == "user":
            QMessageBox.information(self, "Успех", "Добро пожаловать, пользователь!")
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль.")

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
        QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
        self.close()  # Закрываем окно регистрации
        if self.parent:
            self.parent.show()  # Отображаем окно авторизации

    def go_back(self):
        self.close()  # Закрыть окно регистрации
        if self.parent:
            self.parent.show()  # Отобразить окно авторизации


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PasswordWindow()
    main_window.show()
    sys.exit(app.exec())
