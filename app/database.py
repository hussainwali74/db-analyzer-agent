from pydantic import BaseModel

class DBCredentials(BaseModel):
    host: str
    port: str
    database: str
    user: str
    password: str