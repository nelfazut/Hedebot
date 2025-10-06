import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    discord_id: int | None = Field(default=None, primary_key=True)
    display_name: str
    display_color: str = ""
    last_played: datetime.date | None = None
    streak: int = 0
    total_pr: float = 0


sqlite_file_name = "users.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


def create_db_and_tables():
    engine = create_engine(sqlite_url, echo=False)
    SQLModel.metadata.create_all(engine)


def add_users(users: list[User]):
    engine = create_engine(sqlite_url, echo=False)

    with Session(engine) as session:
        for user in users:
            session.add(user)
        session.commit()


def delete_users(users: list[int]):
    engine = create_engine(sqlite_url, echo=False)

    with Session(engine) as session:
        for discord_id in users:
            user = session.exec(select(User).where(User.discord_id == discord_id)).one()
            session.delete(user)
        session.commit()


def get_user(discord_id: int):
    engine = create_engine(sqlite_url, echo=False)

    with Session(engine) as session:
        statement = select(User).where(User.discord_id == discord_id)
        results = session.exec(statement)
        for user in results:
            return user

def get_all() => list[User]:
    engine = create_engine(sqlite_url, echo=False)
    users = []
    with Session(engine) as session:
        statement = select(User).where(User.total_pr != 0).order_by(User.total_pr.desc())
        results = session.exec(statement)
        for user in results:
            users.append(user)
    return users


def update_users(users: list[User]):
    engine = create_engine(sqlite_url, echo=False)

    with Session(engine) as session:
        for user in users:
            session.add(user)
        session.commit()
