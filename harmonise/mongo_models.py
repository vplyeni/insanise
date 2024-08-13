import datetime
import uuid
from typing import List

from conmongo.mongo_model import mongo_model

"""
Field
"""
class TaskFieldModel:
    id: str
    type: str
    name: str
    content: str

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'content': self.content
        }

    def __init__(self, name: str, _type: str, content: str = "", _id:str = str(uuid.uuid4())):
        self.id = _id
        self.name = name
        self.type = _type
        self.content = content


class FieldBaseModel(mongo_model):
    task_id: str
    user_id: int

    created_at: str | None
    updated_at: str | None

    fields: List[TaskFieldModel]

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'fields': [field.to_dict() for field in self.fields]
        }

    def __init__(self, task_id: str, user_id: int, fields: List[TaskFieldModel], created_at: str, updated_at: str):
        super().__init__()
        self.task_id = task_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.fields = fields


class FieldCreateModel(FieldBaseModel):
    def __init__(self, task_id: str, user_id: int, fields: List[TaskFieldModel],
                 created_at: str = str(datetime.datetime.now()), updated_at: str = str(datetime.datetime.now())):
        super().__init__(task_id=task_id, user_id=user_id, fields=fields, created_at=created_at, updated_at=updated_at)
        self.task_id = task_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.fields = fields

    pass


class FieldUpdateModel(FieldBaseModel):
    _id: str

    def to_dict(self):
        return {
            '_id': str(self._id),
            'task_id': self.task_id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'fields': [field.to_dict() for field in self.fields]
        }

    def __init__(self, _id: str, task_id: str, user_id: int, fields: List[TaskFieldModel], created_at: str,
                 updated_at: str = str(datetime.datetime.now())):
        super().__init__(task_id=task_id, created_at=created_at, fields=fields, user_id=user_id, updated_at=updated_at)
        self._id = _id
        self.task_id = task_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.fields = fields


class FieldGetModel(FieldBaseModel):
    _id: str

    def to_dict(self):
        return {
            '_id': str(self._id),
            'task_id': self.task_id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'fields': [field.to_dict() for field in self.fields]
        }

    def __init__(self, _id: str, task_id: str, user_id: int, fields: List[TaskFieldModel], created_at: str,
                 updated_at: str):
        super().__init__(task_id=task_id, created_at=created_at, fields=fields, user_id=user_id, updated_at=updated_at)
        self._id = _id
        self.task_id = task_id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.fields = fields


"""
Task
"""
class TaskBaseModel(mongo_model):
    name: str
    description: str
    fields: List[TaskFieldModel]

    created_date: str | None
    updated_date: str | None

    created_by: str | None
    updated_by: str | None

    company_id: str

    def __init__(self, name: str, description: str, fields: List[TaskFieldModel],
                 created_by: str, updated_by: str,
                 company_id: str, created_date: str = str(datetime.datetime.now()),
                 updated_date: str = str(datetime.datetime.now())):
        super().__init__()
        self.name = name
        self.description = description
        self.fields = fields
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by
        self.company_id = company_id


class TaskCreateModel(TaskBaseModel):
    user_ids: List[str]

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'fields': self.fields,
            'user_ids': self.user_ids,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'company_id': self.company_id
        }

    def __init__(self, name: str, description: str, fields: List[TaskFieldModel],
                 created_by: str, updated_by: str,
                 company_id: str, user_ids: List[str], ):
        super().__init__(name, description, fields, created_by, updated_by, company_id)
        self.name = name
        self.description = description
        self.fields = fields
        self.user_ids = user_ids


class TaskGetModel(TaskBaseModel):
    _id: str

    def to_dict(self):
        return {
            '_id': str(self._id),
            'name': self.name,
            'description': self.description,
            'fields': self.fields,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'company_id': self.company_id,
        }

    def __init__(self, _id: str, name: str, description: str, fields: List[TaskFieldModel], created_by: str,
                 updated_by: str,
                 company_id: str):
        super().__init__(name, description, fields, created_by, updated_by, company_id)
        self._id = _id
        self.name = name
        self.description = description
        self.fields = fields
        self.created_by = created_by
        self.updated_by = updated_by
        self.company_id = company_id


class TaskUpdateModel(TaskCreateModel):
    _id: str

    def to_dict(self):
        return {
            '_id': str(self._id),
            'name': self.name,
            'description': self.description,
            'fields': self.fields,
            'user_ids': self.user_ids
        }

    def __init__(self, _id: str, name: str, description: str, fields: List[TaskFieldModel], user_ids: List[str],
                 created_by: str, updated_by: str, company_id: str):
        super().__init__(name, description, fields, created_by, updated_by, company_id, user_ids)
        self._id = _id
        self.name = name
        self.description = description
        self.fields = fields
        self.user_ids = user_ids
        self.updated_date = str(datetime.datetime.now())
        self.updated_by = updated_by
        self.created_date = None
