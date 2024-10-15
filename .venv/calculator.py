import sympy as sp
import tkinter as tk
from tkinter import messagebox, Frame, Entry, Button, Label, ttk
import requests
import sys
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

current_version = "v1.1"


def check_for_updates():
    repo_url = "https://api.github.com/repos/itsyourdecide/error-calculator/releases/latest"
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release['tag_name']

        if latest_version != current_version:
            if messagebox.askyesno("Доступно обновление", f"Найдена новая версия {latest_version}. Установить?"):
                download_url = latest_release['assets'][0]['browser_download_url']
                threading.Thread(target=download_update, args=(download_url,)).start()
        else:
            print("Вы используете последнюю версию :)")
    except Exception as e:
        print("Ошибка при проверке обновлений:", str(e))


def download_update(url):
    progress_window = tk.Toplevel(root)
    progress_window.title("Загрузка обновления")
    progress_window.geometry("300x100")
    progress_window.configure(bg='#333')

    label = tk.Label(progress_window, text="Загрузка...", bg='#333', fg='white', font=("Segoe UI", 12))
    label.pack(pady=10)

    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=200, mode="determinate")
    progress_bar.pack(pady=10)

    new_file_path = "new_version.exe"

    def update_progress(downloaded, total_size):
        progress_bar['value'] = min((downloaded / total_size) * 100, 100)
        progress_window.update_idletasks()

    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(new_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    update_progress(downloaded_size, total_size)

        label.config(text="Установка...")
        progress_bar['value'] = 100
        progress_window.update_idletasks()
        install_update(new_file_path, progress_window)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при загрузке обновления: {str(e)}")


def install_update(new_file_path, progress_window):
    current_file_path = sys.argv[0]
    try:
        subprocess.Popen(f"timeout 1 && move /Y {new_file_path} {current_file_path}", shell=True)
        progress_window.destroy()
        sys.exit()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при установке обновления: {str(e)}")


def calculate_errors(formulas, variables):
    results = []
    for formula in formulas:
        formula_value = formula.subs(variables)
        error_expr = sp.sqrt(
            sum((sp.diff(formula, var) * variables[f"delta_{var}"]) ** 2 for var in formula.free_symbols))
        error_value = error_expr.subs(variables)
        results.append((formula_value, error_value))
    return results


def calculate():
    try:
        formulas = [sp.sympify(entry.get()) for entry in formula_entries]
        variables = {sp.symbols(var.get()): (float(entry[0].get()), float(entry[1].get())) for var, entry in
                     variable_entries.items()}

        results = calculate_errors(formulas, {var: value for var, (value, delta) in variables.items()})
        output_text = "\n".join(
            f"Формула: {formula}\nЗначение: {value}\nПогрешность: {error}" for (value, error), formula in
            zip(results, formulas))

        messagebox.showinfo("Результаты вычислений", output_text)
        show_derivatives(formulas, variables)

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def draw_formula(formula, canvas, ax):
    ax.clear()
    ax.axis('off')
    ax.set_facecolor('#333')
    try:
        formula_sympy = sp.sympify(formula.strip('$'))
        ax.text(0.5, 0.5, f"${sp.latex(formula_sympy)}$", fontsize=12, ha='center', va='center', color='white')
    except Exception:
        ax.clear()
        ax.axis('off')
    canvas.draw()


def show_derivatives(formulas, variables):
    derivatives_window = tk.Toplevel(root)
    derivatives_window.title("Частные производные")
    derivatives_window.geometry("400x300")
    derivatives_window.configure(bg='#333')

    for idx, formula in enumerate(formulas):
        derivative_text = f"Частные производные для формулы {idx + 1}:\n"
        for var in formula.free_symbols:
            derivative = sp.diff(formula, var)
            derivative_text += f"∂({idx + 1})/∂({str(var)}) = {derivative}\n"

        label = Label(derivatives_window, text=derivative_text, bg='#333', fg='white', font=("Segoe UI", 12))
        label.pack(pady=10)


def add_placeholder(entry, placeholder_text):
    if not entry.get().strip():
        entry.insert(0, placeholder_text)
        entry.config(fg='gray', font=("Segoe UI", 13))


def remove_placeholder(entry, placeholder_text):
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.config(fg='white', font=("Segoe UI", 13))


def add_formula():
    row_frame = Frame(formula_frame, bg='#333')
    row_frame.pack(pady=2, anchor="center")

    formula_input = Entry(row_frame, width=30, font=("Segoe UI", 14), bg='#444', fg='white', insertbackground='white')
    formula_input.pack(side=tk.LEFT)

    placeholder_text = "введите формулу..."
    add_placeholder(formula_input, placeholder_text)

    formula_input.bind("<FocusIn>", lambda event: remove_placeholder(formula_input, placeholder_text))
    formula_input.bind("<FocusOut>", lambda event: add_placeholder(formula_input, placeholder_text))

    remove_button = Button(row_frame, text='−', command=lambda: remove_formula(row_frame), fg='white', bg='red',
                           width=1, font=("Segoe UI", 10, "bold"), height=1)
    remove_button.pack(side=tk.LEFT, padx=5)

    formula_entries.append(formula_input)

    fig, ax = plt.subplots(figsize=(3, 0.5))
    fig.patch.set_facecolor('#333')
    ax.set_facecolor('#333')
    canvas = FigureCanvasTkAgg(fig, master=row_frame)
    canvas.get_tk_widget().pack(pady=(2, 0))
    draw_formula("", canvas, ax)

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

Button(formula_frame, text="Добавить формулу", command=add_formula, bg='#20b2aa', fg='white').pack()

# Рамка для переменных
variable_frame = Frame(root, bg='#333')
variable_frame.pack(pady=5, anchor="center")
tk.Label(variable_frame, text="Переменные:", bg='#333', fg='white', font=("Segoe UI", 16)).pack()
variable_entries = {}

Button(variable_frame, text="Добавить переменную", command=add_variable, bg='#20b2aa', fg='white').pack()

# Кнопка для вычисления
Button(root, text="Вычислить", command=calculate, bg='#008080', fg='white', font=("Segoe UI", 10)).pack(pady=5)

check_for_updates()
root.mainloop()
