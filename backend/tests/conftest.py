import pytest
from sqlmodel import SQLModel

from app.db.session import engine
import app.models.tables  # noqa: F401


@pytest.fixture(autouse=True)
def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
