from flask import request
from flask_restx import Resource

from src.restx import api
from src.models.pdf import Pdf
from src.serializers.chat_serializer import chat_serializer
from src.utils.chat_util import get_answer

ns_chat = api.namespace('chat')

@ns_chat.route('/<uuid:id>')
class PDFQuestionView(Resource):

    @ns_chat.expect(chat_serializer)
    def post(self, id):

        pdf = Pdf.query.get(str(id))

        if not pdf:
            return {"message": "PDF file not found"}, 404
        
        data = request.get_json()

        if 'question' not in data:
            return {"message": "Question is required"}, 400      

        answer = get_answer(id, data['question'])
        
        return {"answer": answer}, 200