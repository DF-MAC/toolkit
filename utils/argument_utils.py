import argparse


def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert JSON to YAML with additional processing.")
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to the input JSON file.'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Path to the output YAML file.'
    )
    parser.add_argument(
        '-w', '--width',
        type=int,
        help='Maximum number of characters per line in the YAML output.'
    )
    return parser.parse_args()
