from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, JWTExtendedException

def role_required(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role')

                if not user_role:
                    return jsonify({"message": "Token saknar rollinformation."}), 403

                if user_role not in required_roles:
                    return jsonify({"message": "Åtkomst nekad: Otillräckliga rättigheter."}), 403

                return fn(*args, **kwargs)

            except NoAuthorizationError:
                return jsonify({"message": "Ingen token tillhandahållen."}), 401
            except InvalidHeaderError:
                return jsonify({"message": "Ogiltig token-header."}), 401
            except JWTExtendedException as e:
                return jsonify({"message": f"JWT-fel: {str(e)}"}), 401
            except Exception as e:
                return jsonify({"message": "Ett oväntat fel inträffade.", "details": str(e)}), 500

        return wrapper
    return decorator
