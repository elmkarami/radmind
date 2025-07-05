import re
from typing import Any, Dict


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    # Handle special cases
    if name == "organizationId":
        return "organization_id"

    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)

    # Insert an underscore before any uppercase letter that follows a lowercase letter or number
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    # Handle special cases
    if name == "organization_id":
        return "organizationId"

    components = name.split("_")
    # First component stays lowercase, rest get capitalized
    return components[0] + "".join(word.capitalize() for word in components[1:])


def convert_dict_keys_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert dictionary keys from camelCase to snake_case."""
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        snake_key = camel_to_snake(key)
        # Convert ID fields from string to int
        if snake_key in [
            "study_id",
            "template_id",
            "user_id",
            "organization_id",
        ] and isinstance(value, str):
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass  # Keep original value if conversion fails
        result[snake_key] = value

    return result


def convert_dict_keys_to_camel_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert dictionary keys from snake_case to camelCase."""
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        camel_key = snake_to_camel(key)
        result[camel_key] = value

    return result
