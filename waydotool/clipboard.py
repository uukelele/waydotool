import pyperclip

def copy(text: str):
    """
    Copies text to the clipboard.
    Literally just the `pyperclip` implementation, but it's provided as part of this library for convenience and to help you reduce your import count.

    Args:
        text: The text you want to copy to the clipboard.
    """

    return pyperclip.copy(text)

def paste() -> str:
    """
    Returns the text copied to the clipboard.
    Literally just the `pyperclip` implementation, but it's provided as part of this library for convenience and to help you reduce your import count.

    Returns:
        The text currently copied to the clipboard.

    """

    return pyperclip.paste()