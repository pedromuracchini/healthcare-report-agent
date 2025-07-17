"""
Loads and exposes the cleaned SRAG data dictionary for dynamic use in query generation.
"""
import json

from agent.config import DATA_DICTIONARY_PATH

def load_data_dictionary():
    """
    Load the data dictionary JSON from the configured path.
    Returns:
        list: List of field definitions (dicts).
    """
    with open(DATA_DICTIONARY_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_field_options(field_name: str):
    """
    Get value options for a field as a dict {value: description}, if available.
    Args:
        field_name (str): The name of the field to look up.
    Returns:
        dict or None: Mapping of value to description, or None if not available.
    """
    data = load_data_dictionary()
    for field in data:
        if field["field_name"] == field_name:
            opts = field.get("value_options", "")
            if not opts or opts == "N/A":
                return None
            result = {}
            for part in opts.split(","):
                if "-" in part:
                    k, v = part.split("-", 1)
                    result[k.strip()] = v.strip()
                else:
                    result[part.strip()] = part.strip()
            return result
    return None

def get_all_fields():
    """
    Get a list of all fields and their descriptions from the data dictionary.
    Returns:
        list: List of field definitions (dicts).
    """
    data = load_data_dictionary()
    return [{"field_name": f["field_name"], "description": f["full_description"]} for f in data]
