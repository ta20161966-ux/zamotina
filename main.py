import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# --- Настройки ---
API_KEY = 'YOUR_API_KEY'  # Замените на свой ключ с exchangerate-api.com
HISTORY_FILE = 'history.json'

# --- Функции ---
def load_history():
    """Загружает историю из файла JSON."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    """Сохраняет историю в файл JSON."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

def get_currencies():
    """Получает список доступных валют от API."""
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/codes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [code for code, name in data['supported_codes']]
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить список валют: {e}")
        return ['USD', 'EUR', 'RUB']  # Дефолтные значения

def convert_currency():
    """Обрабатывает конвертацию валют."""
    amount_str = amount_entry.get()
    from_currency = from_var.get()
    to_currency = to_var.get()

    # Проверка ввода
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректную сумму (положительное число).")
        return

    # Запрос к API
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['result'] == 'error':
            messagebox.showerror("Ошибка API", data['error-type'])
            return

        result = data['conversion_result']
        
        # Обновление истории
        history = load_history()
        history.insert(0, {
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "result": result,
            "rate": data['conversion_rate']
        })
        save_history(history)
        
        # Обновление интерфейса
        update_history_table()
        result_label.config(text=f"Результат: {result:.2f} {to_currency}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выполнить запрос: {e}")

def update_history_table():
    """Обновляет таблицу истории."""
    for i in history_tree.get_children():
        history_tree.delete(i)
    
    for item in load_history():
        history_tree.insert("", "end", values=(
            item['from'],
            item['to'],
            item['amount'],
            item['result'],
            item['rate']
        ))

# --- Создание окна ---
root = tk.Tk()
root.title("Currency Converter")
root.geometry("700x500")
root.resizable(False, False)

# --- Виджеты ---
# Выбор валют
currencies = get_currencies()

tk.Label(root, text="Из:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
from_var = tk.StringVar(value='USD')
from_menu = ttk.Combobox(root, textvariable=from_var, values=currencies, width=5)
from_menu.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="В:").grid(row=0, column=2, padx=10, pady=10, sticky="e")
to_var = tk.StringVar(value='EUR')
to_menu = ttk.Combobox(root, textvariable=to_var, values=currencies, width=5)
to_menu.grid(row=0, column=3, padx=10, pady=10)

# Поле ввода суммы
tk.Label(root, text="Сумма:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
amount_entry = tk.Entry(root)
amount_entry.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="we")

# Кнопка конвертации
convert_btn = tk.Button(root, text="Конвертировать", command=convert_currency)
convert_btn.grid(row=2, column=1, columnspan=2, pady=20)

# Результат
result_label = tk.Label(root, text="Результат: ", font=('Arial', 12))
result_label.grid(row=3, column=0, columnspan=4, pady=(0, 10))

# Таблица истории
history_tree = ttk.Treeview(root, columns=('From', 'To', 'Amount', 'Result', 'Rate'), show='headings')
history_tree.heading('From', text='Из')
history_tree.heading('To', text='В')
history_tree.heading('Amount', text='Сумма')
history_tree.heading('Result', text='Результат')
history_tree.heading('Rate', text='Курс')
history_tree.column('From', width=80)
history_tree.column('To', width=80)
history_tree.column('Amount', width=100)
history_tree.column('Result', width=120)
history_tree.column('Rate', width=120)
history_tree.grid(row=4, column=0, columnspan=4, padx=10, pady=(10, 20), sticky="nsew")

# Загрузка истории при запуске
update_history_table()

root.mainloop()
