import sys
import threading   # Для многопоточности
from translate import Translator   # Для перевода текста
import qdarkstyle   # Для темных и светлых стилей для приложения
import requests   # Для выполнения HTTP-запросов
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout)   # Для создания приложения
from geopy.geocoders import Nominatim   # Для получения координат по названию города
from geopy.exc import GeocoderTimedOut, GeocoderServiceError # Обработка ошибок
import pytz   # Для работы с часовыми поясами
from datetime import datetime   # Для получения текущего времени
from timezonefinder import TimezoneFinder   # Для определения часового пояса по координатам


app = QApplication(sys.argv)


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Введите название города: ", self)  # Создаем пол-ий интерфейс
        self.cite_input = QLineEdit(self)
        self.button = QPushButton("Узнать погоду", self)
        self.temperature = QLabel(self)
        self.emoji = QLabel(self)
        self.description = QLabel(self)
        self.initUI()
        self.Style()
        self.forecast_label_widget = QLabel()
        self.open_button = QPushButton("Время", self)
        self.open_button.move(30, 520)
        self.open_button.resize(150, 50)

        self.new_window = None
        self.open_button.clicked.connect(self.open_new_window)

    def initUI(self):  # Функция с выравниванием интерфейса и с названием приложения
        self.setWindowTitle("Прогноз погоды")
        self.setWindowIcon(QIcon('icons8-солнце-100.png'))

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)  # Выравниваем по вертикали
        vbox.addWidget(self.cite_input)
        vbox.addWidget(self.button)
        vbox.addWidget(self.temperature)
        vbox.addWidget(self.emoji)
        vbox.addWidget(self.description)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)  # Выравниваем по горизонтили
        self.cite_input.setAlignment(Qt.AlignCenter)
        self.temperature.setAlignment(Qt.AlignCenter)
        self.emoji.setAlignment(Qt.AlignCenter)
        self.description.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_label.setObjectName("cite_input")
        self.city_label.setObjectName("button")
        self.city_label.setObjectName("temperature")
        self.city_label.setObjectName("emoji")
        self.city_label.setObjectName("description")


    def get_weather_for_city(self): # Функция с окном ошибки
        city = self.cite_input.text()
        if not city:
            QMessageBox.warning(self, "Ошибка", "Введите название города!")
            return


    def get_weather(self):  # Функция для вывода ошибок
        global response
        api_key = '0b49be77773d38b90a1fee8cbe3d4ef4'
        city = self.cite_input.text()
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            if response.status_code == 400:
                self.get_weather_for_city()
            elif response.status_code == 401:
                self.display_error("Ошибка авторизации:\nНедействительный API ключ.")
            elif response.status_code == 403:
                self.display_error("Ошибка доступа:\nЗапрещен доступ к ресурсу.")
            elif response.status_code == 404:
                self.display_error("Ошибка:\nГород не найден.\n Проверьте правильность ввода.")
            elif response.status_code == 408:
                self.display_error("Ошибка:\nВремя ожидания запроса истекло.")
            elif response.status_code == 500:
                self.display_error("Ошибка сервера:\nПроизошла внутренняя ошибка сервера.\n Повторите попытку позже.")
            elif response.status_code == 502:
                self.display_error("Ошибка шлюза:\nПолучен недействительный ответ от шлюза.")
            elif response.status_code == 503:
                 self.display_error("Ошибка:\nСервис временно недоступен.\n Повторите попытку позже.")
            elif response.status_code == 504:
                self.display_error("Ошибка времени ожидания:\nСервер не отвечает")
            elif response.status_code == 407:
               self.display_error("Ошибка:\nТребуется аутентификация прокси")
            elif response.status_code == 410:
                self.display_error("Ошибка:\nРесурс удален")
            elif response.status_code == 413:
                self.display_error("Ошибка:\nЗапрос слишком большой")
            elif response.status_code == 414:
                self.display_error("Ошибка:\nURI слишком длинный")
            elif response.status_code == 415:
                 self.display_error("Ошибка:\nНе поддерживаемый формат")
            elif response.status_code == 429:
                self.display_error("Ошибка:\nСлишком много запросов")
            elif response.status_code == 501:
                self.display_error("Ошибка:\nНе реализована функциональность")
            elif response.status_code == 505:
                self.display_error("Ошибка:\nВерсия HTTP не поддерживается")
            else:
                self.display_error(f"Ошибка HTTP: \n{http_error}. Код ошибки {response.status_code}")

        except requests.exceptions.ConnectionError as connection_error:
            self.display_error(f"Ошибка подключения:\nПроверьте ваше интернет-соединение.\n {connection_error}")
        except requests.exceptions.Timeout as timeout_error:
            self.display_error(f"Ошибка времени ожидания:\nВремя ожидания запроса истекло.\n{timeout_error}")
        except requests.exceptions.TooManyRedirects as too_many_redirects:
             self.display_error(f"Ошибка:\nСлишком много перенаправлений.\n {too_many_redirects}")
        except requests.exceptions.InvalidURL as invalid_url:
             self.display_error(f"Ошибка:\nНедопустимый URL-адрес.\n {invalid_url}")
        except requests.exceptions.RequestException as req_er:
            self.display_error(f"Общая ошибка запроса:\n{req_er} Проверьте правильность ввода")
        except requests.JSONDecodeError as json_error:
            self.display_error(f"Ошибка декодирования JSON:\nНе удалось обработать данные.\n {json_error}")
        except Exception as e:
            self.display_error(f"Неизвестная ошибка:\n{e} Пожалуйста, повторите попытку позже")


    def display_error(self, message):
        self.temperature.setStyleSheet("font-size: 25px;")
        self.temperature.setStyleSheet("color: red")
        self.temperature.setText(message)
        self.emoji.clear()
        self.description.clear()



    def display_weather(self, data):

        self.temperature.setStyleSheet("color: #C2E3FA")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k -273.15
        weather_id = data["weather"][0]["id"]
        self.temperature.setText(f"{temperature_c:.0f}℃")
        weather_description = data["weather"][0]["description"]
        translator = Translator(from_lang="en", to_lang="ru")
        text = translator.translate(weather_description)
        if text == "weather condition":
            text = "Облачно"
        self.description.setText(text)
        self.emoji.setText(self.emoji_weather(weather_id))


    def Style(self):  # Функция с настраиванием стиля интерфейса
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()  # Меняем цвет фона
        app.setStyleSheet(dark_stylesheet)

        self.temperature.setStyleSheet("font: bold 15px")  # настраиваем стиль
        self.emoji.setStyleSheet("font-family: Segoe UI emoji")


        self.setStyleSheet("""      
           
            QLabel {
                font: bold 50px;
                color: #F5FBFF;
                font-weight: 500;
                    }

            QLineEdit{
                font: 22px;
                border-width: 2px;
                border-color: #66B5FF;
                border-radius: 10px;
                        }

            QPushButton {
                background-color: #0d6efd;
                color: #fff;
                font-weight: 700;
                border-radius: 10px;
                border: 1px solid #0d6efd;
                padding: 10px 30px;
                margin-top: 10px;
                outline: 0px;
                font: bold 15px;
                        }

            QPushButton:hover,
            QPushButton:focus {
                background-color: #0b5ed7;
                border: 3px solid #9ac3fe;
                        }

        """)

        self.button.clicked.connect(self.get_weather)

    def display_forecast(self, forecast_data):
        if not forecast_data:
            return

        for i in range(min(5, len(forecast_data))):
            day_data = forecast_data[i * 8]  # Берем данные с интервалом 24 часа
            date_str = day_data['dt_txt']
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            temp = day_data['main']['temp']
            description = day_data['weather'][0]['description']

            forecast_text = f"{formatted_date}: {temp}°C, {description}"
            forecast_label = QLabel(forecast_text)
            forecast_label.setStyleSheet(f"font-size: 14px; color: {self.text_color};")

            # Вместо добавления в layout нужно добавлять widget
            layout = self.forecast_layouts[i]
            layout.addWidget(forecast_label)
            if layout.count() > 0:  # Очищаем layout, если уже есть данные
                for j in range(layout.count()):
                    item = layout.takeAt(0)
                    if item.widget(): item.widget().deleteLater()


    @staticmethod
    def emoji_weather(weather_id):

        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "⛅"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "🌨️"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""

    def open_new_window(self):
        """Открывает новое окно."""
        if self.new_window is None:
            self.new_window = TimeZoneApp()
        self.new_window.show()
        self.new_window.activateWindow()


class TimeZoneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Время по городу")
        self.setMinimumSize(400, 200) # Минимальный размер окна
        self.move(300, 300)


        self.city_label_time = QLabel("Введите название города:") # Метка для поля ввода города
        self.city_input_time = QLineEdit() # Поле ввода города
        self.get_time_button = QPushButton("Получить время")
        self.get_time_button.clicked.connect(self.get_time_for_city) # Подключение функции к кнопке
        self.time_label = QLabel("")
        self.timezone_label = QLabel("")


        self.setStyleSheet("""
           QPushButton {
               background-color: #4CAF50;
               color: white;
               border: none;
               padding: 8px;
               border-radius: 5px;
           }
           QPushButton:hover {
               background-color: #367c39;
           }
           QLineEdit{
                color: #062647;
                font: 10px;
                        }
        """)


        main_layout = QVBoxLayout() # Главный вертикальный макет
        city_layout = QHBoxLayout() # Горизонтальный макет для поля ввода города
        city_layout.addWidget(self.city_label_time)
        city_layout.addWidget(self.city_input_time)
        main_layout.addLayout(city_layout)
        main_layout.addWidget(self.get_time_button)
        main_layout.addWidget(self.time_label)
        main_layout.addWidget(self.timezone_label)
        self.setLayout(main_layout) # Установка главного макета для окна
        self.city_label_time.setAlignment(Qt.AlignCenter) # Выравнивание меток по центру
        self.time_label.setAlignment(Qt.AlignCenter)
        self.timezone_label.setAlignment(Qt.AlignCenter)
        self.city_input_time.setStyleSheet(f"background-color: white; border: 1px solid #e0e0e0; padding: 5px;")
        self.time_label.setStyleSheet(f"font-size: 20px; font-weight: bold;")


    def get_time_for_city(self):
        """Получает время для введенного города."""
        city = self.city_input_time.text() # Получение текста из поля ввода
        if not city: # Проверка, что поле ввода не пустое
            QMessageBox.warning(self, "Ошибка", "Введите название города!") # Вывод сообщения об ошибке
            return
        self.time_label.setText("Загрузка...") # Вывод сообщения о загрузке
        threading.Thread(target=self.fetch_and_update_time, args=(city,), daemon=True).start() # Запуск функции в отдельном потоке


    def fetch_and_update_time(self, city):
        """Получает координаты и время для города и обновляет метки."""
        try:
            geolocator = Nominatim(user_agent="timezone_app") # Создание объекта геокодера
            location = geolocator.geocode(city, timeout=10) # Получение координат по названию города, timeout=10 секунда
            if location is None:
                self.time_label.setText("Ошибка: Не удалось найти город.")
                self.timezone_label.setText("")
                return
            timezone_str = self.get_timezone_from_coords(location.latitude, location.longitude) # Получение часового пояса по координатам
            if timezone_str:
                time_str = self.get_current_time_in_timezone(timezone_str) # Получение текущего времени в нужном часовом поясе
                self.time_label.setText(f"Время: {time_str}") # Обновление метки времени
                self.timezone_label.setText(f"Часовой пояс: {timezone_str}") # Обновление метки часового пояса
            else:
                self.time_label.setText("Не удалось определить часовой пояс")
                self.timezone_label.setText("")
        except GeocoderTimedOut:
            self.time_label.setText("Ошибка: Время ожидания запроса истекло.")
            self.timezone_label.setText("")
        except GeocoderServiceError:
            self.time_label.setText("Ошибка: Ошибка сервиса геокодирования.")
            self.timezone_label.setText("")
        except Exception as e:
            self.time_label.setText(f"Ошибка: {e}") # Обработка других ошибок
            self.timezone_label.setText("")


    def get_timezone_from_coords(self, latitude, longitude):
        """Получает часовой пояс по координатам."""
        try:
           tf = TimezoneFinder() # Создание объекта TimezoneFinder
           timezone_str = tf.timezone_at(lng=longitude, lat=latitude) # Получение часового пояса по координатам
           return timezone_str
        except Exception as e:
           return None


    def get_current_time_in_timezone(self, timezone_str):
        """Получает текущее время в заданном часовом поясе."""
        try:
            timezone = pytz.timezone(timezone_str) # Создание объекта часового пояса
            now = datetime.now(timezone) # Получение текущего времени в часовом поясе
            return now.strftime("%H:%M:%S %d.%m.%Y") # Форматирование времени в строку
        except pytz.exceptions.UnknownTimeZoneError:
            return None
        except Exception as e:
            return None


if __name__ == '__main__':
    weather_app = WeatherApp()
    weather_app.resize(900, 600)
    weather_app.show()
    sys.exit(app.exec())
