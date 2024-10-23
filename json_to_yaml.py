import os
import logging
from utils.json_utils import load_json, split_property_string, fix_encoding_in_data
from utils.yaml_utils import convert_json_to_yaml
from utils.text_utils import wrap_text, clean_prose
from utils.argument_utils import parse_arguments
from utils.logging_utils import setup_logging


def main():
    # Setup logging
    setup_logging()

    # Parse command-line arguments
    args = parse_arguments()

    # Identify the source directory
    source_directory = os.path.dirname(args.input)
    logging.info(f"Source directory: {source_directory}")

    # Load JSON data
    json_data = load_json(args.input)

    # Fix any encoding issues in the JSON data
    json_data = fix_encoding_in_data(json_data)

    # Split properties as needed (example)
    json_data = split_property_string(
        json_data, 'description', split_keyword=',')
    json_data = split_property_string(json_data, 'notes', split_length=20)

    # Convert JSON to YAML and save to output file
    convert_json_to_yaml(json_data, args.output, handle_quoted_strings=True)


if __name__ == "__main__":
    main()
