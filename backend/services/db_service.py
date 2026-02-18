import json
import os
import logging
from typing import Dict
from models.idea import Idea

# Use absolute path for DB file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Assume backend directory structure: backend/services/db_service.py -> ../.. relative to current file location?
# backend/services -> .. -> backend
APP_DIR = os.path.dirname(BASE_DIR)
DB_FILE = os.path.join(APP_DIR, "ideas_db.json")
LOG_FILE = os.path.join(APP_DIR, "app.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Use absolute path for DB file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# backend/services -> .. -> backend
APP_DIR = os.path.dirname(BASE_DIR)
# Move DB file outside of backend to prevent uvicorn reload loops
PROJECT_ROOT = os.path.dirname(APP_DIR)
DB_FILE = os.path.join(PROJECT_ROOT, "ideas_db.json")

class DBService:
    def __init__(self):
        logger.info(f"DBService initialized. Using DB file: {DB_FILE}")

    def load_ideas(self) -> Dict[str, Idea]:
        if not os.path.exists(DB_FILE):
            logger.info(f"DB file not found at {DB_FILE}, returning empty DB")
            return {}
        
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                ideas = {}
                for k, v in data.items():
                    try:
                        ideas[k] = Idea.model_validate(v)
                    except Exception as validation_err:
                        logger.error(f"Validation error for idea {k}: {validation_err}")
                logger.info(f"Loaded {len(ideas)} ideas from DB")
                return ideas
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
            return {}

    def save_ideas(self, ideas: Dict[str, Idea]):
        try:
            # Pydantic v2 model_dump, fallback to dict if needed
            data = {}
            for k, v in ideas.items():
                if hasattr(v, 'model_dump'):
                    data[k] = v.model_dump(mode='json')
                elif hasattr(v, 'dict'):
                    # Pydantic v1
                    data[k] = json.loads(v.json())
                else:
                    logger.error(f"Object {k} is not a valid Pydantic model: {type(v)}")
                    continue

            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(ideas)} ideas to {DB_FILE}")
        except Exception as e:
            logger.error(f"Error saving DB to {DB_FILE}: {e}")
            raise e
