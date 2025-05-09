import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import geocoder

from services.weather_api import WeatherAPI


# Створюємо застосунок
class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Кольори
        self.color_bg = "#111111"  # Фон
        self.color_surface = "#1C1B1C"  # Блоки
        self.color_surface_card = "#262526"  # Карточки
        self.color_text_primary = "#FFFFFF"  # Основні текстові елементи
        self.color_text_secondary = "#CAC4D0"  # Вторинні текстові елементи

        # Іконки
        self.search_icon = ctk.CTkImage(dark_image=Image.open("assets/icons/buttons/search.png"), size=(24, 24))
        self.gps_icon = ctk.CTkImage(dark_image=Image.open("assets/icons/buttons/gps.png"), size=(24, 24))

        # Стилі тексту
        self.style_primary = ctk.CTkFont(family="Roboto Medium", size=24)
        self.style_big_card_element = ctk.CTkFont(family="Roboto Medium", size=20)
        self.style_big_element = ctk.CTkFont(family="Roboto Medium", size=16)
        self.style_bars_element = ctk.CTkFont(family="Roboto", size=16)
        self.style_small_element = ctk.CTkFont(family="Roboto", size=14)
        self.style_secondary = ctk.CTkFont(family="Roboto", size=12)
        self.style_small_card_element = ctk.CTkFont(family="Roboto", size=10)

        # Ініціалізація
        self.weather_api = WeatherAPI()

        # Налаштування вікна
        self.title("Weather App")
        self.geometry("1200x728")
        self.configure(fg_color=self.color_bg)

        # Створюємо фрейми для віджетів
        self.search_bar_frame = ctk.CTkFrame(self, fg_color=self.color_surface, corner_radius=32, width=760, height=56)
        self.search_bar_frame.place(x=24, y=24)

        self.city_info_frame = ctk.CTkFrame(self, fg_color=self.color_surface, corner_radius=32, width=760, height=264)
        self.city_info_frame.place(x=24, y=100)

        self.hourly_cards_frame = ctk.CTkScrollableFrame(self, fg_color=self.color_surface, corner_radius=0,
                                                         scrollbar_button_color=self.color_surface_card,
                                                         scrollbar_button_hover_color=self.color_surface_card,
                                                         orientation="horizontal", width=724, height=146)
        self.hourly_cards_frame.place(x=44, y=178)

        self.weekly_forecast_frame = ctk.CTkFrame(self, fg_color=self.color_surface, corner_radius=32,
                                                  width=368, height=680)
        self.weekly_forecast_frame.place(x=808, y=24)

        self.weekly_cards_frame = ctk.CTkFrame(self.weekly_forecast_frame, fg_color="transparent", corner_radius=12,
                                               width=328, height=558)
        self.weekly_cards_frame.place(x=20, y=78)

        self.stats_frame = ctk.CTkFrame(self, fg_color=self.color_surface, corner_radius=32, width=760, height=321)
        self.stats_frame.place(x=24, y=384)

        self.graphics_frame = ctk.CTkScrollableFrame(self.stats_frame, fg_color=self.color_surface, corner_radius=0,
                                                  scrollbar_button_color=self.color_surface_card,
                                                  scrollbar_button_hover_color=self.color_surface_card,
                                                  width=720, height=212)
        self.graphics_frame.place(x=20, y=85)


        # Створення інтерфейсу
        self.search_icon = ctk.CTkLabel(self.search_bar_frame, text="", image=self.search_icon, width=24, height=24)
        self.search_icon.bind("<Button-1>", self.submit)
        self.search_icon.place(x=16, y=16)

        self.gps_icon = ctk.CTkLabel(self.search_bar_frame, text="", image=self.gps_icon, width=24, height=24)
        self.gps_icon.bind("<Button-1>", self.locate_city)
        self.gps_icon.place(x=720, y=16)

        self.search_bar = ctk.CTkEntry(self.search_bar_frame, placeholder_text="Search city",
                                       placeholder_text_color = self.color_text_secondary, font=self.style_bars_element,
                                       text_color=self.color_text_secondary, fg_color=self.color_surface,
                                       border_width=0, width=655, height=56)
        self.search_bar.bind("<Return>", self.submit)
        self.search_bar.place(x=44, y=0)

        self.city = ctk.CTkLabel(self.city_info_frame, text="", font=self.style_primary,
                                 text_color=self.color_text_primary, fg_color="transparent")
        self.city.place(x=20, y=18)

        self.description = ctk.CTkLabel(self.city_info_frame, text="", font=self.style_secondary,
                                        text_color=self.color_text_secondary, fg_color="transparent")
        self.description.place(x=20, y=46)

        self.temperature = ctk.CTkLabel(self.city_info_frame, text="", font=self.style_primary,
                                        text_color=self.color_text_primary, fg_color="transparent",
                                        anchor="e", justify="right", width=100)
        self.temperature.place(x=640, y=18)

        self.feels_like = ctk.CTkLabel(self.city_info_frame, text="", font=self.style_secondary,
                                       text_color=self.color_text_secondary, fg_color="transparent",
                                       anchor="e", justify="right", width=100)
        self.feels_like.place(x=640, y=46)

        self.header1 = ctk.CTkLabel(self.weekly_forecast_frame, text="Weekly forecast", font=self.style_primary,
                                    text_color=self.color_text_primary, fg_color="transparent")
        self.header1.place(x=20, y=18)

        self.subheader1 = ctk.CTkLabel(self.weekly_forecast_frame, text="Keep an eye on the weather and don't get wet",
                                       font=self.style_secondary, text_color=self.color_text_secondary,
                                       fg_color="transparent")
        self.subheader1.place(x=20, y=44)

        self.header2 = ctk.CTkLabel(self.stats_frame, text="Statistics", font=self.style_primary,
                                    text_color=self.color_text_primary, fg_color="transparent")
        self.header2.place(x=20, y=18)

        self.subheader2 = ctk.CTkLabel(self.stats_frame, text="Graphics, etc.", font=self.style_secondary,
                                       text_color=self.color_text_secondary, fg_color="transparent")
        self.subheader2.place(x=20, y=44)

        self.locate_city()

    def locate_city(self, event=None):
        city = geocoder.ip("me").city
        self.submit(city=city)

    def submit(self, event=None, city=None):
        manual_input = False
        if city is None:
            city = self.search_bar.get()
            manual_input = True

        if not city:
            return messagebox.showerror("Error", "Please enter a city")
        elif not city.replace(" ", "").replace("-", "").isalpha():
            return messagebox.showerror("Error", "Please enter a valid name of the city")

        if manual_input:
            self.search_bar.delete(0, "end")
            self.focus_set()

        weather = self.weather_api.get_weather(city)
        forecast = self.weather_api.get_hourly_forecast(city)
        weekly_forecast = self.weather_api.get_weekly_forecast(city)

        if weather and forecast and weekly_forecast:
            self.update_current_weather(weather)
            self.update_current_forecast(forecast)
            self.update_current_weekly_forecast(weekly_forecast)

            for widget in self.graphics_frame.winfo_children():
                widget.destroy()

            self.update_linear_graphic(forecast)
            self.update_bar_graphic(forecast)
            self.update_pie_chart(forecast)
        else:
            messagebox.showerror("Error", "Couldn't get weather data. Try another city.")

    def update_current_weather(self, weather):
        self.city.configure(text=weather["city"])
        self.description.configure(text=weather["description"].capitalize())
        self.temperature.configure(text=str(round(weather["temperature"])) + "°C")
        self.feels_like.configure(text="Feels like " + str(round(weather["feels_like"])) + "°C")

    def update_current_forecast(self, forecast):
        for widget in self.hourly_cards_frame.winfo_children():
            widget.destroy()

        for i, item in enumerate(forecast):
            item_card = ctk.CTkFrame(self.hourly_cards_frame, fg_color=self.color_surface_card, corner_radius=12,
                                     width=90, height=138)
            item_card.pack(side="left", padx=(0, 6) if i == 0 else 6)

            temp = ctk.CTkLabel(item_card, text=str(round(item["temperature"])) + "°C", font=self.style_big_element,
                                text_color=self.color_text_primary, width=90)
            temp.place(x=0, y=12)

            time = ctk.CTkLabel(item_card, text=item["datetime"], font=self.style_small_element,
                                text_color=self.color_text_secondary, width=32)
            time.place(x=29, y=108)

            day_time = "day" if 6 <= int(item["datetime"][:-3]) < 20 else "night"

            icon_name = self.get_icon_name(item["description"], day_time)
            icon_png = ctk.CTkImage(dark_image=Image.open(f"assets/icons/weather/{icon_name}.png"), size=(50, 50))
            icon = ctk.CTkLabel(item_card, text="", image=icon_png, width=90, height=50)
            icon.place(x=0, y=48)

    def update_current_weekly_forecast(self, weekly_forecast):
        for widget in self.weekly_cards_frame.winfo_children():
            widget.destroy()

        for i, item in enumerate(weekly_forecast):
            item_card = ctk.CTkFrame(self.weekly_cards_frame, fg_color=self.color_surface_card, corner_radius=12,
                                     width=328, height=69)
            item_card.pack(side="top", pady=(0, 8) if i == 0 else (8, 0) if i == 6 else 8)

            desc = "clear sky" if item["description"] == "sky is clear" else item["description"]
            description = ctk.CTkLabel(item_card, text=desc.capitalize(), font=self.style_secondary,
                                       text_color=self.color_text_secondary)
            description.place(x=20, y=34)

            day = ctk.CTkLabel(item_card, text="Today" if i == 0 else "Tomorrow" if i == 1 else item["day"],
                               font=self.style_big_card_element, text_color=self.color_text_primary)
            day.place(x=20, y=11)

            temperature_day = ctk.CTkLabel(item_card, text=str(round(item["temperature_day"])) + "°C",
                                           font=self.style_big_card_element, text_color=self.color_text_primary,
                                           anchor="e", justify="right", width=60)
            temperature_day.place(x=248, y=11)

            temperature_night = ctk.CTkLabel(item_card, text="Min." + str(round(item["temperature_night"])) + "°C",
                                             font=self.style_secondary, text_color=self.color_text_secondary,
                                             anchor="e", justify="right", width=60)
            temperature_night.place(x=248, y=34)

            icon_name = self.get_icon_name(desc, "day")
            icon_png = ctk.CTkImage(dark_image=Image.open(f"assets/icons/weather/{icon_name}.png"), size=(40, 40))
            icon = ctk.CTkLabel(item_card, text="", image=icon_png, width=40, height=40)
            icon.place(x=190, y=13)

    def get_icon_name(self, description: str, day_time: str = "day") -> str:
        try:
            with open("config/weather_icons_mapping.json", "r", encoding="utf-8") as f:
                icons_data = json.load(f)
        except FileNotFoundError:
            print("JSON файл не найден")
            return "default"
        except json.JSONDecodeError:
            print("Ошибка при чтении weather_icons_mapping.json")
            return "default"

        weather_mapping = icons_data.get("weather_icons_mapping", {})
        description = description.lower()

        for category in weather_mapping.values():
            for desc_pattern, icon_info in category.items():
                if desc_pattern.lower() in description or description in desc_pattern.lower():
                    if isinstance(icon_info, dict):
                        return icon_info.get(day_time, "default")
                    elif isinstance(icon_info, str):
                        return icon_info

        return "default"

    def update_linear_graphic(self, forecast):
        hours = [item["datetime"] for item in forecast]
        temperatures = [item["temperature"] for item in forecast]
        feels_like = [item["feels_like"] for item in forecast]

        fig, ax = plt.subplots(figsize=(7.2, 2), dpi=100) # Створюємо фігуру та вісь для побудови графіка

        ax.plot(hours, temperatures, label="Temperature", color="#ff9800", marker="o") # Малюємо лінію температури по координатах
        ax.plot(hours, feels_like, label="Feels like", color="#90caf9", linestyle="--", marker="x") # Малюємо лінію "як відчувається температура" по координатах

        ax.set_facecolor("#262526") # Встановлюємо фон графіку
        fig.patch.set_facecolor("#262526") # Встановлюємо фон фігури
        ax.tick_params(axis="x", colors="white", labelrotation=45, labelsize=7) # Налаштовуємо параметри осі Х, всім елементам даємо білий колір, повертаємо мітки на 45 градусів і розмір шрифту ставимо 7
        ax.tick_params(axis="y", colors="white", labelsize=8) # Налаштовуємо параметри осі Y, все те саме, крім повороту елементів
        ax.spines['bottom'].set_color('#FFFFFF') # Встановлюємо білий колір нижній і лівій рамці
        ax.spines['left'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#262526') # Встановлюємо колір заднього фону верхній і правій рамці
        ax.spines['right'].set_color('#262526')
        ax.yaxis.label.set_color('white') # Встановлюємо білий колір текстам
        ax.xaxis.label.set_color('white')
        ax.set_xlabel("Hour") # Встановлюємо назву осі Х та Y
        ax.set_ylabel("Temperature (°C)")
        ax.legend(facecolor="#262526", edgecolor="white", labelcolor="white", fontsize=8) # Додаємо легенду, тобто пояснення кольорів

        fig.tight_layout() # Автоматично розставляємо елементи, щоб не вилізти за графік

        canvas = FigureCanvasTkAgg(fig, master=self.graphics_frame) # Створюємо полотно для відображення графіка
        canvas.draw()
        canvas.get_tk_widget().pack(pady=8, fill="both", expand=True)

    def update_bar_graphic(self, forecast):
        hours = [item["datetime"] for item in forecast]
        speed = [item["wind_speed"] for item in forecast]

        fig, ax = plt.subplots(figsize=(7.2, 2), dpi=100)  # Створюємо фігуру та вісь для побудови графіка

        # Створюємо стовпчасту діаграму для швидкості вітру
        ax.bar(hours, speed, label="Wind Speed", color="#ff9800", width=0.4, align="center")  # Стовпці для швидкості вітру

        ax.set_facecolor("#262526") # Встановлюємо фон графіку
        fig.patch.set_facecolor("#262526") # Встановлюємо фон фігури
        ax.tick_params(axis="x", colors="white", labelrotation=45, labelsize=7) # Налаштовуємо параметри осі X
        ax.tick_params(axis="y", colors="white", labelsize=8)  # Налаштовуємо параметри осі Y
        ax.spines['bottom'].set_color('#FFFFFF') # Встановлюємо білий колір нижній і лівій рамці
        ax.spines['left'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#262526') # Встановлюємо колір заднього фону верхній і правій рамці
        ax.spines['right'].set_color('#262526')
        ax.yaxis.label.set_color('white') # Встановлюємо білий колір текстам
        ax.xaxis.label.set_color('white')
        ax.set_xlabel("Hour")  # Встановлюємо назву осі X
        ax.set_ylabel("Wind Speed (m/s)")  # Встановлюємо назву осі Y
        ax.legend(facecolor="#262526", edgecolor="white", labelcolor="white", fontsize=8)  # Додаємо легенду

        fig.tight_layout()  # Автоматично розставляємо елементи

        canvas = FigureCanvasTkAgg(fig, master=self.graphics_frame)  # Створюємо полотно для відображення графіка
        canvas.draw()
        canvas.get_tk_widget().pack(pady=8, fill="both", expand=True)

    def update_pie_chart(self, forecast):
        hours = [item["datetime"] for item in forecast]
        humidity = [item["humidity"] for item in forecast]

        humidity_values = [round(item, 0) for item in humidity]  # Округлюємо вологість до цілих значень
        humidity_labels = [f"{hour}: {hum}%" for hour, hum in zip(hours, humidity_values)]  # Створюємо підписи з годиною і вологістю

        fig, ax = plt.subplots(figsize=(5, 5), dpi=100)  # Створюємо фігуру для кругової діаграми

        # Створюємо кругову діаграму
        ax.pie(humidity_values, labels=humidity_labels, autopct='%1.1f%%', startangle=90, textprops={'color': 'white'})

        ax.set_facecolor("#262526")  # Встановлюємо фон графіку
        fig.patch.set_facecolor("#262526")  # Встановлюємо фон фігури
        ax.tick_params(axis="x", colors="white")  # Налаштовуємо параметри осі X
        ax.tick_params(axis="y", colors="white")  # Налаштовуємо параметри осі Y
        ax.spines['bottom'].set_color('#FFFFFF')  # Встановлюємо білий колір рамки
        ax.spines['left'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#262526')
        ax.spines['right'].set_color('#262526')

        fig.tight_layout()  # Автоматично розставляємо елементи

        canvas = FigureCanvasTkAgg(fig, master=self.graphics_frame)  # Створюємо полотно для відображення графіка
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = WeatherApp()
    app.mainloop()
