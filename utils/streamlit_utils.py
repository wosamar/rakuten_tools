from typing import List


def parse_manage_numbers_input(input_string: str) -> List[str]:
    """
    Parses a string of item manage numbers from a text area.
    The input can be comma-separated or newline-separated.

    Args:
        input_string: The raw string from the text area.

    Returns:
        A list of cleaned, stripped manage numbers.
    """
    if not input_string:
        return []
    # Replace newlines with commas to handle both cases
    cleaned_string = input_string.replace('\n', ',')
    # Split by comma and strip whitespace from each entry
    # Use a set to remove duplicates and then convert back to a list
    return list(set([mn.strip() for mn in cleaned_string.split(',') if mn.strip()]))

