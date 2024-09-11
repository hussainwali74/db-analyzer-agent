from fastapi import APIRouter, HTTPException
from app.database import DBCredentials
from app.models import Question
from app.config import load_config, save_config
from app.vanna_utils import get_vanna_instance, suggest_questions, ask_question, train_vanna
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/db_credentials")
async def set_db_credentials(credentials: DBCredentials):
    try:
        config = load_config()

        config.update(credentials.dict())
        save_config(config)
        vn = get_vanna_instance()
        logger.info("Database credentials updated and connection established")
        return {"message": "Database credentials updated successfully"}
    except Exception as e:
        logger.error(f"Error setting database credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/train")
async def train_model():
    try:
        vn = get_vanna_instance()
        logger.info("vn instantiated")
        train_vanna(vn)
        logger.info("Model training completed")
        return {"message": "Model training completed successfully"}
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest_questions")
async def get_suggested_questions():
    try:
        vn = get_vanna_instance()
        questions = suggest_questions(vn)
        logger.info("Questions suggested successfully")
        return {"suggested_questions": questions}
    except Exception as e:
        logger.error(f"Error suggesting questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask_question")
async def ask_db_question(question: Question):
    try:
        answer = ask_question(question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
