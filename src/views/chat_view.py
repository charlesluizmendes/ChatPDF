from flask import request
from flask_restx import Resource
from marshmallow import ValidationError

from src.restx import api
from src.schemas.chat_schema import ChatSchema
from src.serializers.chat_serializer import chat_serializer
from src.utils.llm_util import get_answer

ns_chat = api.namespace('chat')

@ns_chat.route('/message')
class MessageView(Resource):

    @ns_chat.expect(chat_serializer)
    def post(self):
        data = request.get_json()
        schema = ChatSchema()

        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return {"message": err.messages}, 400

        id = validated_data['id']
        content = validated_data['content']

        answer = get_answer(id, content)
        
        return {"content": answer}, 200