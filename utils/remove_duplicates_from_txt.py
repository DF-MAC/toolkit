import os
import sys


def remove_duplicates(input_file, output_file):
    # Initialize an empty set to track unique items and a list for duplicates
    seen = set()
    duplicates = []
    unique_items = []

    # Open the input file and iterate through each line
    with open(input_file, 'r') as infile:
        for line in infile:
            item = line.strip()  # Strip any leading/trailing whitespace

            if item in seen:
                duplicates.append(item)  # Track duplicates
            else:
                seen.add(item)  # Add new unique item to the set
                unique_items.append(item)  # Add to the list of unique items

    # Write the unique items back to the output file
    with open(output_file, 'w') as outfile:
        for item in unique_items:
            outfile.write(f"{item}\n")

    # Print the list of duplicate items in the console
    if duplicates:
        print("Duplicated items:")
        for duplicate in duplicates:
            print(duplicate)
    else:
        print("No duplicates found.")


if __name__ == "__main__":
    # Specify the input and output files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(
        script_dir, '../lists/nist_assignments.txt')
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    output_file = 'unique_list_output.txt'  # Output .txt file for unique items

    # Call the function to remove duplicates and handle the output
    remove_duplicates(input_file, output_file)
