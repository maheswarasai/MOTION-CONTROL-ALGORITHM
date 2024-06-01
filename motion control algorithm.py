import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import serial
from serial.tools import list_ports
import time
class LoginPage(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("Login Page")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode

        # Create a frame to contain the login widgets
        login_frame = tk.Frame(self, bg="white")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Username Label and Entry
        username_label = tk.Label(login_frame, text="Username:", bg="white", fg="black", font=("Arial", 12, "bold"))
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        # Password Label and Entry
        password_label = tk.Label(login_frame, text="Password:", bg="white", fg="black", font=("Arial", 12, "bold"))
        password_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        # Login Button
        login_button = tk.Button(login_frame, text="Login", command=self.login, font=("Arial", 12, "bold"), bg="blue", fg="white")
        login_button.grid(row=2, columnspan=2, pady=10)
        login_button.bind("<Enter>", self.on_enter)  # Bind mouse hover event
        login_button.bind("<Leave>", self.on_leave)  # Bind mouse leave event

        # Close Button
        close_button = tk.Button(login_frame, text="Close", command=self.close_window, font=("Arial", 12, "bold"), bg="red", fg="white")
        close_button.grid(row=3, columnspan=2, pady=10)

        # Connect to the existing users table
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()

    def on_enter(self, event):
        # Function to change button color on mouse hover
        event.widget.config(bg="light blue")

    def on_leave(self, event):
        # Function to change button color back on mouse leave
        event.widget.config(bg="blue")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the user is admin
        if username == "admin" and password == "password":
            admin_panel = AdminPanel(self)
            self.withdraw()
            admin_panel.mainloop()
         # Check if the user is stock user
        elif username == "stock" and password == "stock":
            stock_page = StockPage(self)  # Pass the LoginPage instance to StockPage
            self.withdraw()  # Hide the login page window
            stock_page.mainloop()
        else:
            self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = self.cursor.fetchone()
            if user:
                user_open_page = UserOpenPage(user[1], self)
                self.withdraw()
                user_open_page.mainloop()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_login_page(self):
        self.deiconify()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
    def close_window(self):
        self.destroy()


class AdminPanel(tk.Toplevel):
    def _init_(self, login_page):
        super()._init_(login_page)
        self.title("Admin Panel")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode
        self.login_page = login_page

        # Create a frame to contain the admin panel widgets
        admin_frame = tk.Frame(self, bg="white")
        admin_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Add User Button
        self.add_user_button = tk.Button(admin_frame, text="Add User", command=self.add_user, font=("Arial", 12), bg="green", fg="white")
        self.add_user_button.grid(row=0, column=0, padx=10, pady=5)

        # Delete User Button
        self.delete_user_button = tk.Button(admin_frame, text="Delete User", command=self.delete_user, font=("Arial", 12), bg="red", fg="white")
        self.delete_user_button.grid(row=1, column=0, padx=10, pady=5)
        
        # Logout Button
        logout_button = tk.Button(admin_frame, text="Logout", command=self.logout, font=("Arial", 12), bg="blue", fg="white")
        logout_button.grid(row=2, column=0, padx=10, pady=10)
        self.bind("<Control-l>", lambda event: self.logout())  # Bind Ctrl+L for logout

        # Connect to the database
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()

    def add_user(self):
        # Open a new window to add a user
        self.add_user_window = tk.Toplevel(self)
        self.add_user_window.title("Add User")
        self.add_user_window.geometry("250x200")

        # Name Label and Entry
        tk.Label(self.add_user_window, text="Name:").pack()
        self.name_entry = tk.Entry(self.add_user_window)
        self.name_entry.pack()

        # Date of Birth Label and Entry
        tk.Label(self.add_user_window, text="Date of Birth (YYYY-MM-DD):").pack()
        self.dob_entry = tk.Entry(self.add_user_window)
        self.dob_entry.pack()

        # Username Label and Entry
        tk.Label(self.add_user_window, text="Username:").pack()
        self.username_entry = tk.Entry(self.add_user_window)
        self.username_entry.pack()

        # Password Label and Entry
        tk.Label(self.add_user_window, text="Password:").pack()
        self.password_entry = tk.Entry(self.add_user_window, show="*")
        self.password_entry.pack()

        # Add User Button
        tk.Button(self.add_user_window, text="Add", command=self.save_user).pack(pady=5)

    def save_user(self):
        # Get user details
        name = self.name_entry.get()
        dob = self.dob_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Insert user into the database
        self.cursor.execute("INSERT INTO users (customer_name, dob, username, password) VALUES (?, ?, ?, ?)",
                            (name, dob, username, password))
        self.conn.commit()

        # Close the add user window
        self.add_user_window.destroy()


    def delete_user(self):
        # Open a new window to select and delete a user
        self.delete_user_window = tk.Toplevel(self)
        self.delete_user_window.title("Delete User")
        self.delete_user_window.geometry("250x150")

        # Get the list of users from the database
        self.cursor.execute("SELECT username FROM users")
        users = self.cursor.fetchall()
        user_list = [user[0] for user in users]

        # User Label and Combobox
        tk.Label(self.delete_user_window, text="Select User:").pack()
        self.user_combo = ttk.Combobox(self.delete_user_window, values=user_list)
        self.user_combo.pack()

        # Delete User Button
        tk.Button(self.delete_user_window, text="Delete", command=self.confirm_delete).pack(pady=5)

    def confirm_delete(self):
        # Get the selected user
        selected_user = self.user_combo.get()

        # Confirm user deletion
        confirm = messagebox.askyesno("Delete User", f"Are you sure you want to delete user '{selected_user}'?")

        if confirm:
            # Delete user from the database
            self.cursor.execute("DELETE FROM users WHERE username=?", (selected_user,))
            self.conn.commit()
            messagebox.showinfo("Success", "User deleted successfully.")

            # Close the delete user window
            self.delete_user_window.destroy()
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.destroy()  # Destroy the admin panel window
            self.login_page.show_login_page()  # Call show_login_page from the login_page instance

class UserOpenPage(tk.Tk):
    def _init_(self, username, login_page):
        super()._init_()
        self.title("User Open Page")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode

        self.username = username
        self.login_page = login_page

        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()

        # Background color
        self.config(bg="lightblue")

        # Welcome message label
        self.user_label = tk.Label(self, text=f"Welcome, {self.username}", font=("Helvetica", 24), bg="lightblue")
        self.user_label.pack(pady=50)

        # Buttons with improved UI
        button_styles = {
            "font": ("Arial", 18),
            "bg": "#4CAF50",  # Green
            "fg": "white",
            "padx": 20,
            "pady": 10,
            "bd": 0,  # No border
            "highlightthickness": 0,  # No highlight
            "activebackground": "#45a049",  # Darker shade of green on hover
            "activeforeground": "white"
        }
        button_margin = {"padx": 20, "pady": 10}

        tk.Button(self, text="Inventory Management", command=self.open_inventory, **button_styles).pack(side="top", fill="x", **button_margin)
        tk.Button(self, text="Billing", command=self.open_billing, **button_styles).pack(side="top", fill="x", **button_margin)
        tk.Button(self, text="Logout", command=self.logout, **button_styles).pack(side="top", fill="x", **button_margin)

    def open_inventory(self):
        inventory_page = InventoryPage(self)
        self.withdraw()
        inventory_page.mainloop()

    def open_billing(self):
        user_billing_page = UserBillingPage(self)
        self.withdraw()
        user_billing_page.mainloop()

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.destroy()
            self.login_page.show_login_page()


class InventoryPage(tk.Tk):
    def _init_(self, user_open_page):
        super()._init_()
        self.title("Inventory Page")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode

        self.user_open_page = user_open_page

        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()

        # Search Bar
        search_frame = tk.Frame(self, bg="#3498DB")
        search_frame.pack(side=tk.TOP, fill=tk.X)

        search_label = tk.Label(search_frame, text="Search Medicine:", font=("Arial", 14), bg="#3498DB", fg="white")
        search_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 14))
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.search_button = tk.Button(search_frame, text="Search", command=self.search_medicine, font=("Arial", 12), bg="#2ECC71", fg="white")
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Inventory Table
        self.inventory_table = ttk.Treeview(self)
        self.inventory_table["columns"] = ("ID", "Name", "Composition", "Batch", "Expire Date", "Stock", "Price", "Manufacturer")
        self.inventory_table.heading("ID", text="ID")
        self.inventory_table.heading("Name", text="Name")
        self.inventory_table.heading("Composition", text="Composition")
        self.inventory_table.heading("Batch", text="Batch")
        self.inventory_table.heading("Expire Date", text="Expire Date")
        self.inventory_table.heading("Stock", text="Stock")
        self.inventory_table.heading("Price", text="Price")
        self.inventory_table.heading("Manufacturer", text="Manufacturer")

        self.inventory_table_scroll = tk.Scrollbar(self, orient="vertical", command=self.inventory_table.yview)
        self.inventory_table.configure(yscrollcommand=self.inventory_table_scroll.set)

        self.inventory_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.inventory_table_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Back Button
        self.back_button = tk.Button(self, text="Back", command=self.back, font=("Arial", 12), bg="#E74C3C", fg="white")
        self.back_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.show_inventory()

    def show_inventory(self):
        self.cursor.execute("SELECT * FROM medicines")
        medicines = self.cursor.fetchall()
        for medicine in medicines:
            self.inventory_table.insert("", tk.END, values=medicine)

    def search_medicine(self):
        search_term = self.search_var.get()
        self.inventory_table.delete(*self.inventory_table.get_children())  # Clear previous search results

        # Fetch medicines matching the search term from the database
        self.cursor.execute("SELECT * FROM medicines WHERE Name LIKE ?", (f'%{search_term}%',))
        medicines = self.cursor.fetchall()
        for medicine in medicines:
            self.inventory_table.insert("", tk.END, values=medicine)

    def back(self):
        self.destroy()
        self.user_open_page.deiconify()

class UserBillingPage(tk.Tk):
    def _init_(self, user_open_page):
        super()._init_()
        self.title("Billing Page")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode

        self.user_open_page = user_open_page  # Store the user open page reference

        # Connect to the existing pharmacy database
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()
        
        self.serial_port = None  # Initialize serial port as None
        self.serial_status_label = tk.Label(self, text="Serial Port Status: Not Connected", font=("Arial", 14), bg="lightblue", fg="black")
        self.serial_status_label.pack()

        # Main Frame
        main_frame = tk.Frame(self, bg="lightblue")  # Set background color
        main_frame.pack(expand=True, fill="both")

        # Customer Name Label and Entry
        customer_name_label = tk.Label(main_frame, text="Customer Name:", font=("Arial", 14), bg="lightblue", fg="black")
        customer_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.customer_name_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.customer_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Mobile Number Label and Entry
        mobile_number_label = tk.Label(main_frame, text="Mobile Number:", font=("Arial", 14), bg="lightblue", fg="black")
        mobile_number_label.grid(row=0, column=2, padx=10, pady=10)
        self.mobile_number_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.mobile_number_entry.grid(row=0, column=3, padx=10, pady=10)

        # Search Medicine Label and Entry
        search_label = tk.Label(main_frame, text="Search Medicine:", font=("Arial", 14), bg="lightblue", fg="black")
        search_label.grid(row=1, column=0, padx=10, pady=10)
        self.search_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.search_entry.grid(row=1, column=1, padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.autocomplete_medicine)

        # Suggestions Listbox
        self.suggestions_listbox = tk.Listbox(main_frame, font=("Arial", 12), width=50)
        self.suggestions_listbox.grid(row=2, column=0, columnspan=4, padx=10, pady=10)
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.select_medicine_from_suggestions)

        # Available Quantity Label and Price Label
        self.available_quantity_label = tk.Label(main_frame, text="", font=("Arial", 12), bg="lightblue", fg="black")
        self.available_quantity_label.grid(row=3, column=0, padx=10, pady=5, columnspan=2)
        self.price_label = tk.Label(main_frame, text="", font=("Arial", 12), bg="lightblue", fg="black")
        self.price_label.grid(row=3, column=2, padx=10, pady=5, columnspan=2)

        # Quantity Label and Entry
        quantity_label = tk.Label(main_frame, text="Quantity:", font=("Arial", 14), bg="lightblue", fg="black")
        quantity_label.grid(row=4, column=0, padx=10, pady=10)
        self.quantity_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.quantity_entry.grid(row=4, column=1, padx=10, pady=10)

        # Add to Cart Button
        add_to_cart_button = tk.Button(main_frame, text="Add to Cart", command=self.add_to_cart, font=("Arial", 12))
        add_to_cart_button.grid(row=4, column=2, padx=10, pady=10)

        # Cart Listbox
        self.cart_listbox = tk.Listbox(main_frame, font=("Arial", 12), width=50)
        self.cart_listbox.grid(row=5, column=0, columnspan=4, padx=10, pady=10)
        
        # Select Serial Port Label and Dropdown
        serial_port_label = tk.Label(main_frame, text="Select Serial Port:", font=("Arial", 14), bg="lightblue", fg="black")
        serial_port_label.grid(row=0, column=4, padx=10, pady=10)
        self.serial_port_var = tk.StringVar()
        self.serial_port_dropdown = tk.OptionMenu(main_frame, self.serial_port_var, *self.get_available_serial_ports())
        self.serial_port_dropdown.grid(row=0, column=5, padx=10, pady=10)

        # Connect Serial Port Button
        connect_serial_button = tk.Button(main_frame, text="Connect Serial Port", command=self.connect_serial_port, font=("Arial", 12))
        connect_serial_button.grid(row=0, column=6, padx=10, pady=10)

        # Payment Mode Checkboxes
        self.payment_mode_var = tk.StringVar()
        payment_mode_label = tk.Label(main_frame, text="Select Payment Mode:", font=("Arial", 14), bg="lightblue", fg="black")
        payment_mode_label.grid(row=6, column=0, padx=10, pady=10)
        cash_checkbox = tk.Checkbutton(main_frame, text="Cash", variable=self.payment_mode_var, onvalue="Cash", font=("Arial", 12), bg="lightblue", fg="black")
        cash_checkbox.grid(row=6, column=1, padx=10, pady=10)
        upi_checkbox = tk.Checkbutton(main_frame, text="UPI", variable=self.payment_mode_var, onvalue="UPI", font=("Arial", 12), bg="lightblue", fg="black")
        upi_checkbox.grid(row=6, column=2, padx=10, pady=10)
        card_checkbox = tk.Checkbutton(main_frame, text="Card/Debit", variable=self.payment_mode_var, onvalue="Card/Debit", font=("Arial", 12), bg="lightblue", fg="black")
        card_checkbox.grid(row=6, column=3, padx=10, pady=10)

        # Overall Price Label
        self.overall_price_label = tk.Label(main_frame, text="Overall Price: $0.00", font=("Arial", 14), bg="lightblue", fg="black")
        self.overall_price_label.grid(row=7, column=0, padx=10, pady=10, columnspan=4)

        # Proceed to Dispatch Button
        self.proceed_button = tk.Button(main_frame, text="Proceed to Dispatch", command=self.proceed_to_dispatch, font=("Arial", 14))
        self.proceed_button.grid(row=8, column=0, padx=10, pady=10, columnspan=4)

        # Bind keyboard shortcut to go back to the UserOpenPage
        self.bind("<Escape>", lambda event: self.go_back())
        
         # Periodically update serial port status
        self.update_serial_status()
    def autocomplete_medicine(self, event=None):
        # Function to provide suggestions for medicine search
        search_term = self.search_entry.get()
        self.suggestions_listbox.delete(0, tk.END)  # Clear previous suggestions

        if search_term:
            # Fetch medicines matching the search term from the inventory table
            self.cursor.execute("SELECT medicine_name, stock_quantity, price FROM medicines WHERE medicine_name LIKE ?", (f'%{search_term}%',))
            medicines = self.cursor.fetchall()
            for medicine in medicines:
                medicine_info = f"{medicine[0]} - Quantity: {medicine[1]} - Price: {medicine[2]}"
                self.suggestions_listbox.insert(tk.END, medicine_info)

    def select_medicine_from_suggestions(self, event=None):
        # Function to select a medicine from the suggestions list
        selection = self.suggestions_listbox.curselection()
        if selection:
            selected_medicine_info = self.suggestions_listbox.get(selection[0])
            selected_medicine = selected_medicine_info.split(" - ")[0]  # Extract medicine name
            available_quantity = selected_medicine_info.split(" - ")[1].split(": ")[1]  # Extract available quantity
            price = selected_medicine_info.split(" - ")[2].split(": ")[1]  # Extract price
            self.available_quantity_label.config(text=f"Available Quantity: {available_quantity}")
            self.price_label.config(text=f"Price: ${price}")

    def add_to_cart(self):
        # Function to add selected medicine to the cart
        if self.suggestions_listbox.curselection():
            selected_medicine_info = self.suggestions_listbox.get(self.suggestions_listbox.curselection()[0])
            selected_medicine = selected_medicine_info.split(" - ")[0]
            selected_quantity = int(self.quantity_entry.get())
            available_quantity = int(selected_medicine_info.split(" - ")[1].split(": ")[1])

            if selected_quantity <= available_quantity:
                self.cart_listbox.insert(tk.END, f"{selected_medicine} - Quantity: {selected_quantity}")
                self.update_overall_price(selected_quantity)
                self.quantity_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Selected quantity is not available.")
        else:
            messagebox.showerror("Error", "Please select a medicine from the suggestions.")


    def update_overall_price(self, quantity):
        # Function to update overall price
        price = float(self.price_label.cget("text").split("$")[1])
        overall_price = float(self.overall_price_label.cget("text").split("$")[1])
        overall_price += price * quantity
        self.overall_price_label.config(text=f"Overall Price: ${overall_price:.2f}")

    def proceed_to_dispatch(self):
        # Function to proceed to dispatch
        count = self.cart_listbox.size()  # Get the number of items in the listbox
        data = str(count) + ";"
        for item in self.cart_listbox.get(0, tk.END):
            medicine_name = item.split(" - ")[0]
            quantity = int(item.split(" - ")[1].split(": ")[1])
            # Query the database to get the medicine ID
            self.cursor.execute("SELECT id FROM medicines WHERE medicine_name=?", (medicine_name,))
            result = self.cursor.fetchone()
            if result:
                medicine_id = result[0]
                data += f"{medicine_id}:{quantity};"
        self.send_data_to_arduino(data)  # Modified the function call here
        print("Data sent to Arduino successfully.")

        response = self.receive_response_from_arduino()  # Modified the function call here
        print("Response from Arduino:", response)
        if response == "Success":
            print("Arduino successfully received and processed the data.")
            for item in self.cart_listbox.get(0, tk.END):
                medicine_name = item.split(" - ")[0]
                quantity = int(item.split(" - ")[1].split(": ")[1])
                self.reduce_quantity_in_inventory(medicine_name, quantity)
            messagebox.showinfo("Success", "Medicines dispatched successfully.")
            self.reset_page()

    def send_data_to_arduino(self, data):
        self.serial_port.write(data.encode())

    def receive_response_from_arduino(self):
        response = self.serial_port.readline().decode().strip()
        return response
    def get_available_serial_ports(self):
        # Function to get a list of available serial ports
        available_ports = []
        for port in serial.tools.list_ports.comports():
            available_ports.append(port.device)
        return available_ports


    def connect_serial_port(self):
        # Function to connect to the selected serial port
        selected_port = self.serial_port_var.get()
        if selected_port:
            try:
                self.serial_port = serial.Serial(selected_port, 115200)
                time.sleep(2)  # Wait for the serial connection to initialize
                self.serial_status_label.config(text=f"Serial Port Status: Connected to {selected_port}")
            except serial.SerialException:
                messagebox.showerror("Error", f"Failed to connect to {selected_port}")
        else:
            messagebox.showerror("Error", "Please select a serial port")
    def update_serial_status(self):
        # Function to update the serial port status periodically
        if self.serial_port and self.serial_port.isOpen():
            self.serial_status_label.config(text="Serial Port Status: Connected")
        else:
            self.serial_status_label.config(text="Serial Port Status: Not Connected")
        self.after(1000, self.update_serial_status)  # Schedule the update after 1 second

    def reduce_quantity_in_inventory(self, medicine_name, quantity_sold):
        # Function to reduce the quantity of a medicine in inventory
        current_quantity = self.get_available_quantity(medicine_name)
        updated_quantity = current_quantity - quantity_sold
        if updated_quantity >= 0:
            self.cursor.execute("UPDATE medicines SET stock_quantity = ? WHERE medicine_name = ?", (updated_quantity, medicine_name))
            self.conn.commit()
        else:
            messagebox.showwarning("Invalid Quantity", f"Invalid quantity for {medicine_name}")

    def get_available_quantity(self, medicine_name):
        # Function to get available quantity of a medicine from the database
        self.cursor.execute("SELECT stock_quantity FROM medicines WHERE medicine_name=?", (medicine_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0  # If medicine not found, return 0 quantity
    def check_payment_selection(self):
        # Function to check if any payment mode is selected and enable/disable the "Proceed to Dispatch" button accordingly
        if self.payment_mode_var.get() != "":
            self.proceed_button.config(state=tk.NORMAL)
        else:
            self.proceed_button.config(state=tk.DISABLED)

    def reset_page(self):
        # Function to reset the page
        self.customer_name_entry.delete(0, tk.END)
        self.mobile_number_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.suggestions_listbox.delete(0, tk.END)
        self.available_quantity_label.config(text="")
        self.price_label.config(text="")
        self.cart_listbox.delete(0, tk.END)
        self.overall_price_label.config(text="Overall Price: $0.00")
        
    def go_back(self, event=None):
        # Functionality to go back to the UserOpenPage
        self.destroy()  # Destroy the billing page window
        self.user_open_page.deiconify()  # Show the UserOpenPage window
class StockPage(tk.Tk):
    def _init_(self, user_open_page):
        super()._init_()
        self.title("Stock Page")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode

        self.user_open_page = user_open_page  # Store the user open page reference

        # Connect to the existing pharmacy database
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()

        # Main Frame with Background Color
        main_frame = tk.Frame(self, bg="#E5E8E8")
        main_frame.pack(expand=True, fill="both")

        # Title Label
        title_label = tk.Label(main_frame, text="Stock Page", font=("Arial", 24, "bold"), bg="#E5E8E8", fg="#0E6EB8")
        title_label.pack(pady=20)

        # Inventory Management Button
        inventory_button = tk.Button(main_frame, text="Inventory Management", command=self.open_inventory_management, font=("Arial", 16), bg="#4CAF50", fg="white")
        inventory_button.pack(pady=10)

        # Remove Expired Stock Button
        remove_expired_button = tk.Button(main_frame, text="Remove Expired Stock", command=self.remove_expired_stock, font=("Arial", 16), bg="#FF5733", fg="white")
        remove_expired_button.pack(pady=10)

        # Back Button
        back_button = tk.Button(main_frame, text="Back", command=self.go_back, font=("Arial", 16), bg="#34495E", fg="white")
        back_button.pack(pady=10)

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def open_inventory_management(self):
        # Functionality to open the inventory management page
        inventory_management_page = InventoryManagementPage(self)
        self.withdraw()  # Hide the stock page window
        inventory_management_page.mainloop()

    def remove_expired_stock(self):
        # Functionality to remove expired stock from the inventory
        # Placeholder for actual implementation
        messagebox.showinfo("Remove Expired Stock", "Expired stock removed successfully.")

    def go_back(self):
        # Functionality to go back to the user open page
        self.destroy()  # Destroy the stock page window
        self.user_open_page.deiconify()  # Show the user open page
class InventoryManagementPage(tk.Tk):
    def _init_(self, user_open_page):
        super()._init_()
        self.title("Inventory Management")
        self.attributes("-fullscreen", True)  # Set the window to full-screen mode

        self.user_open_page = user_open_page  # Store the user open page reference

        # Connect to the existing pharmacy database
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()

        # Main Frame with Background Color
        main_frame = tk.Frame(self, bg="lightblue")
        main_frame.pack(expand=True, fill="both")

        # Scrollbar
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", bg="lightblue")
        scrollbar.pack(side="right", fill="y")

        # Inventory Frame
        inventory_frame = tk.Frame(main_frame, bg="lightblue")
        inventory_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Labels and Entries for adding new medicine
        tk.Label(inventory_frame, text="Medicine Name:", font=("Arial", 14), bg="lightblue").grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.med_name_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.med_name_entry.grid(row=0, column=1, pady=5, padx=10, sticky="w")

        tk.Label(inventory_frame, text="Composition:", font=("Arial", 14), bg="lightblue").grid(row=1, column=0, pady=5, padx=10, sticky="w")
        self.composition_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.composition_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        tk.Label(inventory_frame, text="Batch Number:", font=("Arial", 14), bg="lightblue").grid(row=2, column=0, pady=5, padx=10, sticky="w")
        self.batch_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.batch_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")

        tk.Label(inventory_frame, text="Expire Date (YYYY-MM-DD):", font=("Arial", 14), bg="lightblue").grid(row=3, column=0, pady=5, padx=10, sticky="w")
        self.expire_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.expire_entry.grid(row=3, column=1, pady=5, padx=10, sticky="w")

        tk.Label(inventory_frame, text="Stock Quantity:", font=("Arial", 14), bg="lightblue").grid(row=4, column=0, pady=5, padx=10, sticky="w")
        self.stock_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.stock_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")

        tk.Label(inventory_frame, text="Price:", font=("Arial", 14), bg="lightblue").grid(row=5, column=0, pady=5, padx=10, sticky="w")
        self.price_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.price_entry.grid(row=5, column=1, pady=5, padx=10, sticky="w")

        tk.Label(inventory_frame, text="Manufacturer Name:", font=("Arial", 14), bg="lightblue").grid(row=6, column=0, pady=5, padx=10, sticky="w")
        self.manufacturer_entry = tk.Entry(inventory_frame, font=("Arial", 14))
        self.manufacturer_entry.grid(row=6, column=1, pady=5, padx=10, sticky="w")

        # Buttons for Add Medicine and Remove Expired Stock
        add_button = tk.Button(inventory_frame, text="Add Medicine", command=self.add_medicine, font=("Arial", 14), bg="green", fg="white")
        add_button.grid(row=7, column=0, pady=20, padx=10, sticky="w")

        remove_button = tk.Button(inventory_frame, text="Remove Expired Stock", command=self.remove_expired_stock, font=("Arial", 14), bg="red", fg="white")
        remove_button.grid(row=7, column=1, pady=20, padx=10, sticky="e")

        # Back Button to UserOpenPage
        back_button = tk.Button(inventory_frame, text="Back", command=self.go_back, font=("Arial", 14), bg="blue", fg="white")
        back_button.grid(row=8, column=0, columnspan=2, pady=20)

        # Configure scrollbar
        scrollbar.config(command=inventory_frame.yview)
        inventory_frame.config(yscrollcommand=scrollbar.set)

    def add_medicine(self):
        # Functionality to add new medicine to the inventory
        med_name = self.med_name_entry.get()
        composition = self.composition_entry.get()
        batch_number = self.batch_entry.get()
        expire_date = self.expire_entry.get()
        stock_quantity = self.stock_entry.get()
        price = self.price_entry.get()
        manufacturer_name = self.manufacturer_entry.get()

        # Insert the new medicine into the inventory table
        try:
            self.cursor.execute("INSERT INTO medicines VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                                (med_name, composition, batch_number, expire_date, stock_quantity, price, manufacturer_name))
            self.conn.commit()
            messagebox.showinfo("Success", "Medicine added successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error adding medicine: {e}")

    def remove_expired_stock(self):
        # Functionality to remove expired stock from the inventory
        try:
            self.cursor.execute("DELETE FROM medicines WHERE expire_date <= DATE('now')")
            self.conn.commit()
            messagebox.showinfo("Success", "Expired stock removed successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error removing expired stock: {e}")

    def go_back(self):
        # Functionality to go back to the UserOpenPage
        self.destroy()  # Destroy the inventory management page window
        self.user_open_page.deiconify()  # Show the UserOpenPage window

if _name_ == "_main_":
    login_page = LoginPage()
    login_page.mainloop()
