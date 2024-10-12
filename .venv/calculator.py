import sympy as sp
import tkinter as tk
from tkinter import messagebox, Frame, Entry, Button, Label
import requests
import os
import sys
import subprocess

current_version = "v1.0"

def check_for_updates():
    repo_url = "https://api.github.com/repos/itsyourdecide/error-calculator/releases/latest"

    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release['tag_name']

        if latest_version != current_version:
            download_url = latest_release['assets'][0]['browser_download_url']
            headers = {'Accept': 'application/octet-stream'}
            download_response = requests.get(download_url, headers=headers)

            with open("new_version.exe", "wb") as f:
                f.write(download_response.content)


            subprocess.Popen(["new_version.exe"])
            sys.exit()
        else:
            print("Ви використовуєте останню версію :)")

    except Exception as e:
        print("Помилка під час перевірки оновлень:", str(e))

check_for_updates()

# Функція для обчислення похибок і часткових похідних
def calculate_errors(formulas, variables):
    results = []
    derivative_exprs = []  # Список для зберігання виразів часткових похідних

    for formula in formulas:
        formula_value = formula.subs(variables)  # Підставляємо значення змінних
        error_expr = sp.sqrt(
            sum((sp.diff(formula, var) * variables[f"delta_{var}"]) ** 2 for var in formula.free_symbols))
        error_value = error_expr.subs(variables)  # Підставляємо значення змінних і дельт у вираз похибки
        results.append((formula_value, error_value))  # Додаємо числове значення формули і похибки

        # Зберігаємо вирази часткових похідних
        derivative_expr = {var: sp.diff(formula, var) for var in formula.free_symbols}
        derivative_exprs.append(derivative_expr)

    return results, derivative_exprs  # Повертаємо вирази похідних


# Функція для обчислення похідних і похибок
def calculate():
    try:
        formulas = [sp.sympify(entry.get()) for entry in formula_entries]
        variables = {}
        for var, entry in variable_entries.items():
            var_name = var.get()
            var_value = float(entry[0].get())
            delta_value = float(entry[1].get())
            variables[sp.symbols(var_name)] = var_value
            variables[f"delta_{var_name}"] = delta_value

        results, derivatives = calculate_errors(formulas, variables)

        # Відображення результатів
        output_text = ""
        for (value, error), formula in zip(results, formulas):
            output_text += f"Формула: {formula}\nЗначення: {value}\nПохибка: {error}\n"

        # Показати результати у повідомленні
        messagebox.showinfo("Результати обчислень", output_text)

        # Показати часткові похідні
        show_derivatives(derivatives)

    except Exception as e:
        messagebox.showerror("Помилка", str(e))


# Функція для відображення часткових похідних
def show_derivatives(derivatives):
    derivatives_window = tk.Toplevel(root)
    derivatives_window.title("Часткові похідні")
    derivatives_window.geometry("400x300")
    derivatives_window.configure(bg='#333')

    for idx, derivative in enumerate(derivatives):
        text = f"Часткові похідні для формули {idx + 1}:\n"
        for var, deriv in derivative.items():
            text += f"∂({idx + 1})/∂({str(var)}) = {deriv}\n"  # Використовуємо str для виведення формули

        label = Label(derivatives_window, text=text, bg='#333', fg='white', font=("Segoe UI", 12))
        label.pack(pady=10)


# Функція для додавання формул
def add_formula():
    row_frame = Frame(formula_frame, bg='#333')
    row_frame.pack(pady=5, anchor="center")

    formula_input = Entry(row_frame, width=30, font=("Segoe UI", 14), bg='#444', fg='white', insertbackground='white')
    formula_input.pack(side=tk.LEFT)

    remove_button = Button(row_frame, text='−', command=lambda: remove_formula(row_frame), fg='white', bg='red',
                           width=1, font=("Segoe UI", 10, "bold"), height=1)
    remove_button.pack(side=tk.LEFT, padx=5)

    formula_entries.append(formula_input)


# Функція для видалення формули
def remove_formula(row_frame):
    row_frame.pack_forget()
    for formula_input in formula_entries:
        if formula_input.master == row_frame:
            formula_entries.remove(formula_input)
            break


# Функція для додавання змінних
def add_variable():
    row_frame = Frame(variable_frame, bg='#333')
    row_frame.pack(pady=5, anchor="center")

    var_name = Entry(row_frame, width=5, font=("Segoe UI", 14), bg='#444', fg='white', insertbackground='white')
    var_name.pack(side=tk.LEFT, padx=5)

    var_value = Entry(row_frame, width=10, font=("Segoe UI", 14), bg='#444', fg='white', insertbackground='white')
    var_value.pack(side=tk.LEFT, padx=5)

    delta_value = Entry(row_frame, width=10, font=("Segoe UI", 14), bg='#444', fg='white', insertbackground='white')
    delta_value.pack(side=tk.LEFT, padx=5)

    remove_button = Button(row_frame, text='−', command=lambda: remove_variable(row_frame), fg='white', bg='red',
                           width=1, font=("Segoe UI", 10, "bold"), height=1)
    remove_button.pack(side=tk.LEFT, padx=5)

    variable_entries[var_name] = [var_value, delta_value]


# Функція для видалення змінної
def remove_variable(row_frame):
    row_frame.pack_forget()
    for var_name in variable_entries.keys():
        if variable_entries[var_name][0].master == row_frame:
            del variable_entries[var_name]
            break


# Ініціалізація GUI
root = tk.Tk()
root.title(f"Обчислення похибок - {current_version}")
root.geometry("700x400")
root.configure(bg='#333')

# Рамка для формул
formula_frame = Frame(root, bg='#333')
formula_frame.pack(pady=10, anchor="center")
tk.Label(formula_frame, text="Формули:", bg='#333', fg='white', font=("Segoe UI", 16)).pack()
formula_entries = []

Button(formula_frame, text="Додати формулу", command=add_formula, bg='#20b2aa', fg='white').pack(pady=5)

# Рамка для змінних
variable_frame = Frame(root, bg='#333')
variable_frame.pack(pady=10, anchor="center")
tk.Label(variable_frame, text="Змінні та їх дельти:", bg='#333', fg='white', font=("Segoe UI", 16)).pack()
variable_entries = {}
Button(variable_frame, text="Додати змінну", command=add_variable, bg='#20b2aa', fg='white').pack(pady=5)

# Кнопка для запуску обчислень
calculate_button = Button(root, text="Обчислити", command=calculate, bg='#20b2aa', fg='white')
calculate_button.pack(pady=20)

# Запуск програми
root.mainloop()
