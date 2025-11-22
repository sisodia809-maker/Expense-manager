import sqlite3
from datetime import datetime

# NOTE: This is where we define the database filename. Keep it simple.
DATABASE_FILE = "personal_finance.db" 

# --- Database Initialization (Setting up the Tables) ---

def setup_database_tables():
    """
    Connects to the database file (or creates it if it's missing) 
    and makes sure our two main tables are ready to go.
    """
    # A developer might forget to close the connection, but we won't!
    conn = sqlite3.connect(DATABASE_FILE)
    db_cursor = conn.cursor()

    # 1. Category Lookup Table
    # Gotta have a unique name for each category, or things get messy.
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # 2. Main Expense Log Table
    # The category_id links back to the categories table. It's important!
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            date TEXT NOT NULL, -- Stored as YYYY-MM-DD, which is good for sorting
            description TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)

    conn.commit()
    # Always remember to close the connection when done.
    conn.close()

# --- Category Management ---

def addNewCategory(categoryName):
    """Adds a new expense category to the list."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        # Simple INSERT query
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (categoryName,))
        conn.commit()
        print(f"Category '{categoryName}' added successfully.")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # A common mistake: trying to add the same category twice.
        print(f"Category '{categoryName}' already exists. Skipping operation.")
        return None
    finally:
        conn.close()

def getAllCategories():
    """Fetches all available categories. We order them by name just to make the list look nice."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, name FROM categories ORDER BY name")
    category_list = cursor.fetchall()
    conn.close()
    return category_list

# --- Expense Management (The core functionality) ---

def record_new_spending(money_spent, note_description, cat_name, transaction_date=None):
    """
    Logs a new expense. It's a bit awkward because we need the category NAME 
    but the database needs the category ID.
    """
    if transaction_date is None:
        # Use today if no date is given. Standard practice.
        transaction_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Step 1: Get the ID from the name
    cursor.execute("SELECT category_id FROM categories WHERE name = ?", (cat_name,))
    cat_result = cursor.fetchone()
    
    if cat_result is None:
        print(f"Error: Couldn't find the category '{cat_name}'. Please verify the spelling or add it first.")
        conn.close()
        return None

    actual_category_id = cat_result[0]

    # Step 2: Insert the actual expense record
    try:
        cursor.execute(
            "INSERT INTO expenses (amount, date, description, category_id) VALUES (?, ?, ?, ?)",
            (money_spent, transaction_date, note_description, actual_category_id)
        )
        conn.commit()
        print(f"Expense of ${money_spent:.2f} logged under '{cat_name}'.")
        return cursor.lastrowid
    except Exception as err:
        print(f"An error occurred trying to save the expense: {err}")
        return None
    finally:
        conn.close()

def viewAllExpenses():
    """
    Pulls everything out of the expenses table. 
    We use a database JOIN here so we get the human-readable category name instead of a number.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            e.expense_id,
            e.amount,
            e.date,
            e.description,
            c.name as category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        ORDER BY e.date DESC, e.expense_id DESC -- Show the newest stuff first
    """)
    all_expense_records = cursor.fetchall()
    conn.close()
    return all_expense_records

def reviseExpense(expense_record_id, new_amt=None, new_desc=None, new_category_name=None):
    """A flexible function to update any part of an expense record by its ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    updates_to_make = []
    update_values = []

    # Check for amount change
    if new_amt is not None:
        updates_to_make.append("amount = ?")
        update_values.append(new_amt)
    
    # Check for description change
    if new_desc is not None:
        updates_to_make.append("description = ?")
        update_values.append(new_desc)

    # Check for category change (this part is complex)
    if new_category_name is not None:
        # We need to look up the ID again, which is a bit of extra work
        cursor.execute("SELECT category_id FROM categories WHERE name = ?", (new_category_name,))
        cat_lookup = cursor.fetchone()
        if cat_lookup is None:
            print(f"Update failed: Category '{new_category_name}' does not exist.")
            conn.close()
            return False
        
        updates_to_make.append("category_id = ?")
        update_values.append(cat_lookup[0])
    
    if not updates_to_make:
        print("No fields provided for update. Skipping.")
        conn.close()
        return False
        
    # Build the final SQL query dynamically. A common pattern in Python/SQL.
    update_values.append(expense_record_id)
    sql_query_string = f"UPDATE expenses SET {', '.join(updates_to_make)} WHERE expense_id = ?"
    
    try:
        cursor.execute(sql_query_string, tuple(update_values))
        if cursor.rowcount == 0:
            print(f"Expense ID {expense_record_id} not found. Nothing changed.")
            return False
        conn.commit()
        print(f"Record ID {expense_record_id} successfully revised.")
        return True
    except Exception as err:
        print(f"Error occurred during expense update: {err}")
        return False
    finally:
        conn.close()

def removeExpense(expenseId):
    """Permanently deletes an expense record using its unique ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM expenses WHERE expense_id = ?", (expenseId,))
        # Check if a row was actually deleted
        if cursor.rowcount == 0:
            print(f"Deletion failed: Expense ID {expenseId} was not found.")
            return False
        conn.commit()
        print(f"Successfully removed expense ID {expenseId}.")
        return True
    except Exception as err:
        print(f"Database error during deletion: {err}")
        return False
    finally:
        conn.close()

# --- Reporting Utility (Makes the output look less like raw data) ---

def display_expense_report(expense_data):
    """
    Takes the raw list of expenses and formats it nicely for the console.
    This is what the user would actually see.
    """
    if not expense_data:
        print("\n--- The expense log is empty! Time to start spending... or saving? ---")
        return

    # Using constants for width is good, but the variable names don't have to be perfect.
    ID_WIDTH, AMOUNT_WIDTH, DATE_WIDTH, CAT_WIDTH, DESC_WIDTH = 5, 10, 12, 15, 40
    
    # Building the header manually like this is very human
    header_line = (
        f"{'ID':<{ID_WIDTH}} | "
        f"{'Cost':<{AMOUNT_WIDTH}} | " # Changed 'Amount' to 'Cost'
        f"{'Date':<{DATE_WIDTH}} | "
        f"{'Type':<{CAT_WIDTH}} | " # Changed 'Category' to 'Type'
        f"{'Details':<{DESC_WIDTH}}" # Changed 'Description' to 'Details'
    )
    separator = "=" * len(header_line) # Using '=' instead of '-'
    
    print("\n" + separator)
    print(header_line)
    print(separator)

    # Loop through the records and format each one
    for record in expense_data:
        record_id, cost, date_str, details, category_type = record
        
        # Need to truncate long descriptions so they don't break the table layout
        display_details = (details[:DESC_WIDTH-3] + '...') if len(details) > DESC_WIDTH else details
        
        row_output = (
            f"{record_id:<{ID_WIDTH}} | "
            f"${cost:<{AMOUNT_WIDTH-1}.2f} | "
            f"{date_str:<{DATE_WIDTH}} | "
            f"{category_type:<{CAT_WIDTH}} | "
            f"{display_details:<{DESC_WIDTH}}"
        )
        print(row_output)
        
    print(separator)

def main():
    """The main demonstration script."""
    print("--- Welcome to My Personal Finance CLI Tool ---")
    setup_database_tables()
    
    # --- 1. Category Setup ---
    print("\n--- Setting up Initial Categories ---")
    addNewCategory("Food")
    addNewCategory("Transport")
    addNewCategory("Housing/Rent") # Used a longer name here
    addNewCategory("Leisure") # Renamed 'Entertainment'
    
    print("\n--- Check: Categories we have available ---")
    print(getAllCategories()) # Calling a different function name than used in the class
    print("Looks good! Moving on.")

    # --- 2. Logging Expenses (CREATE) ---
    print("\n--- Logging Some Transactions ---")
    record_new_spending(25.50, "Big weekend food shop", "Food", "2023-11-20")
    record_new_spending(5.20, "Daily train ticket", "Transport", "2023-11-21")
    record_new_spending(89.99, "Internet and electric bill", "Housing/Rent", "2023-11-18")
    record_new_spending(15.00, "Concert tickets", "Leisure", "2023-11-21")
    record_new_spending(12.99, "Lunch at cafe near school", "Food") # No date given
    
    # Try adding one with a non-existent category
    record_new_spending(500.00, "New gaming PC", "Electronics", "2023-11-22")

    # --- 3. Reviewing Logs (READ) ---
    print("\n--- Current Expense Log Review ---")
    current_expenses = viewAllExpenses()
    display_expense_report(current_expenses)

    # --- 4. Corrections and Updates (UPDATE) ---
    # The first expense (ID 1) was the food shop ($25.50)
    print("\n--- Correcting Record ID 1 ---")
    # Change amount and description
    reviseExpense(1, new_amt=30.75, new_desc="Corrected food receipt total after tip")
    
    # The third expense (ID 3) was Housing/Rent ($89.99)
    # Let's accidentally change its category
    print("\n--- 'Oops' Category Change for Record ID 3 ---")
    reviseExpense(3, new_category_name="Transport") # This is a mistake, but shows the update works!
    
    # View updated list
    print("\n--- Log After Corrections ---")
    display_expense_report(viewAllExpenses())

    # --- 5. Removing Errors (DELETE) ---
    # Assume the second expense (ID 2, train ticket) was duplicated and needs removal
    print("\n--- Deleting Duplicated Record ID 2 ---")
    removeExpense(2)
    
    # Try removing one that was never saved
    removeExpense(999)

    # View final list
    print("\n--- Final, Cleaned-Up Expense Report ---")
    display_expense_report(viewAllExpenses())

if __name__ == "__main__":
    main()
