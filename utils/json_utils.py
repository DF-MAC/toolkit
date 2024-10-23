import sys
import os
import json
import logging
import ftfy


def load_json(json_file_path):
    """
    Loads JSON from the provided file path.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data
    except FileNotFoundError:
        logging.error(f"File '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON file: {e}")
        sys.exit(1)


def split_property_string(data, property_name, split_keyword=None, split_length=None):
    """
    Utility to split a string in JSON properties based on a keyword or length.
    - If `split_keyword` is provided, split on that keyword.
    - If `split_length` is provided, split on every `split_length` characters.
    """
    if property_name not in data:
        return data  # Property does not exist, return data unchanged

    value = data[property_name]
    if not isinstance(value, str):
        return data  # If value isn't a string, there's nothing to split

    if split_keyword:
        data[property_name] = value.split(split_keyword)
    elif split_length:
        data[property_name] = [value[i:i+split_length]
                               for i in range(0, len(value), split_length)]

    return data


def split_rql_string(data):
    """
    Utility to split a string in JSON properties based on RQL syntax.
    Splits on the following keywords: and, or, like, eq, ne, gt, ge, lt, le, in, nin, not, nor
    Accommodates for spaces before and after the keyword, and is not case-sensitive.
    """
    rql_keywords = ['and', 'or', 'like', 'eq', 'ne',
                    'gt', 'ge', 'lt', 'le', 'in', 'nin', 'not', 'nor', 'gte', 'lte']
    for key in data:
        if isinstance(data[key], str):
            value = data[key]
            for keyword in rql_keywords:
                if value.lower().find(f' {keyword} ') != -1:
                    data[key] = value.split(f' {keyword} ')
    return data


def fix_encoding_in_data(data):
    """
    Uses ftfy to fix encoding issues in the data recursively.
    """
    if isinstance(data, dict):
        return {key: fix_encoding_in_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [fix_encoding_in_data(element) for element in data]
    elif isinstance(data, str):
        return ftfy.fix_text(data)
    else:
        return data
