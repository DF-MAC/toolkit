import fitz  # PyMuPDF
import argparse
import os


def splice_pdf(input_pdf_path, output_pdf_path, start_page, end_page):
    """
    Splices pages from an input PDF and saves them to a new output PDF.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_pdf_path (str): The path where the output PDF file will be saved.
        start_page (int): The starting page number (1-indexed).
        end_page (int): The ending page number (1-indexed).
    """
    # Open the input PDF
    with fitz.open(input_pdf_path) as pdf_document:
        total_pages = pdf_document.page_count

        # Validate page numbers
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            raise ValueError(f"Invalid page range: {
                             start_page} - {end_page}. PDF has {total_pages} pages.")

        # Create a new PDF for output
        new_pdf_document = fitz.open()

        # Add the specified pages to the new PDF
        for page_num in range(start_page - 1, end_page):  # PyMuPDF uses 0-indexing
            page = pdf_document.load_page(page_num)
            new_pdf_document.insert_pdf(
                pdf_document, from_page=page_num, to_page=page_num)

        # Write the output PDF
        new_pdf_document.save(output_pdf_path)

    print(f"PDF spliced successfully. Pages {start_page} to {
          end_page} saved to '{output_pdf_path}'.")


def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Splice pages from a PDF file.")
    parser.add_argument('-i', '--input', type=str,
                        required=True, help='Path to the input PDF file.')
    parser.add_argument('-o', '--output', type=str,
                        required=True, help='Path to the output PDF file.')
    parser.add_argument('-s', '--start', type=int, required=True,
                        help='Starting page number (1-indexed).')
    parser.add_argument('-e', '--end', type=int, required=True,
                        help='Ending page number (1-indexed).')
    return parser.parse_args()


def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Check if input file exists
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file '{args.input}' does not exist.")

    # Splice the PDF
    splice_pdf(args.input, args.output, args.start, args.end)


if __name__ == "__main__":
    main()
