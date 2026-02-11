import tkinter as tk
from tkinter import messagebox
from main import start_dashboard, resource_path



def open_dashboard(login_window):
    username = user_entry.get()
    password = pass_entry.get()

    if password == "1234":

        if username.strip() == "":
            username = "User"   # fallback name

        messagebox.showinfo("Success", "Login Successful!")

        login_window.withdraw()
        start_dashboard(login_window, username)

    else:
        messagebox.showerror("Error", "Invalid Password")



login = tk.Tk()
login.title("Login")
login.geometry("400x300")
login.resizable(False, False)
login.iconbitmap(resource_path("icon01.ico"))

tk.Label(
    login,
    text="Expense Tracker Login",
    font=("Segoe UI", 16, "bold")
).pack(pady=20)

form = tk.Frame(login)
form.pack(pady=10)

tk.Label(form, text="Username").grid(row=0, column=0, pady=10)
user_entry = tk.Entry(form)
user_entry.focus()
user_entry.grid(row=0, column=1)

tk.Label(form, text="Password").grid(row=1, column=0, pady=10)
pass_entry = tk.Entry(form, show="*")
pass_entry.grid(row=1, column=1)

tk.Button(
    login,
    text="Login",
    width=15,
    command=lambda: open_dashboard(login)
).pack(pady=20)

login.mainloop()
