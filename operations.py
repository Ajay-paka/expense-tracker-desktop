from database import connect_db, create_table

create_table()


def add_expense(amount, category):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, category) VALUES (?, ?)",
        (amount, category)
    )

    conn.commit()
    conn.close()


def get_expenses():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def delete_expense(expense_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))

    conn.commit()
    conn.close()


def update_expense(expense_id, amount, category):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET amount=?, category=?
        WHERE id=?
    """, (amount, category, expense_id))

    conn.commit()
    conn.close()
