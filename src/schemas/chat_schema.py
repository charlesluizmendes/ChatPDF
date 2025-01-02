from marshmallow import Schema, fields, validate

class ChatSchema(Schema):
    id = fields.String(
        required=True, 
        validate=validate.Length(
            min=1, 
            error="O campo 'id' não pode ser vazio."
        )
    )
    content = fields.String(
        required=True, 
        validate=validate.Length(
            min=1, 
            error="O campo 'content' não pode ser vazio."
        )
    )
