from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity


from functools import wraps

# from app.user.model import User


# def auth_required(*roles_required):
#     def requires_auth(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             verify_jwt_in_request()
#             claims = get_jwt()
#             # check role
#             if roles_required:
#                 if not (claims['role'] in roles_required):
#                     return jsonify({"message": "Unauthorized to perform action"}), 401
#             g.user = User.get_by_id(get_jwt_identity())
#             return f(*args, **kwargs)
#         return decorated
#     return requires_auth

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         verify_jwt_in_request()
#         g.user = User.get_by_id(get_jwt_identity())
#         return f(*args, **kwargs)
#     return decorated

# def platform_auth_required(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             auth = request.authorization
#             if not (auth and Platform.is_authorized(auth.username, auth.password)):
#                 return jsonify({"message": "Missing Authorization Header"}), 401
#             g.platform = Platform.get_by_username(auth.username)
#             return f(*args, **kwargs)
#         return decorated