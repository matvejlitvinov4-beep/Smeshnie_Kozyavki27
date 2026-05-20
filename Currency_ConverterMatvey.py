import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

HISTORY_FILE = "conversion_history.json"

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        self.history = self.load_history()
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "CAD", "AUD", "CHF", "TRY", "INR", "BRL"]
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
        # рамка конвертации
        conv_frame = ttk.LabelFrame(self.root, text="Конвертация валют", padding=10)
        conv_frame.pack(fill="x", padx=10, pady=10)

        # сумма
        ttk.Label(conv_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(conv_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # из валюты
        ttk.Label(conv_frame, text="Из валюты:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.from_currency = ttk.Combobox(conv_frame, values=self.currencies, state="readonly", width=10)
        self.from_currency.grid(row=1, column=1, padx=5, pady=5)
        self.from_currency.set("USD")

        # в валюту
        ttk.Label(conv_frame, text="В валюту:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.to_currency = ttk.Combobox(conv_frame, values=self.currencies, state="readonly", width=10)
        self.to_currency.grid(row=2, column=1, padx=5, pady=5)
        self.to_currency.set("EUR")

        # кнопка конвертации
        convert_btn = ttk.Button(conv_frame, text="Конвертировать", command=self.convert)
        convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # результат
        self.result_var = tk.StringVar()
        result_label = ttk.Label(self.root, textvariable=self.result_var, font=("Arial", 14), foreground="green")
        result_label.pack(pady=5)

        # рамка истории
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # таблица
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("Дата", width=120)
        self.tree.column("Результат", width=120)
        self.tree.pack(fill="both", expand=True)

        # кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранную", command=self.delete_selected).pack(side="left", padx=5)

    def convert(self):
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        if not from_curr or not to_curr:
            messagebox.showerror("Ошибка", "Выберите валюты")
            return

        # получаем курс через API
        try:
            url = f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount={amount}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                messagebox.showerror("Ошибка", "Не удалось получить курс. Проверьте интернет.")
                return
            data = response.json()
            if not data.get("success"):
                messagebox.showerror("Ошибка", "Ошибка API. Попробуйте другие валюты.")
                return
            result = data["result"]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {e}")
            return

        self.result_var.set(f"{amount} {from_curr} = {result:.2f} {to_curr}")

        # добавляем в историю
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "date": now,
            "amount": amount,
            "from": from_curr,
            "to": to_curr,
            "result": round(result, 2)
        }
        self.history.insert(0, record)
        if len(self.history) > 50:
            self.history = self.history[:50]
        self.save_history()
        self.update_history_table()

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in self.history:
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["amount"],
                rec["from"],
                rec["to"],
                rec["result"]
            ))

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
            self.history = [h for h in self.history if not (
                h["date"] == values[0] and
                h["amount"] == float(values[1]) and
                h["from"] == values[2] and
                h["to"] == values[3]
            )]
        self.save_history()
        self.update_history_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
