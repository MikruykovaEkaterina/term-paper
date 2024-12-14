import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from functools import partial
class ReportGenerator(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn
        self.report_types = ['Dish Nutrition Report', 'Sales Report by Dish Type', 'Inventory Report']
        self.create_widgets()

    def create_widgets(self):
        # Frame for report selection
        self.style = ttk.Style()
        self.style.configure("FontButton.TButton", font=("Helvetica", 12))

        report_selection_frame = ttk.Frame(self)
        report_selection_frame.pack(pady=10, fill='x')

        ttk.Label(report_selection_frame, text="Select Report:", font=("Helvetica", 12)).pack(side='left', padx=5)
        self.report_var = tk.StringVar()
        combobox = ttk.Combobox(report_selection_frame, textvariable=self.report_var, values=self.report_types, state='readonly', font=("Helvetica", 12))
        combobox.pack(side='left', padx=5)
        button = ttk.Button(report_selection_frame, text="Generate Report", command=self.generate_report, style="FontButton.TButton")
        button.pack(side='left', padx=5)
    def generate_report(self):
        report_name = self.report_var.get()
        if report_name == 'Dish Nutrition Report':
            self.generate_dish_nutrition_report()
        elif report_name == 'Sales Report by Dish Type':
            self.generate_sales_report_by_dish_type()
        elif report_name == 'Inventory Report':
            self.generate_inventory_report()

    def generate_dish_nutrition_report(self):
        filter_dish_type = simpledialog.askstring("Filter", "Filter by Dish Type (leave blank for all):")
        sort_by = simpledialog.askstring("Sort By", "Sort by (calories or microelement):")

        query = "SELECT * FROM dish_nutrition_view"
        params = []

        if filter_dish_type:
            query += " WHERE dish_name LIKE ?"
            params.append(f'%{filter_dish_type}%')

        if sort_by:
            if sort_by.lower() == 'calories':
                query += " ORDER BY total_calories DESC"
            elif sort_by.lower() == 'microelement':
                query += " ORDER BY total_microelements DESC"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # Display the report
        report_window = tk.Toplevel(self)
        report_window.title("Dish Nutrition Report")

        report_title = ttk.Label(report_window, text="Dish Nutrition Report", font=("Helvetica", 16, "bold"))
        report_title.pack(pady=10)

        tree = ttk.Treeview(report_window, columns=('Dish', 'Total Calories', 'Total Microelements'), show='headings')
        tree.heading('Dish', text='Dish')
        tree.heading('Total Calories', text='Total Calories')
        tree.heading('Total Microelements', text='Total Microelements')
        tree.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)

        for index, row in enumerate(rows):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=row, tags=(tag,))

    def generate_sales_report_by_dish_type(self):
        filter_dish_type = simpledialog.askstring("Filter", "Filter by Dish Type (leave blank for all):")
        sort_order = simpledialog.askstring("Sort By", "Sort by (asc or desc):")

        query = "SELECT * FROM sales_by_dish_type_view"
        params = []

        if filter_dish_type:
            query += " WHERE dish_type LIKE ?"
            params.append(f'%{filter_dish_type}%')

        if sort_order:
            query += f" ORDER BY total_sales {sort_order.upper()}"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # Display the report
        report_window = tk.Toplevel(self)
        report_window.title("Sales Report by Dish Type")
        tree = ttk.Treeview(report_window, columns=('Dish Type', 'Total Sales'))
        tree.heading('Dish Type', text='Dish Type')
        tree.heading('Total Sales', text='Total Sales')
        tree.pack(fill='both', expand=True)
        for row in rows:
            tree.insert('', 'end', values=row)

    def generate_inventory_report(self):
        filter_component_name = simpledialog.askstring("Filter", "Filter by Component Name (leave blank for all):")
        sort_by = simpledialog.askstring("Sort By", "Sort by (weight or cost):")

        query = "SELECT * FROM inventory_report_view"
        params = []

        if filter_component_name:
            query += " WHERE component_name LIKE ?"
            params.append(f'%{filter_component_name}%')

        if sort_by:
            if sort_by.lower() == 'weight':
                query += " ORDER BY total_weight DESC"
            elif sort_by.lower() == 'cost':
                query += " ORDER BY total_cost DESC"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # Display the report
        report_window = tk.Toplevel(self)
        report_window.title("Inventory Report")
        tree = ttk.Treeview(report_window, columns=('Component', 'Total Weight', 'Total Cost'))
        tree.heading('Component', text='Component')
        tree.heading('Total Weight', text='Total Weight')
        tree.heading('Total Cost', text='Total Cost')
        tree.pack(fill='both', expand=True)
        for row in rows:
            tree.insert('', 'end', values=row)
class TableManager:
    def __init__(self, frame, table_name, cursor, conn, app):
        self.frame = frame
        self.table_name = table_name
        self.cursor = cursor
        self.conn = conn
        self.app = app

        self.column_types = {
            'dishes': {
                'dish_code': int,
                'denomination': str,
                'price': float,
                'dish_type_code': int
            },
            'components': {
                'component_code': int,
                'denomination': str,
                'caloric_content': int,
                'price': float,
                'weight': int
            },
            'types_of_dishes': {
                'dish_type_code': int,
                'name_of_the_type_of_dish': str
            },
            'composition_of_the_dish': {
                'dish_code': int,
                'component_code': int
            },
            'microelements': {
                'microelement_code': int,
                'denomination': str
            },
            'composition_of_components': {
                'component_code': int,
                'microelement_code': int,
                'quantity_per_100g': int
            },
            'daily_set_of_microelements': {
                'microelement_code': int,
                'quantity_in_mg': int
            }
        }
        # Initialize filter variables
        self.filter_column = None
        self.filter_operator = None
        self.filter_value = None
        # Initialize sort state
        self._sort_column = None
        self.sort_order = True  # True for ascending, False for descending

        # Search entry and button
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.tree = ttk.Treeview(frame)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        # Set columns and headings
        self.set_columns()

        # Set filter column dropdown values after columns are set
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='top', fill='x')
        self.search_button = ttk.Button(frame, text="Search", command=self.perform_search)
        self.search_button.pack(side='top')

        # Load data into the treeview
        self.load_data()

        # Filter UI elements
        self.filter_frame = ttk.Frame(frame)
        self.filter_frame.pack(side='top', fill='x')

        ttk.Label(self.filter_frame, text="Filter by:").pack(side='left')
        self.filter_column_var = tk.StringVar()
        self.filter_column_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.filter_column_var,
                                                   state='readonly')
        self.filter_column_dropdown.pack(side='left')
        self.filter_column_dropdown.bind('<<ComboboxSelected>>', self.on_column_select)

        self.filter_operator_var = tk.StringVar()
        self.filter_operator_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.filter_operator_var,
                                                     state='readonly')
        self.filter_operator_dropdown.pack(side='left')

        self.filter_value_entry = ttk.Entry(self.filter_frame)
        self.filter_value_entry.pack(side='left')

        self.apply_filter_button = ttk.Button(self.filter_frame, text="Apply Filter", command=self.apply_filter)
        self.apply_filter_button.pack(side='left')

        self.clear_filter_button = ttk.Button(self.filter_frame, text="Clear Filter", command=self.clear_filter)
        self.clear_filter_button.pack(side='left')

        # Populate column dropdown
        self.filter_column_dropdown['values'] = self.tree['columns']
        # Edit button
        self.edit_button = ttk.Button(self.frame, text="Edit", command=self.edit_item)
        self.edit_button.pack()

        self.add_button = ttk.Button(self.frame, text="Add", command=self.add_item)
        self.add_button.pack()

        self.delete_button = ttk.Button(self.frame, text="Delete", command=self.delete_item)
        self.delete_button.pack()

    def set_columns(self):
        self.cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns_info = self.cursor.fetchall()
        columns = [col[1] for col in columns_info]
        self.tree['columns'] = columns
        for col in columns:
            # Use lambda to pass the column name to sort_column
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100)

    def sort_by_column(self, col, event=None):
        # Determine the data type for the column
        data_type = self.column_types[self.table_name].get(col, str)
        # Fetch all items from the tree
        items = self.tree.get_children('')
        # Extract the sort column values
        if data_type == int:
            sort_values = [int(self.tree.set(item, col)) for item in items]
        elif data_type == float:
            sort_values = [float(self.tree.set(item, col)) for item in items]
        else:
            sort_values = [self.tree.set(item, col) for item in items]
        # Sort the items based on the sort column and current order
        sorted_items = sorted(items, key=lambda x: sort_values[items.index(x)], reverse=not self.sort_order)
        # Rearrange the items in the Treeview
        for index, item in enumerate(sorted_items):
            self.tree.move(item, '', index)
        # Toggle the sort order
        self.sort_order = not self.sort_order
        # Change the heading arrow to indicate sort order
        if self._sort_column == col:  # Use _sort_column
            self.sort_order = not self.sort_order
        else:
            self._sort_column = col  # Update _sort_column
        self.update_sort_arrow(col)

    def update_sort_arrow(self, col):
        # Optionally, add images for sort arrows
        # For simplicity, this method can be left empty or implement arrow display
        pass
    def on_column_select(self, event):
        selected_column = self.filter_column_var.get()
        column_type = self.column_types[self.table_name].get(selected_column, str)
        if column_type in (int, float):
            self.filter_operator_var.set('=')
            self.filter_operator_dropdown['values'] = ['=', '>', '<', '>=', '<=']
        elif column_type == str:
            self.filter_operator_var.set('contains')
            self.filter_operator_dropdown['values'] = ['contains', 'starts with', 'ends with', 'equals']

    def apply_filter(self):
        self.filter_column = self.filter_column_var.get()
        self.filter_operator = self.filter_operator_var.get()
        self.filter_value = self.filter_value_entry.get()
        self.refresh_treeview()

    def clear_filter(self):
        self.filter_column = None
        self.filter_operator = None
        self.filter_value = None
        self.filter_column_var.set('')
        self.filter_operator_var.set('')
        self.filter_value_entry.delete(0, 'end')
        self.refresh_treeview()

    def build_filter_clause(self):
        if self.filter_column and self.filter_operator and self.filter_value:
            if self.filter_column in self.column_types[self.table_name]:
                column_type = self.column_types[self.table_name][self.filter_column]
                if column_type in (int, float):
                    return f"{self.filter_column} {self.filter_operator} ?"
                elif column_type == str:
                    if self.filter_operator == 'contains':
                        return f"{self.filter_column} LIKE ?"
                    elif self.filter_operator == 'starts with':
                        return f"{self.filter_column} LIKE ?"
                    elif self.filter_operator == 'ends with':
                        return f"{self.filter_column} LIKE ?"
                    elif self.filter_operator == 'equals':
                        return f"{self.filter_column} = ?"
            else:
                return None
        return None

    def perform_search(self):
        search_term = self.search_var.get().strip()
        filter_clause = self.build_filter_clause()
        params = []

        query = f"SELECT * FROM {self.table_name}"
        where_clauses = []
        if search_term:
            search_conditions = []
            for col in self.tree['columns']:
                data_type = self.column_types[self.table_name].get(col, str)
                if data_type == str:
                    search_conditions.append(f"{col} LIKE ?")
                    params.append(f'%{search_term}%')
            if search_conditions:
                where_clauses.append(f"{' OR '.join(search_conditions)}")
        if filter_clause:
            where_clauses.append(filter_clause)
            column_type = self.column_types[self.table_name].get(self.filter_column, str)
            if column_type in (int, float):
                params.append(float(self.filter_value))
            else:
                if self.filter_operator in ('contains', 'starts with', 'ends with'):
                    params.append(f'%{self.filter_value}%')
                else:
                    params.append(self.filter_value)
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def refresh_treeview(self):
        self.search_var.set('')
        self.filter_value_entry.delete(0, 'end')
        self.load_data()
    def load_data(self):
        filter_clause = self.build_filter_clause()
        search_term = self.search_var.get().strip()
        params = []

        query = f"SELECT * FROM {self.table_name}"
        where_clauses = []
        if search_term:
            search_conditions = []
            for col in self.tree['columns']:
                data_type = self.column_types[self.table_name].get(col, str)
                if data_type == str:
                    search_conditions.append(f"{col} LIKE ?")
                    params.append(f'%{search_term}%')
            if search_conditions:
                where_clauses.append(f"{' OR '.join(search_conditions)}")
        if filter_clause:
            where_clauses.append(filter_clause)
            column_type = self.column_types[self.table_name].get(self.filter_column, str)
            if column_type in (int, float):
                params.append(float(self.filter_value))
            else:
                if self.filter_operator in ('contains', 'starts with', 'ends with'):
                    params.append(f'%{self.filter_value}%')
                else:
                    params.append(self.filter_value)
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert('', 'end', values=row)
        if self._sort_column:
            self.sort_by_column(self._sort_column)
    def delete_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        # Retrieve all primary key column names
        self.cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns_info = self.cursor.fetchall()
        pk_columns = [col[1] for col in columns_info if col[5]]  # Column names where pk != 0
        if not pk_columns:
            messagebox.showerror("Error", "No primary key found.")
            return
        # Get the values of the primary key columns for the selected item
        item_values = self.tree.item(selected_item, 'values')
        pk_values = [item_values[self.tree['columns'].index(col)] for col in pk_columns]
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the record?")
        if not confirm:
            return
        # Construct WHERE clause
        where_clause = " AND ".join([f"{col} = ?" for col in pk_columns])
        query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
        # Execute DELETE query
        try:
            self.cursor.execute(query, pk_values)
            self.conn.commit()
            self.refresh_treeview()
            # Refresh dependent tables
            for dep_table in self.app.dependent_tables.get(self.table_name, []):
                self.app.refresh_table(dep_table)
            messagebox.showinfo("Success", "Record deleted successfully.")
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Constraint Violation", f"Cannot delete record due to constraint violation: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def add_item(self):
        if self.table_name == 'dishes':
            self.add_dish_with_components()
        else:
            self.add_item_simple()

    def add_item_simple(self):
        # Create a new window for adding a new item
        add_window = tk.Toplevel(self.frame)
        add_window.title(f"Add New {self.table_name.capitalize()}")

        # Get column names and data types
        columns = self.tree['columns']
        types = [self.column_types[self.table_name][col] for col in columns]

        # Determine primary key columns
        self.cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns_info = self.cursor.fetchall()
        pk_columns = [col for col in columns_info if col[5] > 0]  # col[5] is pk

        # Get foreign key information
        self.cursor.execute(f"PRAGMA foreign_key_list({self.table_name})")
        fk_info = self.cursor.fetchall()

        # Create a mapping from foreign key column to referenced table and column
        fk_mapping = {}
        for fk in fk_info:
            fk_column = fk[3]  # 'from' column
            ref_table = fk[2]  # referenced table
            ref_column = fk[4]  # referenced column
            fk_mapping[fk_column] = (ref_table, ref_column)

        # Check if the primary key is also a foreign key
        pk_column_names = set(col[1] for col in pk_columns)
        fk_from_columns = set(fk_mapping.keys())
        pk_is_fk = not pk_column_names.isdisjoint(fk_from_columns)

        # Determine if the first column is an INTEGER PRIMARY KEY and not a foreign key
        if len(pk_columns) == 1 and pk_columns[0][2].upper() == 'INTEGER' and not pk_is_fk:
            is_autoincrement = True
        else:
            is_autoincrement = False

        entries = []
        row_idx = 0
        for idx, col_name in enumerate(columns):
            if is_autoincrement and idx == 0:
                continue  # Skip the single INTEGER PRIMARY KEY not being a foreign key
            label = ttk.Label(add_window, text=col_name)
            label.grid(row=row_idx, column=0)
            if col_name in fk_mapping:
                # It's a foreign key, create a combobox
                ref_table, ref_column = fk_mapping[col_name]
                # Fetch possible values from the referenced table
                self.cursor.execute(f"SELECT {ref_column} FROM {ref_table}")
                ref_values = [row[0] for row in self.cursor.fetchall()]
                entry = ttk.Combobox(add_window, values=ref_values)
                entry.grid(row=row_idx, column=1)
                widget_type = 'combobox'
            else:
                # It's a regular column, create an entry widget
                entry = ttk.Entry(add_window)
                entry.grid(row=row_idx, column=1)
                widget_type = 'entry'
            entries.append((col_name, entry, widget_type, types[idx]))
            row_idx += 1

        # Save button
        save_button = ttk.Button(add_window, text="Save",
                                 command=lambda: self.save_add(add_window, entries, is_autoincrement))
        save_button.grid(row=row_idx, columnspan=2)

    def save_add(self, window, entries, is_autoincrement):
        # Collect new values
        new_values = {}
        for col_name, widget, widget_type, data_type in entries:
            if widget_type == 'entry':
                value = widget.get()
            elif widget_type == 'combobox':
                value = widget.get()
            else:
                continue  # Unknown widget type
            try:
                converted_value = data_type(value)
            except ValueError:
                messagebox.showerror("Invalid Input",
                                     f"Invalid data for column '{col_name}'. Expected {data_type.__name__}.")
                return
            new_values[col_name] = converted_value

        # Determine columns and values for INSERT
        if is_autoincrement:
            # Exclude the first column (single INTEGER PRIMARY KEY not being a foreign key)
            columns = [col for col in self.tree['columns'] if col != self.tree['columns'][0]]
            values = [new_values[col] for col in columns]
        else:
            # Include all columns
            columns = self.tree['columns']
            values = [new_values[col] for col in columns]

        # Construct INSERT query
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.refresh_treeview()
            messagebox.showinfo("Success", "Record added successfully.")
            window.destroy()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Constraint Violation", f"Cannot add record due to constraint violation: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def add_dish_with_components(self):
        add_window = tk.Toplevel(self.frame)
        add_window.title("Add New Dish with Components")

        # Dish details

        denomination_label = ttk.Label(add_window, text="Denomination:")
        denomination_label.grid(row=0, column=0)
        denomination_entry = ttk.Entry(add_window)
        denomination_entry.grid(row=0, column=1)

        price_label = ttk.Label(add_window, text="Price:")
        price_label.grid(row=1, column=0)
        price_entry = ttk.Entry(add_window)
        price_entry.grid(row=1, column=1)

        dish_type_code_label = ttk.Label(add_window, text="Dish Type Code:")
        dish_type_code_label.grid(row=2, column=0)
        dish_type_code_entry = ttk.Entry(add_window)
        dish_type_code_entry.grid(row=2, column=1)

        # Components section
        ttk.Label(add_window, text="Components:").grid(row=3, column=0, columnspan=2)
        components_tree = ttk.Treeview(add_window, columns=('component_code', 'component_name'))
        components_tree.heading('component_code', text='Component Code')
        components_tree.heading('component_name', text='Component Name')
        components_tree.grid(row=4, column=0, columnspan=2)

        add_component_button = ttk.Button(add_window, text="Add Component",
                                          command=lambda: self.add_component(components_tree))
        add_component_button.grid(row=5, column=0)
        # Save button
        save_button = ttk.Button(add_window, text="Save", command=lambda: self.save_dish_with_components(
            add_window,
            denomination_entry,
            price_entry,
            dish_type_code_entry,
            components_tree
        ))
        save_button.grid(row=5, column=1)

    def add_component(self, components_tree):
        select_window = tk.Toplevel()
        select_window.title("Select Component")

        # Create Treeview to display components
        component_tree = ttk.Treeview(select_window, columns=('component_code', 'denomination'))
        component_tree.heading('component_code', text='Component Code')
        component_tree.heading('denomination', text='Denomination')
        component_tree.pack(fill='both', expand=True)

        # Fetch components from database
        self.cursor.execute("SELECT component_code, denomination FROM components")
        components = self.cursor.fetchall()
        for comp in components:
            component_tree.insert('', 'end', values=comp)

        # Select button
        select_button = ttk.Button(select_window, text="Select", command=lambda: self.select_component(component_tree, components_tree, select_window))
        select_button.pack()

        # Close button
        close_button = ttk.Button(select_window, text="Close", command=select_window.destroy)
        close_button.pack()

    def select_component(self, component_tree, components_tree, select_window):
        selected_item = component_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a component.")
            return
        component_values = component_tree.item(selected_item, 'values')
        component_code = component_values[0]
        component_name = component_values[1]

        # Check if component is already added
        for child in components_tree.get_children():
            if components_tree.set(child, 'component_code') == component_code:
                messagebox.showwarning("Duplicate Component", "This component is already added.")
                return

        # Add to dish's components_tree
        components_tree.insert('', 'end', values=(component_code, component_name))

        # Close the selection window
        select_window.destroy()
    def save_dish_with_components(self, window, denomination_entry, price_entry, dish_type_code_entry, components_tree):
        # Collect dish data
        denomination = denomination_entry.get()
        price = price_entry.get()
        dish_type_code = dish_type_code_entry.get()

        # Validate and convert data types
        try:
            price = float(price)
            dish_type_code = int(dish_type_code)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid data types.")
            return

        # Insert into dishes table
        query_dish = "INSERT INTO dishes (denomination, price, dish_type_code) VALUES (?, ?, ?)"
        try:
            self.cursor.execute(query_dish, (denomination, price, dish_type_code))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Constraint Violation", f"Cannot add dish: {e}")
            return
        # Get the generated dish_code
        dish_code = self.cursor.lastrowid
        # Collect components data
        components = []
        for child in components_tree.get_children():
            component_code = components_tree.item(child, 'values')[0]
            components.append(component_code)

        # Insert into composition_of_the_dish table
        for component_code in components:
            query_component = "INSERT INTO composition_of_the_dish (dish_code, component_code) VALUES (?, ?)"
            try:
                self.cursor.execute(query_component, (dish_code, component_code))
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Constraint Violation", f"Cannot add component: {e}")
                continue  # Continue adding other components

        messagebox.showinfo("Success", "Dish and components added successfully.")
        window.destroy()
        self.refresh_treeview()
        if 'composition_of_the_dish' in self.app.table_managers:
            self.app.table_managers['composition_of_the_dish'].refresh_treeview()

    def edit_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return
        item_values = self.tree.item(selected_item, 'values')
        # Create a new window for editing
        edit_window = tk.Toplevel(self.frame)
        edit_window.title(f"Edit {self.table_name}")

        # Create entry widgets for each column
        entries = []
        for idx, col in enumerate(self.tree['columns']):
            label = ttk.Label(edit_window, text=col)
            label.grid(row=idx, column=0)
            entry = ttk.Entry(edit_window)
            entry.insert(0, item_values[idx])
            entry.grid(row=idx, column=1)
            # Disable primary key field
            if col == self.tree['columns'][0]:
                entry.config(state='disabled')
            entries.append(entry)

        # Save button
        save_button = ttk.Button(edit_window, text="Save", command=lambda: self.save_edit(edit_window, entries, item_values))
        save_button.grid(row=len(self.tree['columns']), columnspan=2)

    def save_edit(self, window, entries, original_values):
        new_values = [entry.get() for entry in entries]
        # Get the column names excluding the primary key
        columns = self.tree['columns'][1:]
        # Get the data types for these columns
        types = [self.column_types[self.table_name][col] for col in columns]
        try:
            # Convert the new_values accordingly, skipping the primary key
            converted_values = [types[i](new_values[i+1]) for i in range(len(types))]
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid data for all fields.")
            return

        # Construct UPDATE query
        set_clause = ', '.join([f"{col} = ?" for col in columns])
        where_clause = f"{self.tree['columns'][0]} = ?"
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"
        try:
            self.cursor.execute(query, (*converted_values, original_values[0]))
            self.conn.commit()
            # Refresh the Treeview
            self.refresh_treeview()
            messagebox.showinfo("Success", "Data updated successfully.")
            window.destroy()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Constraint Violation", f"Cannot update due to constraint violation: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Application")

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set window geometry to screen dimensions
        root.geometry(f"{screen_width}x{screen_height}")

        self.conn = sqlite3.connect('restaurant.db')
        self.cursor = self.conn.cursor()
        # Enable foreign key constraints
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=("Helvetica", 12))
        style.configure('TEntry', font=("Helvetica", 12))
        style.configure('TButton', font=("Helvetica", 12))
        style.configure("Treeview", rowheight=25, font=("Helvetica", 12))
        style.map("Treeview", background=[('selected', 'blue')])
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        self.table_managers = {}
        self.dependent_tables = {
            'types_of_dishes': ['dishes'],
            'dishes': ['composition_of_the_dish'],
            'components': ['composition_of_the_dish', 'composition_of_components'],
            'microelements': ['composition_of_components', 'daily_set_of_microelements']
        }
        self.create_tables_section()
        self.create_reports_section()

    def create_tables_section(self):
        table_names = ['types_of_dishes', 'dishes', 'components', 'composition_of_the_dish', 'microelements', 'composition_of_components', 'daily_set_of_microelements']
        for table in table_names:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=table.capitalize())
            tm = TableManager(tab, table, self.cursor, self.conn, self)
            self.table_managers[table] = tm

    def refresh_table(self, table_name):
        if table_name in self.table_managers:
            self.table_managers[table_name].refresh_treeview()
    def create_reports_section(self):
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text='Reports')
        report_generator = ReportGenerator(reports_frame, self.cursor, self.conn)
        report_generator.pack(fill='both', expand=True)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = RestaurantApp(root)
    app.run()