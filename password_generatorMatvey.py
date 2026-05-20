import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

HISTORY_FILE = "password_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        # Данные
        self.history = self.load_history()
        self.current_password = ""

        # Виджеты
        self.create_widgets()
        self.update_history_table()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Ползунок длины
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=32, orient="horizontal",
                                        variable=self.length_var, command=self.update_length_label)
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5, pady=5)

        # Чекбоксы
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Checkbutton(settings_frame, text="Буквы (a-z A-Z)", variable=self.use_letters).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=1, column=2, sticky="w", padx=5)

        # Кнопка генерации
        gen_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        gen_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле для отображения пароля
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), justify="center")
        password_entry.pack(fill="x", padx=10, pady=5)

        # Кнопка копирования в буфер обмена (опционально)
        copy_btn = ttk.Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)

        # Рамка истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Таблица
        columns = ("Пароль", "Длина", "Набор символов")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Набор символов", text="Набор символов")
        self.tree.column("Пароль", width=250)
        self.tree.column("Длина", width=70)
        self.tree.column("Набор символов", width=150)
        self.tree.pack(fill="both", expand=True)

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранный", command=self.delete_selected).pack(side="left", padx=5)

    def update_length_label(self, event=None):
        self.length_label.config(text=str(int(self.length_var.get())))

    def generate_password(self):
        length = int(self.length_var.get())
        if length < 4:
            messagebox.showerror("Ошибка", "Длина пароля не может быть меньше 4")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Длина пароля не может быть больше 32")
            return

        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_symbols.get():
            chars += "!@#$%^&*()_+-=[]{};:,.<>?/"

        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return

        password = ''.join(random.choice(chars) for _ in range(length))
        self.current_password = password
        self.password_var.set(password)

        # Добавляем в историю
        symbols_desc = []
        if self.use_digits.get(): symbols_desc.append("цифры")
        if self.use_letters.get(): symbols_desc.append("буквы")
        if self.use_symbols.get(): symbols_desc.append("спецсимволы")
        symbols_str = ", ".join(symbols_desc)

        self.history.insert(0, {"password": password, "length": length, "charset": symbols_str})
        if len(self.history) > 50:  # ограничим историю
            self.history = self.history[:50]
        self.save_history()
        self.update_history_table()

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.history:
            self.tree.insert("", tk.END, values=(item["password"], item["length"], item["charset"]))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        for item in selected:
            values = self.tree.item(item, "values")
            # Удаляем из истории по совпадению пароля и длины
            self.history = [h for h in self.history if not (h["password"] == values[0] and h["length"] == int(values[1]))]
        self.save_history()
        self.update_history_table()

    def copy_to_clipboard(self):
        if self.current_password:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_password)
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Внимание", "Нет сгенерированного пароля")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
