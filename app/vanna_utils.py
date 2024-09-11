from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore


from app.config import load_config
from dotenv import load_dotenv, find_dotenv

from app.models import Question

_ = load_dotenv(find_dotenv())
import os

config = load_config()
import logging

logger = logging.getLogger(__name__)


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)


def get_vanna_instance():
    vn = MyVanna(
        config={
            "api_key": config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"),
            "model": "gpt-4o",
            "path": "./fast_api_chromadb",
        }
    )
    # print('config.get("host")',config.get("host"));
    # print('============');
    # vn.connect_to_postgres(
    #         host=config.get('host'),
    #         dbname=config.get('database'),
    #         port=config.get('port'),
    #         user=config.get('user'),
    #         password=config.get('password'),
    #     )
    vn.connect_to_postgres(
        host="localhost",
        dbname="dvdrental",
        port="5432",
        user="postgres",
        password="1122",
    )

    return vn


def train_vanna(vn: MyVanna):

    logger.info("getting schema")
    # The information schema query may need some tweaking depending on your database. This is a good starting point.
    df_information_schema = vn.run_sql(
        "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema='public'"
    )

    logger.info("generating plan")
    # This will break up the information schema into bite-sized chunks that can be referenced by the LLM
    plan = vn.get_training_plan_generic(df_information_schema)

    logger.info("training...")
    # If you like the plan, then uncomment this and run it to train
    vn.train(plan=plan)
    logger.info("done training")


def suggest_questions(vn):
    """
    LLM will look at the db schema, training data and generate questions that user may ask related to the db.
    """

    questions = vn.generate_questions()
    print("------------------------------------")
    print(f"{questions=}")
    print("------------------------------------")
    return questions


def ask_question(question: Question):
    vn = get_vanna_instance()
    res = vn.ask(question=question.question, visualize=False, print_results=False)
    answer = "Something went wrong"
    if res[0] is not None:
        answer = vn.generate_summary(question=question.question, df=res[1])
    return answer
