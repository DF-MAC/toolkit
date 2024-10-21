import json
import datetime
import os
import sys
import logging
import argparse
import textwrap
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from ftfy import fix_text  # Ensure ftfy is installed


def setup_logging():
    """
    Configures the logging settings.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(message)s')


def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(
        script_dir, '../sample_data/NIST_SP-800-53_rev5_catalog.json')
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    output_file_path = os.path.join(
        script_dir, '../output/cspm_simplified_catalog.yml')
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Convert NIST JSON catalog to CSPM YAML with wrapped text.")
    parser.add_argument(
        '-i', '--input',
        type=str,
        default=input_file_path,
        help='Path to the input NIST JSON catalog file.'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=output_file_path,
        help='Path to the output YAML file.'
    )
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=80,
        help='Maximum number of characters per line in the YAML output.'
    )
    return parser.parse_args()


def fix_encoding(text):
    """
    Fixes common encoding issues in the text using ftfy.

    Args:
        text (str): The string that may contain misencoded characters.

    Returns:
        str: The string with corrected encoding.
    """
    return fix_text(text)


def wrap_text(text, width):
    """
    Wraps the text to ensure no line exceeds the specified width.

    Args:
        text (str): The prose text to wrap.
        width (int): Maximum number of characters per line.

    Returns:
        str: The wrapped text.
    """
    # Split the text into paragraphs based on double newlines
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []

    for paragraph in paragraphs:
        # Replace existing single newlines with spaces to treat as a single paragraph
        paragraph = paragraph.replace('\n', ' ').strip()
        wrapped = textwrap.fill(paragraph, width=width)
        wrapped_paragraphs.append(wrapped)

    # Join paragraphs with double newlines to maintain paragraph separation
    return '\n\n'.join(wrapped_paragraphs)


def clean_prose(text, max_width):
    """
    Cleans up the prose text by fixing encoding issues and wrapping text.

    Args:
        text (str): The prose text to clean.
        max_width (int): Maximum number of characters per line.

    Returns:
        str: The cleaned and wrapped prose text.
    """
    # Fix encoding issues
    text = fix_encoding(text)
    # Replace escaped newline and tab characters with actual ones
    text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
    # Wrap text to the specified width
    text = wrap_text(text, max_width)
    # Strip leading and trailing whitespace
    return text.strip()


def nist_to_cspm_yaml(nist_json, max_width):
    """
    Transforms a NIST 800-53 Rev 5 JSON catalog into a simplified YAML format for CSPM policy writing.

    Args:
        nist_json (str): The JSON data representing the NIST catalog.
        max_width (int): Maximum number of characters per line.

    Returns:
        dict: The structured data ready to be dumped to YAML.
    """
    try:
        data = json.loads(nist_json)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        sys.exit(1)

    catalog = data.get("catalog", {})

    oscal_data = {
        "catalog": {
            "uuid": catalog.get("uuid", "unknown-uuid"),
            "metadata": {
                "title": catalog.get("metadata", {}).get("title", "Unknown Title"),
                "last-modified": catalog.get("metadata", {}).get(
                    "last-modified", datetime.datetime.now().isoformat()
                ),
            },
            "groups": []
        }
    }

    # Iterate over groups in the catalog
    for group in catalog.get("groups", []):
        group_data = {
            "id": group.get("id", "unknown-group-id"),
            "title": group.get("title", "Unknown Group Title"),
            "controls": []
        }

        # Iterate over controls in each group
        for control in group.get("controls", []):
            control_data = {
                "id": control.get("id", "unknown-control-id"),
                "title": control.get("title", "Unknown Control Title"),
                "parts": []
            }

            # Extract relevant parts (statement, guidance, etc.) from control
            if "parts" in control:
                prose_list = []
                for part in control["parts"]:
                    if "prose" in part:
                        prose_text = part.get('prose', '')
                        cleaned_text = clean_prose(prose_text, max_width)
                        # Use LiteralScalarString for multi-line strings
                        prose_list.append(LiteralScalarString(cleaned_text))
                if prose_list:
                    control_data["parts"] = prose_list

            group_data["controls"].append(control_data)

        oscal_data["catalog"]["groups"].append(group_data)

    return oscal_data


def main():
    # Setup logging
    setup_logging()

    # Parse command-line arguments
    args = parse_arguments()

    input_file_path = args.input
    output_file_path = args.output
    max_width = args.width

    # Check if input file exists
    if not os.path.exists(input_file_path):
        logging.error(f"Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    # Load the NIST JSON data
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            nist_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"File '{input_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON file: {e}")
        sys.exit(1)

    # Convert to a simplified YAML for CSPM policy writing
    try:
        oscal_data = nist_to_cspm_yaml(json.dumps(nist_data), max_width)
    except Exception as e:
        logging.error(f"Failed to convert JSON to YAML: {e}")
        sys.exit(1)

    # Initialize ruamel.yaml YAML object
    yaml = YAML()
    yaml.explicit_start = True  # Adds '---' at the beginning
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096  # Prevent line wrapping by ruamel.yaml

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Save the YAML output to a file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(oscal_data, yaml_file)
    except Exception as e:
        logging.error(f"Failed to write YAML to file: {e}")
        sys.exit(1)

    logging.info(f"Simplified CSPM YAML file has been saved to '{
                 output_file_path}'")


if __name__ == "__main__":
    main()
