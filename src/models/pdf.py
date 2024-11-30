import uuid
from sqlalchemy import String
from src.config import db

class Pdf(db.Model):
    __tablename__ = 'Pdf'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    file = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, name, file):
        self.name = name
        self.file = file