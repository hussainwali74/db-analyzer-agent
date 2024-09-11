from pydantic import BaseModel
import psycopg2
from app.config import load_config


class DBCredentials(BaseModel):
    host: str
    port: str
    database: str
    user: str
    password: str


def get_connection():
    db_credentials:DBCredentials = DBCredentials(**load_config())
    conn = psycopg2.connect(
        dbname=db_credentials.database,
        user=db_credentials.user,
        password=db_credentials.password,
        host=db_credentials.host,
        port=db_credentials.port,
    )
    cur = conn.cursor()
    return conn, cur


def close_connection(conn, cur):
    cur.close()
    conn.close()
