import os
import sys


def handle_file_path(input_file_path, output_file_path):
    """
    args:
    input_file_path: str: path to the input file
    output_file_path: str: path to the output file

    returns:
    updated_input_file_path: str: updated path to the input file based on location of the script file
    updated_output_file_path: str: updated path to the output file based on location of the script file
    """

    # Specify the input and output files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    updated_input_file_path = os.path.join(
        script_dir, input_file_path)
    if not os.path.exists(updated_input_file_path):
        print(
            f"Error: Input file '{updated_input_file_path}' does not exist.")
        sys.exit(1)
    updated_output_file_path = os.path.join(
        script_dir, output_file_path)

    return updated_input_file_path, updated_output_file_path
