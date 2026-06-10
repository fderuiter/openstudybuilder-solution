"""Decorators that can be used on a service"""

import functools

# pylint: disable=unused-import
from clinical_mdr_api.services.studies.study import validate_if_study_is_not_locked

def architectural_logic(feature: str, description: str):
    def decorator(func):
        if not hasattr(func, "__architectural_logic__"):
            func.__architectural_logic__ = []
        func.__architectural_logic__.append({"feature": feature, "description": description})
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
