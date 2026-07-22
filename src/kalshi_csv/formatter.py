def color_green(text, no_color=False):
    """Wraps text in ANSI green."""
    if no_color:
        return text
    return f"\033[1;32m{text}\033[0m"


def color_red(text, no_color=False):
    """Wraps text in ANSI red."""
    if no_color:
        return text
    return f"\033[1;31m{text}\033[0m"


def color_yellow(text, no_color=False):
    """Wraps text in ANSI yellow."""
    if no_color:
        return text
    return f"\033[1;33m{text}\033[0m"


def color_cyan(text, no_color=False):
    """Wraps text in ANSI cyan."""
    if no_color:
        return text
    return f"\033[1;36m{text}\033[0m"


def color_white(text, no_color=False):
    """Wraps text in ANSI white."""
    if no_color:
        return text
    return f"\033[1;37m{text}\033[0m"


def format_currency_color(value, no_color=False):
    """Returns a signed, colorized string based on profit or loss status."""
    val_str = f"${value:+.2f}"
    return color_green(val_str, no_color) if value >= 0 else color_red(val_str, no_color)


def format_currency_color_padded(value, width, no_color=False):
    """Returns a signed, colorized string padded to specified width before coloring."""
    val_str = f"${value:+.2f}"
    padded_str = f"{val_str:<{width}}"
    return color_green(padded_str, no_color) if value >= 0 else color_red(padded_str, no_color)


def truncate_ticker(ticker, max_len=32):
    """Truncates ticker to max_len, using ellipsis if longer than 29 chars."""
    if len(ticker) > 29:
        return ticker[:29] + "..."
    return ticker


UNICODE_BOX = {
    "top_left": "┌",
    "top_right": "┐",
    "bottom_left": "└",
    "bottom_right": "┘",
    "horizontal": "─",
    "vertical": "│",
    "top_tee": "┬",
    "bottom_tee": "┴",
    "left_tee": "├",
    "right_tee": "┤",
    "cross": "┼",
}

ASCII_BOX = {
    "top_left": "+",
    "top_right": "+",
    "bottom_left": "+",
    "bottom_right": "+",
    "horizontal": "-",
    "vertical": "|",
    "top_tee": "+",
    "bottom_tee": "+",
    "left_tee": "+",
    "right_tee": "+",
    "cross": "+",
}


def get_box_chars(ascii_mode=False):
    """Returns the appropriate box-drawing characters."""
    return ASCII_BOX if ascii_mode else UNICODE_BOX


def format_table_header(headers, widths, ascii_mode=False):
    """Formats a table header row with box-drawing characters."""
    box = get_box_chars(ascii_mode)
    cells = [f" {h:<{w}} " for h, w in zip(headers, widths)]
    return box["vertical"] + box["vertical"].join(cells) + box["vertical"]


def format_table_separator(widths, ascii_mode=False, position="middle"):
    """Formats a table separator line with box-drawing characters."""
    box = get_box_chars(ascii_mode)
    segments = [box["horizontal"] * (w + 2) for w in widths]
    
    if position == "top":
        return box["top_left"] + box["top_tee"].join(segments) + box["top_right"]
    elif position == "bottom":
        return box["bottom_left"] + box["bottom_tee"].join(segments) + box["bottom_right"]
    else:
        return box["left_tee"] + box["cross"].join(segments) + box["right_tee"]


def format_table_row(values, widths, ascii_mode=False):
    """Formats a table data row with box-drawing characters."""
    box = get_box_chars(ascii_mode)
    cells = [f" {str(v):<{w}} " for v, w in zip(values, widths)]
    return box["vertical"] + box["vertical"].join(cells) + box["vertical"]
