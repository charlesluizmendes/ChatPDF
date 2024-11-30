from flask_restx import fields
from src.restx import api

pdf_serializer = api.model('Pdf', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True),
    'file': fields.Raw(required=True)
})
