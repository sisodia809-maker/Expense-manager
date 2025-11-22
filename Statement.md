# **Project Statement:  Expense Manager**

## **1\. Problem Statement**

Many individuals lack a simple, accessible, and quick method for recording daily and recurring expenditures in a structured, local format. Relying solely on manual paper tracking is inefficient, while complex cloud-based tools are often overkill for basic personal finance needs. This project addresses the need for a **lightweight, persistent, and categorize-driven expense management utility** that offers high data integrity and ease of use without the overhead of a graphical interface or online service.

## **2\. Scope of the Project**

The scope of this project is confined to a self-contained, console-based application implemented in **Python 3**.

### **In Scope:**

* **Core CRUD Functionality:** Creating, reading, updating, and deleting expense records.  
* **Database Management:** Use of the built-in sqlite3 library for persistent, local storage of all data (personal\_finance.db).  
* **Categorization:** Defining and linking expenses to a set of user-defined categories.  
* **Batch Data Import:** Implementation of a robust function to load multiple transactional records from a standard CSV file (import\_data.csv).  
* **Console Reporting:** Generating clear, formatted text reports of expense history and summaries directly in the terminal.

### **Out of Scope:**

* **User Interface (UI):** No graphical user interface (GUI) or web interface will be developed.  
* **Advanced Analytics:** No complex reporting, budgeting, forecasting, or graphing tools.  
* **Authentication/Security:** No multi-user support or external sign-in mechanism is included.  
* **External Dependencies:** The project will only use Python's standard library (sqlite3, csv, os, datetime).

## **3\. Target Users**

The primary users of this utility are individuals who prefer control over their data and simplicity in their tools.

* **Students and Individuals:** Seeking a fast, free, and straightforward way to track personal spending without requiring internet access.  
* **Developers and Python Enthusiasts:** Looking for a practical, real-world example of database interaction and file handling in Python.  
* **Small Teams/Groups:** Requiring a simple, non-shared utility for local, segmented expense logging.

## **4\. High-Level Features**

| Feature Name | Description |
| :---- | :---- |
| **SQLite Persistence** | All category and expense data is saved locally using SQLite, ensuring data is retained between executions. |
| **Expense CRUD** | Users can record new spending, view a historical log, modify existing entries, and delete incorrect records by ID. |
| **Category Management** | Ability to define, list, and assign expenses to categories (e.g., Food, Transport, Utilities) for structured tracking. |
| **CSV Bulk Import** | A function to read structured data from a CSV file and batch-process it into the database. |
| **Clear Console Reports** | Displays the current state of the expense log in a clean, easy-to-read tabular format in the terminal. |

