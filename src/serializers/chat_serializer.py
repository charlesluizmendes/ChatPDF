from flask_restx import fields
from src.restx import api

chat_serializer = api.model('Chat', {
    'question': fields.String(required=True),
})
