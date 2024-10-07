from sqlmodel import Field, SQLModel, Index


class Position(SQLModel, table=True):
    vesselid: str = Field(primary_key=True)
    timehours: int = Field(primary_key=True)
    x: int
    y: int
    z: int
    # __table_args__ = (
    #     Index("timehours_gist", "timehours", postgresql_using="gist"),
    # )
    
