import logging

from sqlmodel import SQLModel

from src.models.position import Position
from src.db.session import SessionLocal
from src.db.session import engine, settings

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


import json


def create_init_data(file_name="init-data.json") -> None:
    with open(file_name) as f:
        positions = json.loads("".join(f.readlines()))
        with SessionLocal() as session:
            for position in positions:
                position_obj = Position(**position)
                session.merge(position_obj)
        session.commit()


def initialize():
    SQLModel.metadata.create_all(engine)


def main() -> None:
    logger.info("Creating initial data")
    initialize()
    create_init_data()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
