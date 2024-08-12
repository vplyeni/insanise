import datetime
from typing import List, Any, Mapping

from bson import ObjectId

from conmongo.connection import mongo_task, mongo_field
from .mongo_models import (TaskBaseModel, TaskFieldModel, TaskCreateModel,
                           TaskGetModel, TaskUpdateModel, FieldGetModel,
                           FieldUpdateModel, FieldBaseModel, FieldCreateModel)


def create_task(creator_user, name: str = "", description: str = "",
                fields: List[TaskFieldModel] = None,
                user_ids=None) -> TaskCreateModel:
    if user_ids is None:
        user_ids = []

    created_by = str(creator_user.id)
    company_id = str(creator_user.company_id)

    task = TaskCreateModel(name=name, description=description, fields=fields, user_ids=user_ids, created_by=created_by,
                           updated_by=created_by, company_id=company_id)
    mongo_task.insert_one(task.to_dict())
    return TaskCreateModel(name=name, description=description, fields=fields, user_ids=user_ids,
                           created_by=creator_user.id, updated_by="", company_id=creator_user.company_id)


def get_task_by_id_as_create_model(_id: str) -> TaskBaseModel:
    task: Mapping[str, Any] | None | Any = mongo_task.find_one({"_id": ObjectId(_id)})
    if task is None:
        return TaskBaseModel(name="", description="", fields=[], created_by="", updated_by="", company_id="")
    return TaskCreateModel(name=task.get("name"), description=task.get("description"), fields=task.get("fields"),
                           user_ids=task.get("user_ids"), created_by=task.get("created_by"),
                           updated_by=task.get("updated_by"), company_id=task.get("company_id"))


def get_tasks_by_user_id(user_id: str) -> List[TaskGetModel]:
    db_tasks = list(mongo_task.find({"user_ids": user_id}))
    tasks = []

    for task in db_tasks:
        task['_id'] = str(task['_id'])
        del task['user_ids']
        tasks.append(task)

    return list(tasks)


def update_task(updater_user, _id: str, name: str, description: str, fields: List[TaskFieldModel],
                user_ids: List[str]) -> TaskUpdateModel:
    document_to_update = {"_id": ObjectId(_id)}

    found = mongo_task.find_one(document_to_update)

    if found is None:
        raise Exception("No document found with given _id")

    found_model = TaskUpdateModel(_id=found.get("_id"), name=found.get("name"), description=found.get("description"),
                                  fields=found.get("fields"), user_ids=found.get("user_ids"),
                                  company_id=found.get("company_id"), updated_by=found.get("updated_by"), created_by="")

    if str(found_model.company_id) != str(updater_user.company_id) or not updater_user.is_manager:
        raise Exception("User is not authorized to update")

    task = TaskUpdateModel(_id=_id, name=name, description=description, fields=fields,
                           user_ids=[str(a) for a in user_ids], company_id=found_model.company_id,
                           updated_by=found_model.updated_by, created_by=found_model.created_by)

    to_update = {}

    print(found_model.to_dict())
    for i in found_model.get_attributes():
        if getattr(task, i) != getattr(found_model, i) and i != "_id" and getattr(task, i) is not None:
            to_update[i] = getattr(task, i)

    new_values = {"$set": to_update}

    mongo_task.update_one(document_to_update, new_values)

    return task


def delete_task(user, _id: str) -> TaskUpdateModel:
    document_to_update = {"_id": ObjectId(_id)}

    found = mongo_task.find_one(document_to_update)

    if found is None:
        raise Exception("No document found with given _id")

    found_model = TaskUpdateModel(_id=found.get("_id"), name=found.get("name"), description=found.get("description"),
                                  fields=found.get("fields"), user_ids=found.get("user_ids"),
                                  company_id=found.get("company_id"), updated_by=found.get("updated_by"), created_by="")

    if str(found_model.company_id) != str(user.company_id) or not user.is_manager:
        raise Exception("User is not authorized to update")

    mongo_task.delete_one(document_to_update)

    return found_model


def create_or_update_field(user_id: str, task_id: str, fields: List[TaskFieldModel],
                           created_at: str = str(datetime.datetime.now()),
                           updated_at: str = str(datetime.datetime.now())):
    found_field = mongo_field.find_one({"task_id": ObjectId(task_id), "user_id": user_id})
    if found_field is None:
        print("Create")
        return create_field(user_id, task_id, fields)
    else:
        field = FieldUpdateModel(_id=found_field.get("_id"), task_id=found_field.get("task_id"),
                                 user_id=found_field.get("user_id"), created_at=found_field.get("created_at"),
                                 updated_at=found_field.get("updated_at"), fields=found_field.get("fields"))

        return update_field(old_model=field, user_id=user_id, task_id=task_id, fields=fields)


def create_field(user_id: str, task_id: str, fields: List[TaskFieldModel]):
    field = FieldCreateModel(task_id=task_id, user_id=user_id, fields=fields)
    mongo_field.insert_one(field.to_dict())
    return field


def update_field(old_model: FieldUpdateModel, user_id: str, task_id: str, fields: List[TaskFieldModel]):
    document_to_update = {"_id": ObjectId(old_model._id)}

    field = FieldUpdateModel(task_id=task_id, user_id=user_id, fields=fields, created_at=old_model.created_at)

    if field.task_id != old_model.task_id and field.user_id != old_model.user_id:
        raise Exception("User is not authorized to update")

    to_update = {}

    print(old_model.to_dict())
    for i in old_model.get_attributes():
        if getattr(field, i) != getattr(old_model, i) and i != "_id" and getattr(field, i) is not None:
            to_update[i] = getattr(field, i)

    new_values = {"$set": to_update}

    mongo_field.update_one(document_to_update, new_values)

    return field


def get_fields_by_user_id(user_id: str) -> List[FieldGetModel]:
    found_fields = mongo_field.find({"user_id": user_id})

    fields = [FieldGetModel(_id=field.get("_id"), task_id=field.get("task_id"),
                            user_id=field.get("user_id"), created_at=field.get("created_at"),
                            updated_at=field.get("updated_at"),
                            fields=[TaskFieldModel(i.name, i.type) for i in field.get('fields')]) for field in
              found_fields]

    return fields


def get_fields_by_user_id_task_id_raw(user_id: str, task_id: str) -> List[FieldGetModel]:
    found_fields = mongo_field.find({"user_id": user_id, "task_id": task_id})
    return found_fields


def get_fields_by_user_id_task_id(user_id: str, task_id: str) -> List[FieldGetModel]:
    found_fields = mongo_field.find({"user_id": user_id, "task_id": task_id})

    fields = [FieldGetModel(_id=field.get("_id"), task_id=field.get("task_id"),
                            user_id=field.get("user_id"), created_at=field.get("created_at"),
                            updated_at=field.get("updated_at"),
                            fields=[TaskFieldModel(i.name, i.type) for i in field.get('fields')]) for field in
              found_fields]

    return fields


def get_fields_by_user_id_raw(user_id: str) -> List[FieldGetModel]:
    found_fields = mongo_field.find({"user_id": user_id})
    return found_fields


def get_field_by_task_id(task_id: str, user_id) -> List[TaskUpdateModel]:
    field = mongo_field.find_one({"task_id": ObjectId(task_id), "user_id": user_id})
    return field


def delete_field(user_id: str, task_id: str):
    document_to_delete = {"task_id": task_id, "user_id": user_id}

    found_field = mongo_field.find_one(document_to_delete)
    if found_field is None:
        raise Exception("No document found with given _id")

    field = FieldUpdateModel(_id=found_field.get("_id"), task_id=task_id, user_id=user_id,
                             fields=[TaskFieldModel(i.name, i.type) for i in found_field.get('fields')],
                             created_at=found_field.get('created_at'), updated_at=found_field.get('updated_at'))

    mongo_field.delete_one(document_to_delete)
    return field
