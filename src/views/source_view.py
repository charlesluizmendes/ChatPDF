from flask_restx import Resource
from marshmallow import ValidationError
from werkzeug.datastructures import FileStorage

from src.restx import api
from src.schemas.pdf_schema import PdfSchema
from src.utils.llm_util import upload_pdf, delete_pdf

ns_source = api.namespace('source')

file_upload_parser = ns_source.parser()
file_upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='file')

@ns_source.route('/addFile')
class AddFileView(Resource):

    @ns_source.expect(file_upload_parser)
    def post(self):
        args = file_upload_parser.parse_args()
        data = args.get('file')
        schema = PdfSchema()

        try:
            validated_data = schema.load_file(data)
        except ValidationError as err:
            return {"message": err.messages}, 400

        id = validated_data['id']
        name = validated_data['name']
        content = validated_data['content']

        upload_pdf(id, name, content)
        
        return {"id": id}, 201
    
@ns_source.route('/delete/<uuid:id>')
class DeleteFileView(Resource):
    
    def delete(self, id):
        if not id:
            return {"message": "O 'id' não pode ser nulo"}, 400

        result = delete_pdf(id)

        if result:
            return {"message": "Documento excluído com sucesso"}, 200
        else:
            return {"message": "Não foi possível excluir o Documento"}, 400