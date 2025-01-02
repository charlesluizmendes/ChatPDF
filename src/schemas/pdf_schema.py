import uuid
from marshmallow import Schema, fields, ValidationError

class PdfSchema(Schema):
    id = fields.String(dump_only=True)
    file = fields.Raw(required=True)

    @staticmethod
    def validate_file(file):
        if not file:
            raise ValidationError("O arquivo é obrigatório.")
        if not hasattr(file, "filename"):
            raise ValidationError("Formato de arquivo inválido.")
        return file

    def load_file(self, file):
        validated_file = self.validate_file(file)
        return {
            "id": str(uuid.uuid4()),
            "name": validated_file.filename,
            "content": validated_file.read(),
        }
