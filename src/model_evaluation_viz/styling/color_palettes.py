"""Color palettes for chart styling.

This module provides colorblind-accessible color palettes for use in charts.
The default palette is designed to be distinguishable for people with various
types of color vision deficiency.
"""

from typing import List


# Colorblind-accessible palette based on Wong (2011) and Okabe & Ito (2008)
# These colors are designed to be distinguishable for people with:
# - Protanopia (red-blind)
# - Deuteranopia (green-blind)
# - Tritanopia (blue-blind)
DEFAULT_PALETTE: List[str] = [
    '#0173B2',  # Blue
    '#DE8F05',  # Orange
    '#029E73',  # Green
    '#CC78BC',  # Pink/Purple
    '#CA9161',  # Tan/Brown
    '#949494',  # Gray
    '#ECE133',  # Yellow
    '#56B4E9',  # Sky Blue
    '#F0E442',  # Light Yellow
    '#D55E00',  # Vermillion/Red-Orange
]
