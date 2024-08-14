import uuid
from datetime import datetime

from mongoengine import connect, Document, StringField, IntField, EmbeddedDocument, ListField, EmbeddedDocumentField, \
    DateTimeField

connect("insanise")


class TaskFieldTypeModel(EmbeddedDocument):
    name = StringField(required=True)
    type = StringField(required=True)

    meta = {
        'allow_inheritance': True
    }


class TaskFieldModel(TaskFieldTypeModel):
    id = StringField(default=uuid.uuid4(),required=True, unique=True)
    content = StringField(required=True)


class Task(Document):
    name = StringField(max_length=200, required=True)
    description = StringField(max_length=200, required=True)
    fields = ListField(EmbeddedDocumentField(TaskFieldTypeModel))

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    created_by = IntField(required=True)
    updated_by = IntField(required=True)
    status = StringField(required=True)

    company_id = IntField(required=True)

    assigned_to = ListField(IntField())

class FieldModel(EmbeddedDocument):
    id = StringField(required=True, unique=True)
    name = StringField(required=True)
    type = StringField(required=True)
    content = StringField(required=True)

class UserField(Document):
    task_id = StringField(required=True)
    user_id = IntField(required=True)

    name = StringField(max_length=200, required=True)
    description = StringField(max_length=200, required=True)

    fields = ListField(EmbeddedDocumentField(FieldModel))
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    created_by = IntField(required=True)
    updated_by = StringField(required=True)

    status = StringField(required=True)
    company_id = IntField(required=True)

