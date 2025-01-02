from flask_restx import fields
from src.restx import api

chat_serializer = api.model('Chat', {
    'id': fields.String(required=True),
    'content': fields.String(required=True)
})
