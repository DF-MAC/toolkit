import sys
import logging
from ruamel.yaml import YAML


def convert_json_to_yaml(json_data, output_yaml_path, handle_quoted_strings=True):
    """
    Converts JSON data to YAML and writes it to an output YAML file.
    Optionally handle quoted and unquoted strings based on parameter.
    """
    yaml = YAML()
    yaml.default_flow_style = False  # Write in a human-readable block form
    yaml.explicit_start = True  # Adds '---' at the beginning
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096  # Prevent line wrapping

    if handle_quoted_strings:
        yaml.preserve_quotes = True

    try:
        with open(output_yaml_path, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(json_data, yaml_file)
        logging.info(f"YAML file created at: {output_yaml_path}")
    except Exception as e:
        logging.error(f"Failed to write YAML to file: {e}")
        sys.exit(1)
