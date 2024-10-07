from src.db.session import SessionLocal
from src.models.position import Position
import logging

logger = logging.getLogger(__name__)

import json
import sqlalchemy


class PositionService:

    def get_position(self, timehours: int, vessel_id: str | None = None):
        """
        Gets the Position that is closest to given timehours,
        with optional vessel_id to get Position for a particular Vessel
        Note: the closest timehours maybe behind or ahead of the passed timehours
        """
        with SessionLocal() as session:
            q = session.query(Position)
            if vessel_id:
                q = q.filter(Position.vesselid == vessel_id)
            if timehours:
                q = q.order_by(sqlalchemy.func.abs(Position.timehours - timehours))
            position = q.limit(1).first()
            if position:
                return position.model_dump_json()
        return None

    def store_position(self, position: Position):
        """
        Upserts the passed position updating the x,y,z values if an entry with same vesselid, timehours already exists
        """
        with SessionLocal() as session:
            session.merge(position)
            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                # this should ideally have been caught by the Pydantic models
                logger.warning("error trying to store position", position, e)
                raise e
            if position:
                return position.model_dump_json()
        return None

    def get_series(self, vessel_id: str | None = None):
        """
        Returns a series of Positions, can be filtered to include Positions only for the passed vesselid
        """
        with SessionLocal() as session:
            q = session.query(Position)
            if vessel_id:
                q = q.filter(Position.vesselid == vessel_id)
            return json.dumps(list(map(lambda x: x.model_dump(), q.all())))
