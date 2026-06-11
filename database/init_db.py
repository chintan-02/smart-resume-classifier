from database.db import Base, engine
from database import models  # noqa: F401


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
    print("ResumeIQ database initialized successfully.")


if __name__ == "__main__":
    init_database()
