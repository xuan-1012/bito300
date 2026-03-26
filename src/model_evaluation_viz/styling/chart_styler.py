"""Chart styling utilities for consistent visual appearance.

This module provides the ChartStyler class which applies consistent styling
to matplotlib figures, including colors, fonts, grid lines, and other visual
elements.
"""

from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from ..core.models import ChartStyle
from .color_palettes import DEFAULT_PALETTE


class ChartStyler:
    """Applies consistent styling to matplotlib figures.
    
    The ChartStyler manages visual appearance of charts including colors,
    fonts, grid lines, and other styling elements. It ensures all charts
    have a consistent, professional appearance suitable for presentations
    and publications.
    
    Attributes:
        style: ChartStyle configuration object containing styling parameters.
    
    Example:
        >>> from model_evaluation_viz.core.models import ChartStyle
        >>> from model_evaluation_viz.styling.chart_styler import ChartStyler
        >>> 
        >>> # Use default styling
        >>> styler = ChartStyler()
        >>> 
        >>> # Use custom styling
        >>> custom_style = ChartStyle(
        ...     font_size=14,
        ...     line_width=2.5,
        ...     grid=True
        ... )
        >>> styler = ChartStyler(custom_style)
        >>> 
        >>> # Apply styling to a matplotlib axes
        >>> fig, ax = plt.subplots()
        >>> styler.apply_base_style(ax)
        >>> styler.format_axis_labels(ax, 'X Label', 'Y Label', 'Chart Title')
    """
    
    def __init__(self, style: Optional[ChartStyle] = None):
        """Initialize the ChartStyler.
        
        Args:
            style: Optional ChartStyle configuration. If None, uses default
                   ChartStyle with colorblind-accessible palette.
        """
        if style is None:
            # Create default style with our colorblind-accessible palette
            self.style = ChartStyle(color_palette=DEFAULT_PALETTE.copy())
        else:
            self.style = style
            # If style was provided but has no custom palette, use DEFAULT_PALETTE
            if self.style.color_palette is None or self.style.color_palette == [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]:
                self.style.color_palette = DEFAULT_PALETTE.copy()
    
    def apply_base_style(self, ax: Axes) -> None:
        """Apply base styling to matplotlib axes.
        
        This method configures grid lines, font sizes, line widths, and
        anti-aliasing for the provided axes. It ensures minimum font size
        of 10 points and enables anti-aliasing for smooth rendering.
        
        Args:
            ax: Matplotlib axes object to style.
        
        Example:
            >>> fig, ax = plt.subplots()
            >>> styler = ChartStyler()
            >>> styler.apply_base_style(ax)
        """
        # Enable grid if configured
        if self.style.grid:
            ax.grid(
                True,
                alpha=self.style.grid_alpha,
                linestyle=self.style.grid_style,
                linewidth=0.5
            )
        else:
            ax.grid(False)
        
        # Set font sizes (ensure minimum of 10 points)
        font_size = max(10, self.style.font_size)
        title_font_size = max(10, self.style.title_font_size)
        
        # Apply font sizes to tick labels
        ax.tick_params(
            axis='both',
            which='major',
            labelsize=font_size
        )
        
        # Set background and text colors
        ax.set_facecolor(self.style.background_color)
        
        # Enable anti-aliasing for smooth rendering
        # This is done at the figure level when saving
        if ax.figure:
            ax.figure.set_facecolor(self.style.background_color)
    
    def get_color(self, index: int) -> str:
        """Get color from palette by index.
        
        Retrieves a color from the configured color palette using modulo
        arithmetic to cycle through colors if index exceeds palette length.
        
        Args:
            index: Zero-based index of the color to retrieve.
        
        Returns:
            Hex color string (e.g., '#0173B2').
        
        Example:
            >>> styler = ChartStyler()
            >>> color1 = styler.get_color(0)  # First color
            >>> color2 = styler.get_color(1)  # Second color
            >>> color11 = styler.get_color(10)  # Wraps around to first color
        """
        return self.style.color_palette[index % len(self.style.color_palette)]
    
    def format_axis_labels(
        self,
        ax: Axes,
        xlabel: str,
        ylabel: str,
        title: str
    ) -> None:
        """Format axis labels and title with proper font sizes.
        
        Sets the x-axis label, y-axis label, and title with appropriate
        font sizes. Ensures minimum font size of 10 points for all text
        elements.
        
        Args:
            ax: Matplotlib axes object to format.
            xlabel: Label for the x-axis.
            ylabel: Label for the y-axis.
            title: Chart title.
        
        Example:
            >>> fig, ax = plt.subplots()
            >>> styler = ChartStyler()
            >>> styler.format_axis_labels(
            ...     ax,
            ...     'Training Set Size',
            ...     'Score',
            ...     'Learning Curve'
            ... )
        """
        # Ensure minimum font sizes of 10 points
        font_size = max(10, self.style.font_size)
        title_font_size = max(10, self.style.title_font_size)
        
        # Set axis labels
        ax.set_xlabel(
            xlabel,
            fontsize=font_size,
            fontfamily=self.style.font_family,
            color=self.style.text_color
        )
        ax.set_ylabel(
            ylabel,
            fontsize=font_size,
            fontfamily=self.style.font_family,
            color=self.style.text_color
        )
        
        # Set title
        ax.set_title(
            title,
            fontsize=title_font_size,
            fontfamily=self.style.font_family,
            color=self.style.text_color,
            pad=15  # Add padding between title and plot
        )
        
        # Update tick label colors
        ax.tick_params(
            axis='both',
            colors=self.style.text_color
        )
        
        # Update spine colors
        for spine in ax.spines.values():
            spine.set_edgecolor(self.style.text_color)
            spine.set_linewidth(0.8)
