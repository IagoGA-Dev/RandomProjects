def colors_match(color1, color2, tolerance=20):
    """Check if two colors match within a given tolerance."""
    return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))

def rgb_to_hex(rgb):
    """Convert an RGB tuple to a hex color code."""
    return '#%02x%02x%02x' % rgb
