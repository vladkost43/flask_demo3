from functools import wraps
from flask import Response
from flask_login import login_required, current_user

from flask_project.models import Events


def admin_required(foo):
    @login_required
    @wraps(foo)
    def wrapper(*args, **kwargs):
        if current_user.group_id != 3:
            return Response("Admin account required", status=403)
        return foo(*args, **kwargs)

    return wrapper


def owner_required(foo):
    @login_required
    @wraps(foo)
    def wrapper(*args, **kwargs):
        if current_user != Events.find_by_id(kwargs.get("event_id")).owner:
            return Response("Owner account required", status=403)
        return foo(*args, **kwargs)

    return wrapper


def admin_or_owner_required(foo):
    @login_required
    @wraps(foo)
    def wrapper(*args, **kwargs):
        if not current_user.group_id != 3 and current_user != Events.find_by_id(kwargs.get("event_id")).owner:
            return Response("Admin or owner account required", status=403)
        return foo(*args, **kwargs)
    return wrapper