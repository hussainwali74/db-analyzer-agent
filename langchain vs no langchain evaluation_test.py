from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

db = SQLDatabase.from_uri("postgresql://postgres:1122@localhost:5432/dvdrental")

from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

llm = ChatOpenAI(temperature=0)

toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(model="gpt-4o"))
tools = toolkit.get_tools()



list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables") # string of table names
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema") # string of table schema, 3 rows from the table
@tool
def db_get_schema_tool(q:str) -> str:
    """
    Get the schema of the database.
    """

    tables = list_tables_tool.invoke('')
    tables = tables.split(' ,')
    print('tables',tables);
    print('============');
    if len(tables) == 0:
        return "Error: Query failed. Please rewrite your query and try again."
    schema = ''
    if len(tables) > 10:
        for i in range(0, len(tables), 10):
            schema += get_schema_tool.invoke(','.join(tables[i:i+10]))
    else:
        schema = get_schema_tool.invoke(','.join(tables))

    print('schema',len(schema));
    if not schema:
        return "Error: getting schema failed."
    return schema

schema = db_get_schema_tool.invoke('s')

query_check_system = f"""You are a SQL expert with a strong attention to detail.
 this is the schema of a database:
 ---
 {schema}
 ---
Considering the users are non-technical, create 3 questions that user may ask about the database.

"""
from langchain_core.prompts import ChatPromptTemplate

query_check_prompt = ChatPromptTemplate.from_messages(
    [("system", query_check_system)]
)

query_check = query_check_prompt | ChatOpenAI(model="gpt-4o",temperature=0)
# query_check.invoke('s')
res = query_check.invoke({"messages": [("user", "begin")]})
print('============');
print('============');
print('============');
print('res',res);
print('============');



# ===============================================================
import os
import psycopg2
from dotenv import load_dotenv
import openai

load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to the PostgreSQL database
conn = psycopg2.connect("dbname=dvdrental user=postgres password=1122 host=localhost port=5432")
cur = conn.cursor()

def list_tables():
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cur.fetchall()
    return [table[0] for table in tables]

def get_table_schema(table_name):
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
    schema = cur.fetchall()
    return schema

def db_get_schema_tool():
    tables = list_tables()
    if not tables:
        return "Error: Query failed. Please rewrite your query and try again."
    
    schema = {}
    for table in tables:
        schema[table] = get_table_schema(table)
    
    if not schema:
        return "Error: getting schema failed."
    return schema

schema = db_get_schema_tool()

query_check_system = f"""You are a SQL expert with a strong attention to detail.
 this is the schema of a database:
 ---
 {schema}
 ---
Considering the users are non-technical, create 3 questions that user may ask about the database.
"""

response = openai.Completion.create(
  engine="gpt-4o",
  prompt=query_check_system,
  max_tokens=150
)

print(response.choices[0].text.strip())

# Close the database connection
cur.close()
conn.close()