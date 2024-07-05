import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from PIL import ImageTk, Image

# Define conn and cursor after imports
conn = None
cursor = None

# Global variables to store the selected database and table
selected_database = None
selected_table = None
insert_frame = None

def on_row_select(event):
    global selected_table
    # Get the selected item
    item = event.widget.focus()
    # Get the values of the selected row
    values = event.widget.item(item, 'values')
    # Populate insert fields with the selected row values
    for i in range(len(values)):
        insert_entries[i].delete(0, tk.END)  # Clear existing value
        insert_entries[i].insert(0, values[i])

def create_insert_widgets(columns):
    global insert_frame, insert_entries
    insert_frame = tk.Frame(window, bg="white")
    insert_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Adjust the number of columns based on the number of attributes
    num_columns = 2 if len(columns) > 3 else 1
    num_rows = (len(columns) + 1) // num_columns

    insert_labels = []
    insert_entries = []

    for i in range(len(columns)):
        row = i // num_columns
        col = i % num_columns

        # Create label
        insert_label = tk.Label(insert_frame, text=columns[i] + ":", bg="white", font=("Calibri", 12))
        insert_label.grid(row=row, column=col*2, sticky="w", padx=(5, 0), pady=(5, 2))
        insert_labels.append(insert_label)

        # Create entry
        insert_entry = tk.Entry(insert_frame, font=("Calibri", 12))
        insert_entry.grid(row=row, column=col*2+1, sticky="ew", padx=(0, 5), pady=(5, 2))
        insert_entries.append(insert_entry)

    insert_button = tk.Button(insert_frame, text="Insert", command=lambda: insert_data(insert_labels, insert_entries), font=("Calibri", 14))
    insert_button.grid(row=num_rows, column=0, columnspan=num_columns*2, pady=(10, 0), padx=5)

def insert_data(insert_labels, insert_entries):
    global conn, cursor, selected_table
    if selected_table:
        # Get values from insert entries
        values = [entry.get() for entry in insert_entries]
        primary_key_value = values[0]
        
        # Check if the primary key value already exists in the table
        cursor.execute(f"SELECT * FROM {selected_table} WHERE {insert_labels[0]['text'][: -1]} = %s", (primary_key_value,))
        existing_row = cursor.fetchone()
        if existing_row:
            # Prompt the user to update the existing row
            confirm_update = messagebox.askyesno("Duplicate Primary Key",
                                                  "Data with same primary key found in the table.\nUpdate the values in the table with the new values?")
            if confirm_update:
                # Construct UPDATE query
                set_clause = ", ".join([f"{insert_labels[i]['text'][: -1]} = %s" for i in range(1, len(values))])  # Skip the primary key field
                sql = f"UPDATE {selected_table} SET {set_clause} WHERE {insert_labels[0]['text'][: -1]} = %s"
                cursor.execute(sql, values[1:] + [primary_key_value])
                conn.commit()
                messagebox.showinfo("Success", "Data updated successfully!")
                update_table_content()
            return  # Stop execution if the row is updated
        
        # If primary key value doesn't exist, proceed with insertion
        # Create placeholder string for values
        placeholder = ','.join(['%s'] * len(values))
        # Execute separate INSERT statement for each row
        sql = f"INSERT INTO {selected_table} VALUES ({placeholder})"
        cursor.execute(sql, values)
        conn.commit()
        messagebox.showinfo("Success", "Data inserted successfully!")
        update_table_content()

# Function to update the database dropdown menu
def update_database_dropdown():
    global conn, cursor, selected_database
    if conn is None:
        messagebox.showinfo("Information", "Please connect to MySQL first.")
        return
    cursor = conn.cursor()
    # Execute query to fetch database names
    cursor.execute("SHOW DATABASES")
    # Fetch all rows
    databases = [db[0] for db in cursor.fetchall()]
    cursor.close()
    # Clear existing options
    database_dropdown["menu"].delete(0, "end")
    # Add new options
    for db in databases:
        database_dropdown["menu"].add_command(label=db, command=lambda db=db: select_database(db))
    if selected_database in databases:
        database_var.set(selected_database)

# Function to update the table dropdown menu
def update_table_dropdown():
    global conn, cursor, selected_database
    if selected_database:
        cursor = conn.cursor()
        # Execute query to fetch table names for the selected database
        cursor.execute(f"USE {selected_database}")
        cursor.execute("SHOW TABLES")
        # Fetch all rows
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        # Clear existing options
        table_dropdown["menu"].delete(0, "end")
        # Add new options
        for table in tables:
            table_dropdown["menu"].add_command(label=table, command=lambda t=table: select_table(t))

def clear_insert_widgets():
    global insert_frame
    if insert_frame:
        insert_frame.destroy()

# Function to select a database
def select_database(database):
    global selected_database, selected_table
    selected_database = database
    clear_insert_widgets()
    selected_table = None  # Clear selected table when database is changed
    update_table_dropdown()
    # Update the dropdown menu with the selected database
    database_var.set(database)
    

def select_table(table):
    global conn, cursor, selected_table
    selected_table = table
    clear_insert_widgets()
    # Update the dropdown menu with the selected table
    table_var.set(table)
    # Update the text of the table dropdown button
    table_dropdown.config(text=f"Table: {table}")
    if selected_table:
        cursor = conn.cursor()
        # Get table columns
        cursor.execute(f"DESCRIBE {selected_table}")
        columns = [col[0] for col in cursor.fetchall()]
        create_insert_widgets(columns)
        update_table_content()
        # Populate the search attribute dropdown
        populate_search_attribute_dropdown()
    

def update_table_content():
    global selected_table, cursor
    if selected_table:
        # Clear existing widgets in the display frame
        for widget in display_frame.winfo_children():
            widget.destroy()
        cursor = conn.cursor()
        # Fetch data from selected table
        query = f"SELECT * FROM {selected_table}"
        cursor.execute(query)
        data = cursor.fetchall()
        # Create a label to display the table name
        label = ttk.Label(display_frame, text=f"Data from Table: {selected_table}", font=("Calibri", 12))
        label.grid(row=0, column=0, columnspan=2)
        # Create a treeview to display the data
        tree = ttk.Treeview(display_frame, columns=[i[0] for i in cursor.description], show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        for row in data:
            tree.insert("", tk.END, values=row)
        tree.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # Set font for the values inside the table
        style = ttk.Style()
        style.configure("Treeview", font=("Calibri", 12))
        tree.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # Add horizontal scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        # Bind row selection event to on_row_select function
        tree.bind('<<TreeviewSelect>>', on_row_select)

# Function to connect to MySQL
def connect_to_mysql():
    global conn
    # Connect to MySQL with default username and password
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="zxcvbnm,./",
        database="mysql"
    )
    update_database_dropdown()

# Function to populate the search attribute dropdown
def populate_search_attribute_dropdown():
    global conn, cursor, selected_table
    if selected_table:
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {selected_table}")
        columns = [col[0] for col in cursor.fetchall()]
        # Clear existing options
        search_attr_dropdown["menu"].delete(0, "end")
        # Add new options
        for column in columns:
            search_attr_dropdown["menu"].add_command(label=column, command=lambda col=column: search_attr_var.set(col))

# Function to perform search
def perform_search(event=None):
    global conn, cursor, selected_table
    if selected_table:
        search_attribute = search_attr_var.get()
        search_value = search_value_entry.get()
        if search_attribute and search_value:
            query = f"SELECT * FROM {selected_table} WHERE {search_attribute} LIKE '%{search_value}%'"
            cursor.execute(query)
            data = cursor.fetchall()
            update_table_content_with_search(data)

# Function to update table content after search
def update_table_content_with_search(data):
    global selected_table, cursor
    if selected_table:
        # Clear existing widgets in the display frame
        for widget in display_frame.winfo_children():
            widget.destroy()
        # Create a label to display the table name
        label = ttk.Label(display_frame, text=f"Search Results from Table: {selected_table}", font=("Calibri", 12))
        label.grid(row=0, column=0, columnspan=2)
        # Create a treeview to display the search results
        tree = ttk.Treeview(display_frame, columns=[i[0] for i in cursor.description], show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        for row in data:
            tree.insert("", tk.END, values=row)
        tree.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # Set font for the values inside the table
        style = ttk.Style()
        style.configure("Treeview", font=("Calibri", 14))
        tree.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # Add horizontal scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=0, columnspan=2, sticky="ew")

# Function to delete data based on search criteria
def delete_data():
    global conn, cursor, selected_table
    if selected_table:
        search_attribute = search_attr_var.get()
        search_value = search_value_entry.get()
        if search_attribute and search_value:
            query = f"DELETE FROM {selected_table} WHERE {search_attribute} LIKE '%{search_value}%'"
            cursor.execute(query)
            conn.commit()
            messagebox.showinfo("Success", "Data deleted successfully!")
            perform_search()

# Create Tkinter window
window = tk.Tk()
window.title("MySQL Table Display")
window.geometry("1080x720")
window.configure(bg="white")

# Create a frame to hold the database and table dropdown menus
dropdown_frame = tk.Frame(window, bg="white")
dropdown_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# Create a frame for the image label
image_frame = tk.Frame(window, bg="white")
image_frame.grid(row=0, column=0, sticky="e", padx=10, pady=10)

# Load the image
image_path = '/images/test.png '
image = Image.open(image_path)
image = image.resize((167, 52))
tk_image = ImageTk.PhotoImage(image)

# Create a label to display the image
image_label = tk.Label(image_frame, image=tk_image, bg="white")
image_label.pack(side="left")

# Label for database dropdown menu
database_label = tk.Label(dropdown_frame, text="Select Database:", bg="white", font=("Calibri", 12))
database_label.grid(row=0, column=0, padx=(0, 5))

# Variable to store selected database
database_var = tk.StringVar(window)

# Dropdown menu for databases
database_dropdown = tk.OptionMenu(dropdown_frame, database_var, "")
database_dropdown.config(bg="white", font=("Calibri", 12))
database_dropdown.grid(row=0, column=1, padx=(0, 10))

# Label for table dropdown menu
table_label = tk.Label(dropdown_frame, text="Select Table:", bg="white", font=("Calibri", 12))
table_label.grid(row=0, column=2, padx=(0, 5))

# Variable to store selected table
table_var = tk.StringVar(window)

# Dropdown menu for tables
table_dropdown = tk.OptionMenu(dropdown_frame, table_var, "")
table_dropdown.config(bg="white", font=("Calibri", 12))
table_dropdown.grid(row=0, column=3, padx=(0, 10))

# Search attribute dropdown
search_attr_label = tk.Label(dropdown_frame, text="Search Attribute:", bg="white",fg='White', font=("Calibri", 12),)
search_attr_label.grid(row=1, column=0, padx=(10, 5))

# Search attribute dropdown
search_attr_label = tk.Label(dropdown_frame, text="Search Attribute:", bg="white", font=("Calibri", 12))
search_attr_label.grid(row=2, column=0, padx=(10, 5))

search_attr_var = tk.StringVar(window)
search_attr_dropdown = tk.OptionMenu(dropdown_frame, search_attr_var, "")
search_attr_dropdown.config(bg="white", font=("Calibri", 14))
search_attr_dropdown.grid(row=2, column=1)

# Search value entry
search_value_label = tk.Label(dropdown_frame, text="Search Value:", bg="white", font=("Calibri", 12))
search_value_label.grid(row=2, column=2, padx=(10, 5))

search_value_entry = tk.Entry(dropdown_frame, font=("Calibri", 12))
search_value_entry.grid(row=2, column=3, padx=(10, 5))
search_value_entry.bind("<KeyRelease>", perform_search)

# Delete button
delete_button = tk.Button(dropdown_frame, text="Delete", command=delete_data, font=("Calibri", 12))
delete_button.grid(row=2, column=4, padx=(10, 0))

# Create a frame to hold the display of table data
display_frame = tk.Frame(window, bg="white")
display_frame.grid(row=5, column=0, sticky="nsew", padx=25, pady=25)

# Configure grid weights for resizing
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
display_frame.columnconfigure(0, weight=1)

# Connect to MySQL by default
connect_to_mysql()

# Run Tkinter main loop
window.mainloop()
