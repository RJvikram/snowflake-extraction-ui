import streamlit as st
import snowflake.connector
import pandas as pd
import uuid

# --- Config ---
st.set_page_config(page_title="Snowflake Extraction UI", layout="centered")
st.title("❄️ Extract Configuration")

# --- Connect to Snowflake ---
@st.cache_resource
def get_connection():
    creds = st.secrets["snowflake"]
    return snowflake.connector.connect(
        user=creds["user"],
        password=creds["password"],
        account=creds["account"],
        warehouse=creds["warehouse"],
        database=creds["database"],
        schema=creds["schema"]
    )

conn = get_connection()
cursor = conn.cursor()

# --- Get Tables or Views ---
def fetch_sources(source_type):
    cursor.execute(f"SHOW {source_type}")
    return [row[1] for row in cursor.fetchall()]

def describe_columns(source_type, source_name):
    cursor.execute(f"DESC {source_type} {source_name}")
    return [col[0] for col in cursor.fetchall()]

# --- Filters ---
def build_filter_sql(filters):
    clauses = []
    for i, (col, cond, val1, val2, logic, cs) in enumerate(filters):
        clause = ""
        if cond == "BETWEEN":
            clause = f"{col} BETWEEN '{val1}' AND '{val2}'"
        elif cond == "IN":
            items = ", ".join([f"'{v.strip()}'" for v in val1.split(",")])
            clause = f"{col} IN ({items})"
        elif cond == "LIKE":
            clause = f"{col} LIKE '%{val1}%'"
        else:
            clause = f"{col} {cond} '{val1}'"
        clauses.append(clause)
        if i < len(filters) - 1:
            clauses.append(logic)
    return " ".join(clauses)

# --- CASE WHEN ---
def build_case_when(rules):
    lines = []
    for rule in rules:
        line = f"WHEN {rule['column']} {rule['operator']} '{rule['value']}' THEN '{rule['then']}'"
        if rule['else']:
            line += f" ELSE '{rule['else']}'"
        lines.append(line)
    return f"CASE\n" + "\n".join(lines) + f"\nEND AS {rules[0]['alias']}"

# --- UI: Source Selection ---
source_type = st.selectbox("Select Source Type", ["TABLE", "VIEW"])
sources = fetch_sources(source_type + "S")
source_name = st.selectbox("Select Source Name", sources)

if source_name:
    st.success(f"Selected: {source_name}")
    columns = describe_columns(source_type, source_name)

# --- UI: Configuration Name ---
st.subheader("📁 Configuration")
existing_configs = ["None"]
existing_config = st.selectbox("Select Existing Configuration", existing_configs)
new_config_name = st.text_input("Enter New Configuration Name")

# --- UI: Filters ---
st.subheader("🔎 Global Extract Filters")
filter_count = st.number_input("Number of Filters", 1, 5, 1)
filters = []

for i in range(filter_count):
    with st.expander(f"Filter {i+1}"):
        f_col = st.selectbox("Column", columns, key=f"col_{i}")
        f_cond = st.selectbox("Condition", ["=", "!=", "LIKE", "IN", "BETWEEN", "<", "<=", ">", ">="], key=f"cond_{i}")
        f_val1 = st.text_input("Value", key=f"val1_{i}")
        f_val2 = st.text_input("AND Value (for BETWEEN only)", key=f"val2_{i}") if f_cond == "BETWEEN" else None
        case_sensitive = st.checkbox("Case sensitive", key=f"cs_{i}")
        logic = st.selectbox("Combine with next filter", ["AND", "OR"], key=f"log_{i}")
        filters.append((f_col, f_cond, f_val1, f_val2, logic, case_sensitive))

# --- UI: CASE WHEN ---
st.subheader("⚙️ Attributes (Rules Engine)")
add_rule = st.checkbox("Add CASE WHEN Rule")
rules = []

if add_rule:
    rule_name = st.text_input("Rule Name")
    rule_desc = st.text_input("Description")
    rule_col = st.selectbox("Rule Column", columns)
    rule_op = st.selectbox("Operator", ["=", "!=", "LIKE"])
    rule_val = st.text_input("Value")
    rule_then = st.text_input("THEN")
    rule_else = st.text_input("ELSE")
    rule_new_col = st.text_input("New Column Name")
    rules.append({
        "column": rule_col,
        "operator": rule_op,
        "value": rule_val,
        "then": rule_then,
        "else": rule_else,
        "alias": rule_new_col
    })

# --- SQL Generation ---
st.subheader("🧠 Preview SQL")
where_sql = build_filter_sql(filters)
if rules:
    case_expr = build_case_when(rules)
    query = f"""WITH base AS (SELECT * FROM {source_name})\nSELECT *, {case_expr} FROM base"""
else:
    query = f"SELECT * FROM {source_name}"
    if where_sql:
        query += f" WHERE {where_sql}"
st.code(query, language="sql")

# --- Preview Results ---
if st.button("Preview Results"):
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    except Exception as e:
        st.error(f"Query error: {e}")

# --- Save View ---
st.subheader("💾 Save Configuration")
if st.button("Save as View"):
    if new_config_name:
        try:
            view_name = new_config_name + "_" + str(uuid.uuid4())[:6]
            cursor.execute(f"CREATE OR REPLACE VIEW {view_name} AS {query}")
            st.success(f"Configuration saved as view: {view_name}")
        except Exception as e:
            st.error(f"Saving failed: {e}")
    else:
        st.warning("Enter a configuration name.")

# --- Upload CSV ---
st.subheader("📤 Upload CSV to Insert into Selected Table")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file:
    df_upload = pd.read_csv(uploaded_file)
    st.dataframe(df_upload.head())
    if st.button("Insert Data"):
        try:
            for _, row in df_upload.iterrows():
                values = ",".join([f"'{str(v)}'" for v in row.values])
                cursor.execute(f"INSERT INTO {source_name} VALUES ({values})")
            st.success("Data inserted successfully.")
        except Exception as e:
            st.error(f"Insertion failed: {e}")




# [snowflake]
# user = "VikramKumar"
# password = "Softude@123456"
# account = "hjixexz-rk20363"
# warehouse = "COMPUTE_WH"
# database = "EXTRACTION_FRAMEWORK_DB"
# schema = "EXTRACTION_CONFIG"
