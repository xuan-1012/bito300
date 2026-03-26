"""Unit tests for ImageExporter class."""

import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil
from PIL import Image

from src.model_evaluation_viz.export.image_exporter import ImageExporter


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_figure():
    """Create a simple matplotlib figure for testing."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([1, 2, 3, 4], [1, 4, 9, 16])
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_title('Test Chart')
    yield fig
    plt.close(fig)


class TestImageExporter:
    """Test suite for ImageExporter class."""
    
    def test_init_creates_output_directory(self, temp_output_dir):
        """Test that __init__() creates output directory if not exists."""
        output_path = Path(temp_output_dir) / "new_dir"
        assert not output_path.exists()
        
        exporter = ImageExporter(output_dir=str(output_path))
        
        assert output_path.exists()
        assert output_path.is_dir()
        assert exporter.output_dir == output_path
    
    def test_export_png_creates_file(self, temp_output_dir, sample_figure):
        """Test PNG export creates file with correct DPI."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath = exporter.export(sample_figure, "test_chart.png", format='png', dpi=300)
        
        assert Path(filepath).exists()
        assert filepath.endswith('.png')
        assert Path(filepath).stat().st_size > 0
        
        # Verify DPI using PIL (allow small floating point tolerance)
        img = Image.open(filepath)
        dpi_value = img.info.get('dpi', (0, 0))[0]
        assert dpi_value >= 299.9  # Allow for floating point precision
    
    def test_export_jpeg_creates_file(self, temp_output_dir, sample_figure):
        """Test JPEG export creates file."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath = exporter.export(sample_figure, "test_chart.jpeg", format='jpeg', dpi=300)
        
        assert Path(filepath).exists()
        assert filepath.endswith('.jpeg')
        assert Path(filepath).stat().st_size > 0
    
    def test_export_svg_creates_file(self, temp_output_dir, sample_figure):
        """Test SVG export creates file."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath = exporter.export(sample_figure, "test_chart.svg", format='svg')
        
        assert Path(filepath).exists()
        assert filepath.endswith('.svg')
        assert Path(filepath).stat().st_size > 0
    
    def test_export_transparent_png(self, temp_output_dir, sample_figure):
        """Test transparent PNG option."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath = exporter.export(
            sample_figure, "test_transparent.png", 
            format='png', transparent=True, dpi=300
        )
        
        assert Path(filepath).exists()
        
        # Verify transparency using PIL
        img = Image.open(filepath)
        assert img.mode in ['RGBA', 'LA', 'PA']  # Has alpha channel
    
    def test_export_custom_dimensions(self, temp_output_dir, sample_figure):
        """Test custom width/height specifications."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        custom_width = 12.0
        custom_height = 8.0
        
        # Get original size
        original_width, original_height = sample_figure.get_size_inches()
        
        filepath = exporter.export(
            sample_figure, "test_custom_size.png",
            format='png', dpi=300,
            width=custom_width, height=custom_height
        )
        
        assert Path(filepath).exists()
        
        # Verify that figure size was changed
        new_width, new_height = sample_figure.get_size_inches()
        assert abs(new_width - custom_width) < 0.01
        assert abs(new_height - custom_height) < 0.01
        
        # Note: bbox_inches='tight' may adjust final image size,
        # so we verify the figure was resized, not the final image pixels
    
    def test_export_minimum_dpi_validation(self, temp_output_dir, sample_figure):
        """Test that export enforces minimum 300 DPI for raster formats."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        with pytest.raises(ValueError, match="DPI must be at least 300"):
            exporter.export(sample_figure, "test.png", format='png', dpi=150)
    
    def test_export_unsupported_format(self, temp_output_dir, sample_figure):
        """Test that unsupported format raises ValueError."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        with pytest.raises(ValueError, match="Unsupported format"):
            exporter.export(sample_figure, "test.bmp", format='bmp')
    
    def test_export_adds_extension_if_missing(self, temp_output_dir, sample_figure):
        """Test that export adds extension if not present in filename."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath = exporter.export(sample_figure, "test_chart", format='png', dpi=300)
        
        assert filepath.endswith('.png')
        assert Path(filepath).exists()
    
    def test_export_multiple_formats(self, temp_output_dir, sample_figure):
        """Test export_multiple_formats() saves in multiple formats."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepaths = exporter.export_multiple_formats(
            sample_figure, "test_multi", 
            formats=['png', 'svg', 'jpeg'],
            dpi=300
        )
        
        assert len(filepaths) == 3
        
        for filepath in filepaths:
            assert Path(filepath).exists()
            assert Path(filepath).stat().st_size > 0
        
        # Check each format
        extensions = [Path(fp).suffix for fp in filepaths]
        assert '.png' in extensions
        assert '.svg' in extensions
        assert '.jpeg' in extensions
    
    def test_export_multiple_formats_default(self, temp_output_dir, sample_figure):
        """Test export_multiple_formats() with default formats (png, svg)."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepaths = exporter.export_multiple_formats(sample_figure, "test_default")
        
        assert len(filepaths) == 2
        extensions = [Path(fp).suffix for fp in filepaths]
        assert '.png' in extensions
        assert '.svg' in extensions
    
    def test_generate_filename_with_timestamp(self, temp_output_dir):
        """Test filename generation includes chart type and timestamp."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filename = exporter.generate_filename('roc_curve', timestamp=True)
        
        assert 'roc_curve' in filename
        assert filename.endswith('.png')
        # Check timestamp format (YYYYMMDD_HHMMSS)
        assert len(filename.split('_')) >= 3  # chart_type_YYYYMMDD_HHMMSS.ext
    
    def test_generate_filename_without_timestamp(self, temp_output_dir):
        """Test filename generation without timestamp."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filename = exporter.generate_filename('confusion_matrix', timestamp=False)
        
        assert filename == 'confusion_matrix.png'
    
    def test_generate_filename_custom_extension(self, temp_output_dir):
        """Test filename generation with custom extension."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filename = exporter.generate_filename('lift_curve', timestamp=False, extension='svg')
        
        assert filename == 'lift_curve.svg'
    
    def test_generate_filename_sanitizes_chart_type(self, temp_output_dir):
        """Test that chart type is sanitized (spaces to underscores, lowercase)."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filename = exporter.generate_filename('ROC Curve', timestamp=False)
        
        assert filename == 'roc_curve.png'
    
    def test_all_files_saved_to_same_directory(self, temp_output_dir, sample_figure):
        """Test that all exported images are saved to the same output directory."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath1 = exporter.export(sample_figure, "chart1.png", dpi=300)
        filepath2 = exporter.export(sample_figure, "chart2.png", dpi=300)
        filepath3 = exporter.export(sample_figure, "chart3.svg")
        
        assert Path(filepath1).parent == Path(temp_output_dir)
        assert Path(filepath2).parent == Path(temp_output_dir)
        assert Path(filepath3).parent == Path(temp_output_dir)
    
    def test_export_jpg_format_alias(self, temp_output_dir, sample_figure):
        """Test that 'jpg' format is accepted and converted to 'jpeg'."""
        exporter = ImageExporter(output_dir=temp_output_dir)
        
        filepath = exporter.export(sample_figure, "test.jpg", format='jpg', dpi=300)
        
        assert Path(filepath).exists()
        assert filepath.endswith('.jpeg')
