
import os
from dotenv import load_dotenv
import openai
# from database import get_connection, close_connection
load_dotenv()
from app.database import get_connection, close_connection

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def list_tables():
    print('list_tables');   
    conn, cur = get_connection()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cur.fetchall()
    print('tables',tables);
    print('============');
    close_connection(conn, cur)
    return [table[0] for table in tables]

def get_table_schema(table_name):
    conn, cur = get_connection()
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
    schema = cur.fetchall()
    close_connection(conn, cur)
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

def suggest_questions(num_questions=3) -> list[str]:
    """
    Suggest a list of questions that a non-technical user might ask about the database.

    Args:
        num_questions (int): The number of questions to generate. Defaults to 3.

    Returns:
        list[str]: A list of suggested questions.
    """
    database_schema = db_get_schema_tool()

    system_prompt = f"""You are a SQL expert with a keen eye for detail.
    Below is the schema of a database:
    ---
    {database_schema}
    ---
    Your task is to generate {num_questions} questions that a non-technical user might ask about this database.
    Please ensure the questions are simple, clear, and relevant to the schema provided.
    Return the questions in a comma-separated list, without any additional text or formatting.
    """
#     system_prompt = f"""
# You are a SQL expert with a keen eye for detail, tasked with assisting non-technical users to understand a database schema. Below is the schema of a database:
# ---
# {database_schema}
# ---
# Imagine you are explaining this schema to someone with no technical background. Your task is to generate {num_questions} questions that such a user might realistically ask to better understand the database. These questions should be simple, clear, and directly related to the schema provided.

# Please format your response as a comma-separated list of questions, with no additional text or formatting. Focus on the kind of queries that help elucidate the structure and purpose of the database elements.
# """
    # system_prompt = f"""You are a SQL expert with a strong attention to detail.
    # This is the schema of a database:
    # ---
    # {database_schema}
    # ---
    # Considering the users are non-technical, create {num_questions} questions that a user may ask about the database.
    # IMPORTANT: Return the questions in a comma-separated list.
    # """
    
    conversation = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": "SELECT * FROM actor LIMIT 10;"
        }
    ]

    ai_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        max_tokens=850
    )
    
    raw_questions = ai_response.choices[0].message.content.replace('\n', '')
    suggested_questions = [question.strip() for question in raw_questions.split(',')]
    
    return suggested_questions