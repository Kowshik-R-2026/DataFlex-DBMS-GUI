# MySQL Table Management with Tkinter

This project is a **Python** application using **Tkinter** to provide a graphical interface for managing MySQL databases and tables. The app allows users to select databases and tables, perform CRUD operations (Create, Read, Update, Delete), and search for specific records.

## Features

- **Connect to MySQL** and retrieve databases and tables.
- **Insert, Update, Delete** records from selected tables.
- **Search** functionality using specified attributes and values.
- Display table contents in a **TreeView** widget.
- Responsive and dynamic UI using **Tkinter**.
- Supports **image integration** in the GUI using **Pillow**.

## Tech Stack

- **Python 3.x**
- **Tkinter** for the GUI.
- **Pillow** for image handling.
- **MySQL Connector** to interact with MySQL databases.

## Setup Instructions

### Prerequisites

1. Ensure you have **Python** installed.
2. Install required Python packages:
   ```bash
   pip install mysql-connector-python Pillow
   ```

3. Make sure you have a **MySQL server** running and accessible.

### Configuration

Before running the application, update the **MySQL credentials** in the code (`connect_to_mysql()` function):
```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="your_database"
)
```

### Run the Application

1. Clone or download the repository.
2. Run the Python script:
   ```bash
   python app.py
   ```

### User Interface

- **Select Database**: Dropdown menu to select the active database.
- **Select Table**: Dropdown menu to choose a table within the selected database.
- **Insert Data**: Add new records directly into the table.
- **Update Records**: Modify existing records by selecting a row and updating values.
- **Delete Records**: Search and delete records using the **Search Attribute** and **Search Value** fields.

## File Structure

```plaintext
.
├── app.py                # Main Python Tkinter Application
├── README.md             # This file
├── images                # Folder to store images used in the GUI
    └── test.png          # Example image used in the interface
```

## Usage

1. **Select Database**: Choose the database from the dropdown list.
2. **Select Table**: Select the table for the operation.
3. **Insert Data**: Fill out the input fields and press "Insert".
4. **Update Data**: Select a row from the table, modify the values in the input fields, and press "Update".
5. **Delete Data**: Use the search bar to find specific records and press "Delete" to remove them.

## License

This project is licensed under the MIT License.
