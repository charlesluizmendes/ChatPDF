from marshmallow import fields, validate
from src.config import ma
from src.models.pdf import Pdf  

class PdfSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Pdf

    name = fields.Str(required=True, validate=validate.Length(min=1, error="O Nome não pode ser vazio"))