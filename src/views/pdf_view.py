from flask_restx import Resource
from werkzeug.datastructures import FileStorage

from src.restx import api
from src.config import db
from src.models.pdf import Pdf
from src.schemas.pdf_schema import PdfSchema
from src.utils.pdf_util import set_pdf

ns_pdf = api.namespace('pdf')

file_upload_parser = ns_pdf.parser()
file_upload_parser.add_argument('name', location='form', type=str, required=True, help='Nome do PDF')
file_upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='PDF file')

@ns_pdf.route('/')
class AddFileView(Resource):

    @ns_pdf.expect(file_upload_parser)
    def post(self):
        args = file_upload_parser.parse_args()

        pdf_file = args.get('file')
        pdf_name = args.get('name')

        if not pdf_file:
            return {"message": "Nenhum arquivo enviado"}, 400
        
        schema = PdfSchema()
        errors = schema.validate({"name": pdf_name})

        if errors:
            return {"message": "Erro de validação", "errors": errors}, 400

        file_content = pdf_file.read()

        pdf = Pdf(name=pdf_name, file=file_content)
        db.session.add(pdf)
        db.session.commit()

        set_pdf(pdf.id, pdf_name, file_content)
        
        return {"id": pdf.id}, 201