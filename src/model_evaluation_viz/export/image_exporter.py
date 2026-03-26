"""Image export functionality for matplotlib figures."""

from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
import matplotlib.pyplot as plt


class ImageExporter:
    """Exports matplotlib figures to image files.
    
    Supports multiple image formats (PNG, JPEG, SVG) with customizable
    resolution, transparency, and dimensions. All exports maintain a
    minimum of 300 DPI for publication-quality output.
    
    Attributes:
        output_dir: Path to the output directory for exported images.
    
    Example:
        >>> exporter = ImageExporter(output_dir="./charts")
        >>> fig, ax = plt.subplots()
        >>> ax.plot([1, 2, 3], [1, 4, 9])
        >>> filepath = exporter.export(fig, "my_chart.png")
        >>> print(f"Chart saved to: {filepath}")
    """
    
    def __init__(self, output_dir: str = "./output"):
        """Initialize ImageExporter with output directory.
        
        Creates the output directory if it doesn't exist.
        
        Args:
            output_dir: Path to directory where images will be saved.
                       Defaults to "./output".
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(
        self,
        fig: plt.Figure,
        filename: str,
        format: str = 'png',
        dpi: int = 300,
        transparent: bool = False,
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> str:
        """Export figure to file and return file path.
        
        Saves the matplotlib figure to the specified format with the given
        parameters. Ensures minimum 300 DPI for raster formats.
        
        Args:
            fig: Matplotlib figure to export.
            filename: Name of the output file (with or without extension).
            format: Image format - 'png', 'jpeg', or 'svg'. Defaults to 'png'.
            dpi: Dots per inch for raster formats. Minimum 300. Defaults to 300.
            transparent: Whether to use transparent background (PNG only).
                        Defaults to False.
            width: Custom width in inches. If None, uses figure's current width.
            height: Custom height in inches. If None, uses figure's current height.
        
        Returns:
            str: Full path to the saved file.
        
        Raises:
            ValueError: If format is not supported or DPI is below 300.
        
        Example:
            >>> exporter = ImageExporter()
            >>> fig = plt.figure()
            >>> path = exporter.export(fig, "chart.png", dpi=300, transparent=True)
        """
        # Validate format
        format = format.lower()
        supported_formats = ['png', 'jpeg', 'jpg', 'svg']
        if format not in supported_formats:
            raise ValueError(
                f"Unsupported format '{format}'. "
                f"Supported formats: {', '.join(supported_formats)}"
            )
        
        # Ensure minimum DPI for raster formats
        if format in ['png', 'jpeg', 'jpg'] and dpi < 300:
            raise ValueError(
                f"DPI must be at least 300 for raster formats. Got: {dpi}"
            )
        
        # Normalize jpeg format
        if format == 'jpg':
            format = 'jpeg'
        
        # Add extension if not present
        if not filename.endswith(f'.{format}'):
            filename = f"{filename}.{format}"
        
        # Build full file path
        filepath = self.output_dir / filename
        
        # Apply custom dimensions if specified
        if width is not None or height is not None:
            current_width, current_height = fig.get_size_inches()
            new_width = width if width is not None else current_width
            new_height = height if height is not None else current_height
            fig.set_size_inches(new_width, new_height)
        
        # Prepare save parameters
        save_kwargs = {
            'dpi': dpi,
            'bbox_inches': 'tight',
            'format': format
        }
        
        # Add transparency for PNG
        if format == 'png' and transparent:
            save_kwargs['transparent'] = True
        
        # JPEG doesn't support transparency
        if format == 'jpeg' and transparent:
            # Silently ignore transparency for JPEG
            pass
        
        # Save the figure
        fig.savefig(filepath, **save_kwargs)
        
        return str(filepath)
    
    def export_multiple_formats(
        self,
        fig: plt.Figure,
        base_filename: str,
        formats: List[str] = None,
        dpi: int = 300,
        transparent: bool = False,
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> List[str]:
        """Export figure to multiple formats.
        
        Convenience method to save the same figure in multiple formats
        with consistent settings.
        
        Args:
            fig: Matplotlib figure to export.
            base_filename: Base name for output files (without extension).
            formats: List of formats to export. Defaults to ['png', 'svg'].
            dpi: Dots per inch for raster formats. Defaults to 300.
            transparent: Whether to use transparent background (PNG only).
                        Defaults to False.
            width: Custom width in inches. If None, uses figure's current width.
            height: Custom height in inches. If None, uses figure's current height.
        
        Returns:
            List[str]: List of full paths to all saved files.
        
        Example:
            >>> exporter = ImageExporter()
            >>> fig = plt.figure()
            >>> paths = exporter.export_multiple_formats(
            ...     fig, "chart", formats=['png', 'svg', 'jpeg']
            ... )
            >>> print(f"Saved {len(paths)} files")
        """
        if formats is None:
            formats = ['png', 'svg']
        
        # Remove extension from base_filename if present
        base_filename = Path(base_filename).stem
        
        filepaths = []
        for fmt in formats:
            try:
                filepath = self.export(
                    fig=fig,
                    filename=base_filename,
                    format=fmt,
                    dpi=dpi,
                    transparent=transparent,
                    width=width,
                    height=height
                )
                filepaths.append(filepath)
            except ValueError as e:
                # Log error but continue with other formats
                print(f"Warning: Failed to export {fmt} format: {e}")
        
        return filepaths
    
    def generate_filename(
        self,
        chart_type: str,
        timestamp: bool = True,
        extension: str = 'png'
    ) -> str:
        """Generate descriptive filename for chart.
        
        Creates a filename that includes the chart type and optionally
        a timestamp for uniqueness.
        
        Args:
            chart_type: Type of chart (e.g., 'roc_curve', 'confusion_matrix').
            timestamp: Whether to include timestamp in filename. Defaults to True.
            extension: File extension. Defaults to 'png'.
        
        Returns:
            str: Generated filename.
        
        Example:
            >>> exporter = ImageExporter()
            >>> filename = exporter.generate_filename('roc_curve')
            >>> print(filename)  # e.g., 'roc_curve_20240115_143022.png'
        """
        # Sanitize chart_type (replace spaces with underscores, lowercase)
        chart_type = chart_type.lower().replace(' ', '_').replace('-', '_')
        
        # Remove extension if present
        extension = extension.lstrip('.')
        
        if timestamp:
            # Generate timestamp in format: YYYYMMDD_HHMMSS
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{chart_type}_{ts}.{extension}"
        else:
            filename = f"{chart_type}.{extension}"
        
        return filename
