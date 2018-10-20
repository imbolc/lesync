from functools import wraps

from trafaret import DataError
from trafaret.constructor import construct


def validate_json(validator):
    def decorator(f):
        @wraps(f)
        async def wrapper(request, *args, **kwargs):
            if validator:
                validate = construct(validator)
                try:
                    validate(request.json)
                except DataError as e:
                    return {'errors': e.as_dict()}, 400
            return await f(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_query(validator):
    def decorator(f):
        @wraps(f)
        async def wrapper(request, *args, **kwargs):
            if validator:
                validate = construct(validator)
                try:
                    validate(request.GET)
                except DataError as e:
                    return {'errors': e.as_dict()}, 400
            return await f(request, *args, **kwargs)
        return wrapper
    return decorator
