import textwrap
from ftfy import fix_text


def wrap_text(text, width):
    """
    Wraps the text to ensure no line exceeds the specified width.
    """
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []

    for paragraph in paragraphs:
        paragraph = paragraph.replace('\n', ' ').strip()
        wrapped = textwrap.fill(paragraph, width=width)
        wrapped_paragraphs.append(wrapped)

    return '\n\n'.join(wrapped_paragraphs)


def clean_prose(text, max_width):
    """
    Cleans up the prose text by fixing encoding issues and wrapping text.
    """
    text = fix_text(text)
    text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
    text = wrap_text(text, max_width)
    return text.strip()
