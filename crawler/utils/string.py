def clean_and_merge(lst):
    """
    Cleans the input list by removing empty strings and strings containing only whitespace.
    Merges consecutive string elements into a single string without adding spaces.

    Args:
        lst (list): The input list containing strings and other data types.

    Returns:
        list: The cleaned and merged list.
    """
    result = []  # List to store the final result
    buffer = None  # Buffer to temporarily hold consecutive strings

    for item in lst:
        if isinstance(item, str):
            stripped = item.strip()  # Remove leading and trailing whitespace
            if stripped:
                if buffer is not None:
                    buffer += stripped  # type: ignore
                else:
                    buffer = stripped  # Start a new buffer
            # If the string is only whitespace, ignore it
        else:
            if buffer is not None:
                result.append(buffer)  # Add the buffered string to the result
                buffer = None  # Reset the buffer
            result.append(item)  # Add the non-string element to the result

    if buffer is not None:
        result.append(buffer)  # Add any remaining buffered string to the result

    return result
