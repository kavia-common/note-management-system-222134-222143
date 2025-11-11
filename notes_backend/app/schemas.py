from marshmallow import Schema, fields, validate


class NoteBaseSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=256), description="Title of the note")
    content = fields.Str(required=True, validate=validate.Length(min=1), description="Content/body of the note")
    tags = fields.List(fields.Str(validate=validate.Length(max=64)), required=False, description="Optional tags")


class NoteCreateSchema(NoteBaseSchema):
    """Schema for creating a note."""
    pass


class NoteUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=256), description="Title of the note")
    content = fields.Str(required=False, validate=validate.Length(min=1), description="Content/body of the note")
    tags = fields.List(fields.Str(validate=validate.Length(max=64)), required=False, description="Optional tags")


class NoteSchema(Schema):
    id = fields.Str(required=True, description="Identifier of the note")
    title = fields.Str(required=True, description="Title of the note")
    content = fields.Str(required=True, description="Content/body of the note")
    tags = fields.List(fields.Str(), required=True, description="Tags for the note")
    created_at = fields.Float(required=True, description="Creation timestamp (epoch seconds)")
    updated_at = fields.Float(required=True, description="Last update timestamp (epoch seconds)")
