import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import pandas as pd # type: ignore
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS   # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
from operations import (
    add_expense,
    get_expenses,
    delete_expense,
    update_expense
)
from collections import Counter
from datetime import datetime
from PIL import Image, ImageTk


def start_dashboard(login_window, username):

    root = tk.Toplevel()
    root.lift()
    root.focus_force()
    root.title("Expense Tracker")
    root.geometry("1100x650")
    root.iconbitmap(resource_path("icon01.ico"))

    root.grab_set()

    # Close entire app properly
    root.protocol("WM_DELETE_WINDOW", login_window.destroy)

    # ================= MAIN FRAME =================
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # ================= SIDEBAR =================
    sidebar = tk.Frame(main_frame, bg="#2c3e50", width=250)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar,text="Expense Tracker",wraplength=220,bg="#2c3e50",fg="white",font=("Segoe UI", 16, "bold")).pack(pady=10)
    img = Image.open(resource_path("logo01.png"))
    img = img.resize((160, 160))
    logo_img = ImageTk.PhotoImage(img)

    logo_label = tk.Label(sidebar, image=logo_img, bg="#2c3e50")
    logo_label.image = logo_img
    logo_label.pack(pady=0)

    description = tk.Label(
        sidebar, text="Manage your daily expenses,\ntrack spending patterns,\nand make smarter financial decisions.",
        wraplength=200,      # VERY IMPORTANT (forces text inside sidebar)
        justify="left",
        bg="#2c3e50",
        fg="#dfe6e9",
        font=("Segoe UI", 14, "bold"),
        pady=15)
    description.pack(pady=5, padx=5)


    # ================= CONTENT =================
    content = tk.Frame(main_frame, bg="#ecf0f1")
    content.pack(side="left", fill="both", expand=True)

    tk.Label(
        content,
        text=f"Welcome, {username} 👋",
        font=("Segoe UI", 18, "bold"),
        bg="#ececf1",
        fg="#2c3e50",
    ).pack(pady=10)

    # ================= DASHBOARD CARDS =================
    dashboard_frame = tk.Frame(content, bg="#ecf0f1")
    dashboard_frame.pack(fill="x", pady=10)

    for i in range(3):
        dashboard_frame.grid_columnconfigure(i, weight=1)

    def create_card(parent, title, color, column):
        card = tk.Frame(parent, bg=color, height=160, highlightthickness=1, highlightbackground="#d0d0d0")
        
        card.grid(row=0,column=column, padx=30,pady=10, sticky="ew")
        card.grid_propagate(False)

        tk.Label(card, text=title, bg=color,font=("Arial", 14, "bold")).pack(pady=(18, 5))

        value = tk.Label(
            card,
            text="₹0",
            bg=color,
            font=("Arial", 18, "bold")
        )
        value.pack(pady=(5,18))

        return value

    total_label = create_card(dashboard_frame, "Total Spending 💲", "#E3F2FD",0)
    top_label = create_card(dashboard_frame, "Top Category 📌", "#FFF3E0",1)
    month_label = create_card(dashboard_frame, "This Month 📈", "#E8F5E9",2)
    
    def show_chart():
        expenses = get_expenses()

        if not expenses:
            messagebox.showinfo("No Data", "No expenses to show")
            return

        categories = {}
        for exp in expenses:
         categories[exp["category"]] = categories.get(exp["category"], 0) + exp["amount"]

        plt.figure(figsize=(6, 6))
        plt.pie(categories.values(),labels=categories.keys(),autopct="%1.1f%%")
        plt.title("Expense by Category")
        plt.show()


    def export_excel():
        expenses = get_expenses()

        if not expenses:
            messagebox.showinfo("No Data", "Nothing to export")
            return

        df = pd.DataFrame(expenses)
        df.to_excel("expenses.xlsx", index=False)

        messagebox.showinfo("Success", "Exported as expenses.xlsx")

    search_frame = tk.Frame(content, bg="#ecf0f1")
    search_frame.pack(pady=5)
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame,textvariable=search_var,width=35, font=("Segoe UI",11))
    search_entry.pack(ipady=4)
    search_entry.insert(0, " Search 🔍")

    def clear_placeholder(event):
        if search_entry.get() == " Search 🔍":
            search_entry.delete(0, tk.END)

    search_entry.bind("<FocusIn>", clear_placeholder)


    # ================= TABLE =================
    table_frame = tk.Frame(content)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)
    scrollbar_y = tk.Scrollbar(table_frame, width=40, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")
    columns = ( "Date", "Category", "Amount")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        #height=12,
        yscrollcommand=scrollbar_y.set,

    )

    for col in ("Date", "Category", "Amount"):
        tree.heading(col,text=col,command=lambda c=col: sort_column(c))

        tree.column(col, anchor="center", width=150)

    tree.pack(fill="both", expand=True)
    scrollbar_y.config(command=tree.yview)
    sort_state = {"Date": None,"Category": None,"Amount": None}
    def handle_click(event):

        row_id = tree.identify_row(event.y)

        if row_id:  
            # Row clicked → select it manually
            tree.selection_set(row_id)
            on_row_select(None)

        else:
            # Empty space clicked → clear selection
            tree.selection_remove(tree.selection())


    tree.bind("<Button-1>", handle_click)

    def sort_column(col):

        state = sort_state[col]
        # Reset all arrows first
        for c in sort_state:
            sort_state[c] = None
            tree.heading(c, text=c, command=lambda x=c: sort_column(x))

        # THIRD CLICK → restore original order
        if state is True:
            load_table()   # reload original data
            return
        data = []

        for child in tree.get_children():
            value = tree.set(child, col)

         # Convert amount properly
            if col == "Amount":
             value = float(value.replace("₹", ""))

            data.append((value, child))
        reverse = False if state is None else True
        data.sort(reverse=reverse)

        for index, (_, child) in enumerate(data):
            tree.move(child, "", index)

        # Toggle state
        sort_state[col] = reverse

        
     # Add arrow to current column
        arrow = "▲" if not reverse else "▼"
        tree.heading(col, text=f"{col} {arrow}", command=lambda: sort_column(col))
    
    def on_row_select(event=None):

        selected = tree.selection()

        if selected:
            values = tree.item(selected[0], "values")

            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, values[2].replace("₹",""))

            category.set(values[1])
    tree.bind("<<TreeviewSelect>>", on_row_select)

    
    # ================= FORM =================
    form = tk.Frame(content, bg="#ecf0f1")
    form.pack(pady=5)

    tk.Label(form, text="Amount:", bg="#ecf0f1").grid(row=0, column=0)
    amount_entry = tk.Entry(form)
    amount_entry.grid(row=0, column=1, padx=5)

    tk.Label(form, text="Category:", bg="#ecf0f1").grid(row=0, column=2)

    category = ttk.Combobox(
        form,
        values=["Food", "Travel", "Bills", "Shopping"],
        width=15
    )
    category.grid(row=0, column=3, padx=5)

    # ================= FUNCTIONS =================

    def load_table(search_text=""):
        
        for row in tree.get_children():
            tree.delete(row)
            
        expenses = get_expenses()
        search_text = search_text.strip().lower()

        if search_text:
            filtered = []
            text = search_text.lower()

            for e in expenses:
             # Convert everything to string and lowercase for comparison
                amt = str(e["amount"]).lower()
                cat = str(e["category"]).lower()
                date = str(e["date"][:10]).lower()

                if text in amt or text in cat or text in date:
                    filtered.append(e)

            expenses = filtered
            
        for exp in expenses:
            tree.insert(
                "",
                "end",
                iid=exp["id"],
                values=(
                    exp["date"][:10],
                    exp["category"],
                    f"₹{exp['amount']}"
                )
            )
        all_expenses = get_expenses()
        update_cards(all_expenses)
    
    def update_cards(expenses):

        if not expenses:
            total_label.config(text="₹0")
            top_label.config(text="None")
            month_label.config(text="₹0")
            return

        total = sum(e["amount"] for e in expenses)
        total_label.config(text=f"₹{total}")

        category_totals = {}

        for e in expenses:
            category = e["category"]
            amount = e["amount"]

            category_totals[category] = category_totals.get(category, 0) + amount

        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            top_label.config(text=top_category)
        else:
            top_label.config(text="None")


        current_month = datetime.now().strftime("%Y-%m")

        monthly_total = sum(
            e["amount"]
            for e in expenses
            if e["date"].startswith(current_month)
        )

        month_label.config(text=f"₹{monthly_total}")
    search_var.trace_add("write", lambda *args: load_table(search_var.get()))
    load_table()
    def add_ui():
        if not amount_entry.get() or not category.get():
            messagebox.showerror("Error", "Fill all fields")
            return

        add_expense(float(amount_entry.get()), category.get())

        amount_entry.delete(0, tk.END)
        category.set("")

        load_table()

    def delete_ui():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select expense")
            return

        delete_expense(selected[0])
        load_table()

    def edit_ui():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select expense")
            return

        update_expense(
            selected[0],
            float(amount_entry.get()),
            category.get()
        )

        load_table()

    # ================= BUTTONS =================
    btn_frame = tk.Frame(content, bg="#ecf0f1")
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Add", width=10, command=add_ui).grid(row=0, column=0, padx=15)
    tk.Button(btn_frame, text="🖊Edit", width=10, command=edit_ui).grid(row=0, column=1, padx=15)
    tk.Button(btn_frame, text="Delete", width=10, command=delete_ui).grid(row=0, column=2, padx=15)
    tk.Button(sidebar,text="Export Excel",width=25,command=export_excel, relief="flat",bd=0).pack(side="bottom",pady=25)
    tk.Button(sidebar,text="Show Chart",width=25,command=show_chart, relief="flat", bd=0).pack(side="bottom",pady=10)
    load_table()
