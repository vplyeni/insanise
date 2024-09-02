import uuid
from datetime import datetime

from mongoengine import connect, Document, StringField, IntField, EmbeddedDocument, ListField, EmbeddedDocumentField, \
    DateTimeField, BooleanField

connect("insanise")


class TaskFieldTypeModel(EmbeddedDocument):
    id = StringField(default=lambda: str(uuid.uuid4()), unique=False)
    name = StringField(required=True)
    type = StringField(required=True)


class Task(Document):
    name = StringField(max_length=200, required=True)
    description = StringField(max_length=1024, required=True)
    fields = ListField(EmbeddedDocumentField(TaskFieldTypeModel))

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    # Time required to complete the task, in seconds
    task_period = IntField(required=True)

    created_by = IntField(required=True)
    updated_by = IntField(required=True)

    status = StringField(required=True)

    company_id = IntField(required=True)

    assigned_to = ListField(IntField())


class TaskFieldModel(EmbeddedDocument):
    id = StringField(default=str(uuid.uuid4()), unique=False)
    name = StringField(required=True)
    type = StringField(required=True)
    content = StringField(default="", required=True, blank=True)
    represented_name = StringField(default="", required=True, blank=True)
    updated_at = DateTimeField(default=datetime.utcnow)


class TaskUser(Document):
    task_id = StringField(required=True)
    user_id = IntField(required=True)
    user_full_name = StringField(required=True)
    username = StringField(required=True)

    name = StringField(max_length=200, required=True)
    description = StringField(max_length=1000, required=True)

    fields = ListField(EmbeddedDocumentField(TaskFieldModel))
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    created_by = IntField(required=True)
    updated_by = IntField(required=True)

    status = StringField(required=True)
    company_id = IntField(required=True)

    due_date = DateTimeField(default=datetime.now)
