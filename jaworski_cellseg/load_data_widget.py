from magicgui import magicgui
import napari
from pathlib import Path
from bioio import BioImage
import tifffile
import numpy as np


def decode_resolution(res):
    if res and isinstance(res.value, tuple):
        return res.value[0] / res.value[1]
    return res.value or 1.0


# Read tiff files
def handle_tiff(napari_viewer, file_path: Path, physical_sizes: dict):
    """Handle loading and processing of TIFF files."""
    bio_data = tifffile.imread(file_path)
    transformed_data = np.moveaxis(bio_data, 1, 0)  # Adjust axis
    napari_viewer.add_image(
        transformed_data,
        channel_axis=0,
        name=[f"Channel {i}" for i in range(transformed_data.shape[0])],
    )

    # Extract physical sizes
    with tifffile.TiffFile(file_path) as tiff:
        page = tiff.pages[0]
        x_resolution = page.tags.get("XResolution", None)
        y_resolution = page.tags.get("YResolution", None)
        # get imageJ metadata if exist, otherwise the or operator will return the empty dict
        imagej_metadata = tiff.imagej_metadata or {}
        z_physical_size = imagej_metadata.get("spacing", 1.0)
        unit_name = imagej_metadata.get("unit", None)

        x_res = decode_resolution(x_resolution)
        y_res = decode_resolution(y_resolution)

        physical_sizes.update(
            {
                "x": x_res,
                "y": y_res,
                "z": z_physical_size,
                "unit": unit_name,
            }
        )


# Read bio formart
def handle_bioformats(napari_viewer, file_path: Path, physical_sizes: dict):
    """Handle loading and processing of BioImage-compatible files"""
    image = BioImage(file_path)
    bio_data = image.get_image_data("CZYX")
    napari_viewer.add_image(
        bio_data,
        channel_axis=0,
        name=[f"Channel {i}" for i in range(bio_data.shape[0])],
    )

    # Extract physical sizes
    metadata = image.metadata.images[0]
    physical_sizes.update(
        {
            key: getattr(metadata.pixels, f"physical_size_{key}", 1.0)
            for key in ["x", "y", "z"]
        }
        | {"unit": getattr(metadata.pixels, "physical_size_x_unit", None)}
    )


def jwslab_load_bio_data(
    napari_viewer: napari.Viewer, file_path: Path, physical_sizes: dict
):
    file_extension_handlers = {
        ".tiff": handle_tiff,
        ".tif": handle_tiff,
        ".oir": handle_bioformats,
        ".nd2": handle_bioformats,
    }

    file_extension = file_path.suffix.lower()

    # Find and execute the appropriate handler
    handler = file_extension_handlers.get(file_extension, None)
    if handler is None:
        raise ValueError(f"Unsupported file format: {file_extension}")

    handler(napari_viewer, file_path, physical_sizes)


def create_load_data_widget(viewer: napari.Viewer, physical_sizes: dict):
    @magicgui(
        call_button="Open BioImage ...",
        auto_call=False,
        file_path={"label": "Choose a file", "mode": "r"},
    )
    def select_bio_data_widget(file_path: Path = None):
        jwslab_load_bio_data(viewer, file_path, physical_sizes)

    return select_bio_data_widget
