import sympy as sp
import tkinter as tk
from tkinter import messagebox, Frame, Entry, Button, Label
import requests
import os
from tkinter import *
import sys
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

current_version = "v1.1"

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
            print("Вы используете последнюю версию :)")

    except Exception as e:
        print("Ошибка при проверке обновлений:", str(e))

check_for_updates()

def calculate_errors(formulas, variables):
    results = []
    derivative_exprs = []

    for formula in formulas:
        formula_value = formula.subs(variables)
        error_expr = sp.sqrt(
            sum((sp.diff(formula, var) * variables[f"delta_{var}"]) ** 2 for var in formula.free_symbols))
        error_value = error_expr.subs(variables)
        results.append((formula_value, error_value))

        derivative_expr = {var: sp.diff(formula, var) for var in formula.free_symbols}
        derivative_exprs.append(derivative_expr)

    return results, derivative_exprs

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

        output_text = ""
        for (value, error), formula in zip(results, formulas):
            output_text += f"Формула: {formula}\nЗначение: {value}\nПогрешность: {error}\n"

        messagebox.showinfo("Результаты вычислений", output_text)
        show_derivatives(derivatives)

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def draw_formula(formula, canvas, ax):
    ax.clear()
    ax.axis('off')
    ax.set_facecolor('#333')  # Устанавливаем цвет фона оси на темно-серый
    try:
        formula_sympy = sp.sympify(formula.strip('$'))  # Удаляем символы '$' из формулы
        formula_latex = sp.latex(formula_sympy)
        ax.text(0.5, 0.5, f"${formula_latex}$", fontsize=12, ha='center', va='center', color='white')
    except Exception:
        # Очищаем поле, если произошла ошибка, но не отображаем текст ошибки
        ax.clear()  # Очищаем ось, чтобы ничего не показывать
        ax.axis('off')  # Убираем ось

    canvas.draw()

def show_derivatives(derivatives):
    derivatives_window = tk.Toplevel(root)
    derivatives_window.title("Частные производные")
    derivatives_window.geometry("400x300")
    derivatives_window.configure(bg='#333')

    for idx, derivative in enumerate(derivatives):
        text = f"Частные производные для формулы {idx + 1}:\n"
        for var, deriv in derivative.items():
            text += f"∂({idx + 1})/∂({str(var)}) = {deriv}\n"

        label = Label(derivatives_window, text=text, bg='#333', fg='white', font=("Segoe UI", 12))
        label.pack(pady=10)

def add_placeholder(entry, placeholder_text):
    if not entry.get().strip():  # Если поле ввода пустое
        entry.insert(0, placeholder_text)  # Добавляем текст-подсказку
        entry.config(fg='gray', font=("Segoe UI", 13))  # Меняем цвет текста на серый для подсказки и уменьшаем размер шрифта

def remove_placeholder(entry, placeholder_text):
    if entry.get() == placeholder_text:  # Если текст равен подсказке
        entry.delete(0, tk.END)  # Очищаем поле ввода
        entry.config(fg='white', font=("Segoe UI", 13))  # Возвращаем цвет текста на белый и восстанавливаем размер шрифта

def add_formula():
    row_frame = Frame(formula_frame, bg='#333')
    row_frame.pack(pady=2, anchor="center")  # Уменьшаем pady с 5 до 2

    formula_input = Entry(row_frame, width=30, font=("Segoe UI", 14), bg='#444', fg='white', insertbackground='white')
    formula_input.pack(side=tk.LEFT)

    placeholder_text = "введите формулу..."  # Текст подсказки
    add_placeholder(formula_input, placeholder_text)  # Добавляем подсказку

    # Связываем события фокуса
    formula_input.bind("<FocusIn>", lambda event: remove_placeholder(formula_input, placeholder_text))
    formula_input.bind("<FocusOut>", lambda event: add_placeholder(formula_input, placeholder_text))

    remove_button = Button(row_frame, text='−', command=lambda: remove_formula(row_frame), fg='white', bg='red',
                           width=1, font=("Segoe UI", 10, "bold"), height=1)
    remove_button.pack(side=tk.LEFT, padx=5)

    formula_entries.append(formula_input)

    # Создаем фигуру и поле для рисования формулы
    fig, ax = plt.subplots(figsize=(2, 0.5))  # Размеры для рисования
    fig.patch.set_facecolor('#333')  # Устанавливаем цвет фона для всей фигуры
    ax.set_facecolor('#333')  # Установите цвет фона оси
    canvas = FigureCanvasTkAgg(fig, master=row_frame)
    canvas.get_tk_widget().pack(pady=(2, 0))  # Отступы
    draw_formula("", canvas, ax)

    # Связываем ввод формулы с функцией рисования
    formula_input.bind("<KeyRelease>", lambda event: draw_formula(formula_input.get(), canvas, ax))



def remove_formula(row_frame):
    row_frame.pack_forget()
    for formula_input in formula_entries:
        if formula_input.master == row_frame:
            formula_entries.remove(formula_input)
            break

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


def remove_variable(row_frame):
    row_frame.pack_forget()
    for var_name in variable_entries.keys():
        if variable_entries[var_name][0].master == row_frame:
            del variable_entries[var_name]
            break

# Инициализация GUI
root = tk.Tk()
root.title(f"Вычисление погрешностей - {current_version}")
root.geometry("700x500")
root.configure(bg='#333')

# Рамка для формул
formula_frame = Frame(root, bg='#333')
formula_frame.pack(pady=5, anchor="center")
tk.Label(formula_frame, text="Формулы:", bg='#333', fg='white', font=("Segoe UI", 16)).pack()
formula_entries = []

Button(formula_frame, text="Добавить формулу", command=add_formula, bg='#20b2aa', fg='white').pack(pady=5)

# Рамка для переменных
variable_frame = Frame(root, bg='#333')
variable_frame.pack(pady=5, anchor="center")
tk.Label(variable_frame, text="Переменные, их значения и дельты:", bg='#333', fg='white', font=("Segoe UI", 14)).pack()
variable_entries = {}
Button(variable_frame, text="Добавить переменную", command=add_variable, bg='#20b2aa', fg='white').pack(pady=5)

# Кнопка для запуска вычислений
calculate_button = Button(root, text="Вычислить", command=calculate, bg='#20b2aa', fg='white')
calculate_button.pack(pady=10)

# Запуск программы
root.mainloop()