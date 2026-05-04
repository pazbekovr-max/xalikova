import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary (Дневник погоды)")
        self.root.geometry("600x500")

        # Список для хранения данных
        self.records = []
        self.file_path = "weather_data.json"

        # --- Интерфейс (GUI) ---
        
        # Фрейм для ввода
        input_frame = ttk.LabelFrame(root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)

        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="w")

        # Осадки
        self.rain_var = tk.BooleanVar()
        self.rain_check = ttk.Checkbutton(input_frame, text="Осадки (да/нет)", variable=self.rain_var)
        self.rain_check.grid(row=2, column=0, columnspan=4, sticky="w", pady=5)

        # Кнопка Добавить
        btn_add = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        btn_add.grid(row=3, column=0, columnspan=4, pady=10)

        # --- Фильтрация ---
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Дата (необязательно):").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Мин. температура:").grid(row=0, column=2, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        btn_filter = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=4, padx=10)
        
        btn_clear = ttk.Button(filter_frame, text="Сбросить", command=self.clear_filter)
        btn_clear.grid(row=0, column=5)

        # --- Таблица (Treeview) ---
        columns = ("date", "temp", "desc", "rain")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("rain", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temp", width=80)
        self.tree.column("desc", width=250)
        self.tree.column("rain", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Кнопки управления файлом ---
        file_frame = ttk.Frame(root)
        file_frame.pack(fill="x", padx=10, pady=5)

        btn_save = ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_to_json)
        btn_save.pack(side="left", padx=5)

        btn_load = ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_from_json)
        btn_load.pack(side="left", padx=5)

        # Загрузка данных при старте
        self.load_from_json()

    def validate_input(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc_str = self.desc_entry.get().strip()

        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте YYYY-MM-DD.")
            return False

        # Проверка температуры
        try:
            temp_val = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return False

        # Проверка описания
        if not desc_str:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым.")
            return False

        return True, {"date": date_str, "temp": temp_val, "desc": desc_str, "rain": self.rain_var.get()}

    def add_record(self):
        is_valid, data = self.validate_input()
        if not is_valid:
            return

        self.records.append(data)
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись добавлена!")

    def refresh_table(self, data_to_show=None):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Данные для отображения (все или отфильтрованные)
        source_data = data_to_show if data_to_show is not None else self.records

        for record in source_data:
            rain_str = "Да" if record['rain'] else "Нет"
            self.tree.insert("", "end", values=(
                record['date'],
                record['temp'],
                record['desc'],
                rain_str
            ))

    def apply_filter(self):
        date_filter = self.filter_date_entry.get().strip()
        temp_filter_str = self.filter_temp_entry.get().strip()

        filtered_records = []

        for record in self.records:
            # Фильтр по дате
            if date_filter and record['date'] != date_filter:
                continue
            
            # Фильтр по температуре
            if temp_filter_str:
                try:
                    min_temp = float(temp_filter_str)
                    if record['temp'] < min_temp:
                        continue
                except ValueError:
                    messagebox.showwarning("Внимание", "Неверный формат температуры в фильтре.")
                    return

            filtered_records.append(record)

        self.refresh_table(filtered_records)

    def clear_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()

    def save_to_json(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в {self.file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_from_json(self):
        if not os.path.exists(self.file_path):
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
            self.refresh_table()
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл поврежден или имеет неверный формат JSON.")
            self.records = []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
