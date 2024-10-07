from src.db.session import SessionLocal
from src.models.position import Position
import logging

logger = logging.getLogger(__name__)

import json
import sqlalchemy

class PositionService:

    def get_position(self, vessel_id: str|None = None, timehours: int|None = None):
        with SessionLocal() as session:
            q = session.query(Position)
            if vessel_id:
                q = q.filter(Position.vesselid == vessel_id)
            if timehours:
                q = q.order_by(sqlalchemy.func.abs(Position.timehours - timehours))
            position = q.limit(1).first()
            return position.model_dump_json()


    def store_position(self, position: Position):
        with SessionLocal() as session:
            session.merge(position)
            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                logger.warning("error trying to store position", position, e)
                return str(e)
            except Exception as e:
                logger.warning("error trying to store position", position, e)
                return str(type(e))
            return position.model_dump_json()


    def get_series(self, vessel_id: str|None = None):
        with SessionLocal() as session:
            q = session.query(Position)
            if vessel_id:
                q = q.filter(Position.vesselid == vessel_id)
            return json.dumps(list(map(lambda x: x.model_dump(), q.all())))