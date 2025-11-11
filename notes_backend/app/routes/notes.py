from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError

from ..models import storage
from ..schemas import NoteCreateSchema, NoteSchema, NoteUpdateSchema

blp = Blueprint(
    "Notes",
    "notes",
    url_prefix="/notes",
    description="CRUD operations for notes",
)


@blp.route("")
class NotesCollection(MethodView):
    """PUBLIC_INTERFACE
    Collection resource for listing and creating notes.
    """

    @blp.response(200, NoteSchema(many=True), description="List all notes")
    def get(self):
        """List notes with optional future filters. Returns an array of notes."""
        notes = storage.list_notes()
        return [n.to_dict() for n in notes]

    @blp.arguments(NoteCreateSchema, location="json")
    @blp.response(201, NoteSchema, description="Created note")
    def post(self, json_data):
        """Create a new note and return it with status 201."""
        try:
            title = json_data.get("title", "").strip()
            content = json_data.get("content", "").strip()
            tags = json_data.get("tags", [])
        except (AttributeError, ValidationError) as exc:
            abort(400, message="Invalid request body", errors=str(exc))

        if not title or not content:
            abort(400, message="Both 'title' and 'content' are required and must be non-empty strings.")

        note = storage.create_note(title=title, content=content, tags=tags)
        return note.to_dict()


@blp.route("/<string:note_id>")
class NoteResource(MethodView):
    """PUBLIC_INTERFACE
    Resource for retrieving, updating, and deleting a single note by id.
    """

    @blp.response(200, NoteSchema, description="The requested note")
    def get(self, note_id: str):
        """Get a note by id. Returns 200 with note or 404 if missing."""
        note = storage.get_note(note_id)
        if not note:
            abort(404, message="Note not found")
        return note.to_dict()

    @blp.arguments(NoteUpdateSchema, location="json")
    @blp.response(200, NoteSchema, description="Updated note")
    def put(self, json_data, note_id: str):
        """Update a note by id. Returns 200 with updated note or 404 if missing."""
        if not any(k in json_data for k in ("title", "content", "tags")):
            abort(400, message="At least one of 'title', 'content', or 'tags' must be provided.")

        title = json_data.get("title")
        content = json_data.get("content")
        tags = json_data.get("tags")

        if isinstance(title, str):
            title = title.strip()
            if title == "":
                abort(400, message="'title' cannot be empty.")

        if isinstance(content, str):
            content = content.strip()
            if content == "":
                abort(400, message="'content' cannot be empty.")

        updated = storage.update_note(note_id, title=title, content=content, tags=tags)
        if not updated:
            abort(404, message="Note not found")
        return updated.to_dict()

    @blp.response(204, description="Deleted")
    def delete(self, note_id: str):
        """Delete a note by id. Returns 204 if deleted or 404 if missing."""
        ok = storage.delete_note(note_id)
        if not ok:
            abort(404, message="Note not found")
        # 204 No Content must not return a body
        return ""
