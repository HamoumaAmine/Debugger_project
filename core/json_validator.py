# core/json_validator.py
from jsonschema import validate, ValidationError

SCHEMA = {
    "type": "object",
    "required": ["error_summary", "modifications"],
    "additionalProperties": False,
    "properties": {
        "error_summary": {"type": "string"},
        "modifications": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["line", "remove", "add"],
                "additionalProperties": False,
                "properties": {
                    "line": {"type": "integer", "minimum": 1},
                    "remove": {"type": "string"},
                    "add": {"type": "string"}
                }
            }
        }
    }
}

def validate_correction_json(obj: dict):
    """
    Retourne (True, None) si valide, sinon (False, erreur_details).
    """
    try:
        validate(instance=obj, schema=SCHEMA)
        return True, None
    except ValidationError as e:
        return False, str(e)
