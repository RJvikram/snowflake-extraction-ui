# Snowflake Extraction UI

A Streamlit-based UI for configuring and previewing SQL extracts from Snowflake, with support for filters, CASE WHEN rules, and CSV uploads.

---

## 🛠️ Setup Instructions

### 1. Clone or Download the Repository

Download or clone this project to your local machine.

### 2. Install Python Dependencies

Make sure you have Python 3.7+ installed.  
Install required packages:

```sh
pip install -r requirements.txt
```

### 3. Configure Snowflake Credentials

Edit the file [`/.streamlit/secrets.toml`](.streamlit/secrets.toml) with your Snowflake account details:

```toml
[snowflake]
user = "YOUR_USER"
password = "YOUR_PASSWORD"
account = "YOUR_ACCOUNT"
warehouse = "YOUR_WAREHOUSE"
database = "YOUR_DATABASE"
schema = "YOUR_SCHEMA"
```

### 4. (Optional) Adjust Spell Checker Settings

The file [`/.vscode/settings.json`](.vscode/settings.json) contains custom spell-check words for VS Code.

### 5. Run the Streamlit App

```sh
streamlit run snowflake_extraction_ui_clean.py
```

---

## 🧑‍💻 Code Walkthrough

### 1. **Imports and Config**

- Imports Streamlit, Snowflake connector, Pandas, and UUID.
- Sets up the Streamlit page title and layout.

### 2. **Snowflake Connection**

- Uses `st.cache_resource` to cache the Snowflake connection.
- Reads credentials from `st.secrets["snowflake"]`.

### 3. **Source Selection**

- Fetches available TABLES or VIEWS from Snowflake.
- Lets the user select a source and displays its columns.

### 4. **Configuration Name**

- Allows selection of an existing configuration (placeholder) or entry of a new configuration name.

### 5. **Global Extract Filters**

- User specifies the number of filters (1-5).
- For each filter, user selects column, condition, value(s), logic (AND/OR), and case sensitivity.
- Filters are combined into a SQL WHERE clause.

### 6. **CASE WHEN Rules Engine**

- Optionally add a CASE WHEN rule to create a new derived column.
- User specifies rule name, description, column, operator, value, THEN, ELSE, and new column name.

### 7. **SQL Generation**

- Dynamically builds the SQL query based on selected filters and rules.
- Shows the generated SQL for preview.

### 8. **Preview Results**

- Executes the generated SQL and displays the result as a table.

### 9. **Save Configuration as View**

- Allows saving the current configuration as a new Snowflake view.

### 10. **Upload CSV to Insert Data**

- User can upload a CSV file.
- Displays the uploaded data.
- Inserts the data into the selected table in Snowflake.

---

## 📁 Files

- [`snowflake_extraction_ui_clean.py`](snowflake_extraction_ui_clean.py): Main Streamlit app.
- [`employees.csv`](employees.csv): Example CSV data.
- [`.streamlit/secrets.toml`](.streamlit/secrets.toml): Snowflake credentials.
- [`.vscode/settings.json`](.vscode/settings.json): VS Code settings.

---

## 🚀 Usage

1. Start the app.
2. Select a source table/view.
3. Configure filters and rules as needed.
4. Preview and save SQL extracts.
5. Optionally upload and insert CSV data.

---

## 📝 Notes

- Ensure your Snowflake user has privileges to read tables/views and create views.
- The UI is designed for demonstration and may need enhancements for production use.
