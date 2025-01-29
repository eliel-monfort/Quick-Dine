import sqlite3
import tkinter as tk
from tkinter import messagebox
import random

# Database Setup
def initialize_db():
    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()
    
    # Check if 'status' column exists in 'orders'
    cursor.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "status" not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'Pending'")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_size INTEGER,
            preferences TEXT,
            assigned BOOLEAN DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER,
            rating INTEGER,
            comments TEXT,
            FOREIGN KEY(table_id) REFERENCES tables(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_name TEXT,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()
def process_payment(amount):
    payment_success = random.choice([True, False])  # Simulating random payment success or failure
    return payment_success
   
# Tkinter Setup
class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("500x400")
        
        self.main_menu()
    
    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Restaurant Management", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Enter Group Size & Preferences", command=self.enter_group_info).pack(pady=10)
        tk.Button(self.root, text="Order a Meal", command=self.order_meal).pack(pady=10)
        tk.Button(self.root, text="Add Items to Order", command=self.add_items_to_order).pack(pady=10)
        tk.Button(self.root, text="Add Items to Menu", command=self.add_menu_item).pack(pady=10)
        tk.Button(self.root, text="Submit Feedback", command=self.submit_feedback).pack(pady=10)
        tk.Button(self.root, text="View Feedback", command=self.view_feedback).pack(pady=10)
        tk.Button(self.root, text="View Orders", command=self.view_orders).pack(pady=10)
        tk.Button(self.root, text="Process Payment", command=self.process_payment_ui).pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=10)
    
    def view_feedback(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Customer Feedback", font=("Arial", 14)).pack(pady=10)
        
        conn = sqlite3.connect("restaurant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback")
        feedback_entries = cursor.fetchall()
        conn.close()
        
        for feedback in feedback_entries:
            tk.Label(self.root, text=f"Table {feedback[1]} - Rating: {feedback[2]}/5 - {feedback[3]}").pack()
        
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=10)
    def add_menu_item(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Add Item to Menu", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Dish Name:").pack()
        dish_name_entry = tk.Entry(self.root)
        dish_name_entry.pack()
        
        tk.Label(self.root, text="Price:").pack()
        price_entry = tk.Entry(self.root)
        price_entry.pack()
        
        def save_menu_item():
            dish_name = dish_name_entry.get()
            price = price_entry.get()
            if dish_name and price.replace('.', '', 1).isdigit():
                conn = sqlite3.connect("restaurant.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO menu (dish_name, price) VALUES (?, ?)", (dish_name, float(price)))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Menu item added successfully!")
                self.main_menu()
            else:
                messagebox.showerror("Error", "Please enter a valid dish name and price")
        
        tk.Button(self.root, text="Add Item", command=save_menu_item).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)
    
    def order_meal(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Order a Meal", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Table ID:").pack()
        table_id_entry = tk.Entry(self.root)
        table_id_entry.pack()
        
        conn = sqlite3.connect("restaurant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu")
        menu_items = cursor.fetchall()
        conn.close()
        
        tk.Label(self.root, text="Select Dish:").pack()
        dish_var = tk.StringVar(self.root)
        dish_var.set(menu_items[0][1] if menu_items else "")
        dish_dropdown = tk.OptionMenu(self.root, dish_var, *[item[1] for item in menu_items])
        dish_dropdown.pack()
        
        def place_order():
            table_id = table_id_entry.get()
            dish_name = dish_var.get()
            if table_id.isdigit() and dish_name:
                conn = sqlite3.connect("restaurant.db")
                cursor = conn.cursor()
                cursor.execute("SELECT price FROM menu WHERE dish_name = ?", (dish_name,))
                price = cursor.fetchone()[0]
                cursor.execute("INSERT INTO orders (table_id, items, bill, status) VALUES (?, ?, ?, 'Pending')", (table_id, dish_name, price))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Order placed successfully!")
                self.main_menu()
            else:
                messagebox.showerror("Error", "Please enter a valid Table ID and select a dish")
        
        tk.Button(self.root, text="Submit Order", command=place_order).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)
    def process_payment_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Process Payment", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Table ID:").pack()
        table_id_entry = tk.Entry(self.root)
        table_id_entry.pack()
        
        def make_payment():
            table_id = table_id_entry.get()
            if table_id.isdigit():
                conn = sqlite3.connect("restaurant.db")
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(bill) FROM orders WHERE table_id = ?", (table_id,))
                total_bill = cursor.fetchone()[0]
                conn.close()
                
                if total_bill is None:
                    total_bill = 0.0
                
                if process_payment(total_bill):
                    messagebox.showinfo("Payment Success", f"Payment of ${total_bill:.2f} was successful!")
                else:
                    messagebox.showerror("Payment Failed", "Payment could not be processed. Please try again.")
            else:
                messagebox.showerror("Error", "Please enter a valid Table ID")
        
        tk.Button(self.root, text="Pay Now", command=make_payment).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)
    
    def submit_feedback(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Submit Feedback", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Table ID:").pack()
        table_id_entry = tk.Entry(self.root)
        table_id_entry.pack()
        
        tk.Label(self.root, text="Rating (1-5):").pack()
        rating_entry = tk.Entry(self.root)
        rating_entry.pack()
        
        tk.Label(self.root, text="Comments:").pack()
        comments_entry = tk.Entry(self.root)
        comments_entry.pack()
        
        def save_feedback():
            table_id = table_id_entry.get()
            rating = rating_entry.get()
            comments = comments_entry.get()
            if table_id.isdigit() and rating.isdigit() and 1 <= int(rating) <= 5:
                conn = sqlite3.connect("restaurant.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO feedback (table_id, rating, comments) VALUES (?, ?, ?)", (table_id, int(rating), comments))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Feedback submitted successfully!")
                self.main_menu()
            else:
                messagebox.showerror("Error", "Please enter valid Table ID and a rating between 1-5")
        
        tk.Button(self.root, text="Submit Feedback", command=save_feedback).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)
    def enter_group_info(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Enter Group Size & Preferences", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Group Size:").pack()
        group_size_entry = tk.Entry(self.root)
        group_size_entry.pack()
        
        tk.Label(self.root, text="Preferences:").pack()
        preferences_entry = tk.Entry(self.root)
        preferences_entry.pack()
        
        def save_group():
            group_size = group_size_entry.get()
            preferences = preferences_entry.get()
            if group_size.isdigit():
                conn = sqlite3.connect("restaurant.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM tables WHERE assigned = 0 LIMIT 1")
                available_table = cursor.fetchone()
                
                if available_table:
                    table_id = available_table[0]
                    cursor.execute("UPDATE tables SET group_size = ?, preferences = ?, assigned = 1 WHERE id = ?", 
                                   (group_size, preferences, table_id))
                    messagebox.showinfo("Success", f"Table {table_id} assigned successfully!")
                else:
                    cursor.execute("INSERT INTO tables (group_size, preferences, assigned) VALUES (?, ?, 1)", (group_size, preferences))
                    table_id = cursor.lastrowid
                    messagebox.showinfo("Success", f"New table {table_id} assigned successfully!")
                
                conn.commit()
                conn.close()
                self.main_menu()
            else:
                messagebox.showerror("Error", "Please enter a valid number for group size")
        
        tk.Button(self.root, text="Submit", command=save_group).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)
    def add_items_to_order(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Add Items to Existing Order", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Table ID:").pack()
        table_id_entry = tk.Entry(self.root)
        table_id_entry.pack()
        
        conn = sqlite3.connect("restaurant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu")
        menu_items = cursor.fetchall()
        conn.close()
        
        tk.Label(self.root, text="Select Additional Dish:").pack()
        dish_var = tk.StringVar(self.root)
        dish_var.set(menu_items[0][1])
        dish_dropdown = tk.OptionMenu(self.root, dish_var, *[item[1] for item in menu_items])
        dish_dropdown.pack()
        
        def update_order():
            table_id = table_id_entry.get()
            dish_name = dish_var.get()
            if table_id.isdigit():
                conn = sqlite3.connect("restaurant.db")
                cursor = conn.cursor()
                cursor.execute("SELECT price FROM menu WHERE dish_name = ?", (dish_name,))
                price = cursor.fetchone()[0]
                cursor.execute("UPDATE orders SET items = items || ', ' || ?, bill = bill + ? WHERE table_id = ?", (dish_name, price, table_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Item added to the order successfully!")
                self.main_menu()
            else:
                messagebox.showerror("Error", "Please enter a valid Table ID")
        
        tk.Button(self.root, text="Add Item", command=update_order).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)
    
    
    def view_orders(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Orders", font=("Arial", 14)).pack(pady=10)
        
        conn = sqlite3.connect("restaurant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            tk.Label(self.root, text=f"Order {order[0]}: Table {order[1]}, Items: {order[2]}, Bill: ${order[3]}").pack()
        
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=10)

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()
