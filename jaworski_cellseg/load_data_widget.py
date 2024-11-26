from magicgui import magicgui
import napari
from pathlib import Path
from bioio import BioImage
import tifffile
import numpy as np


def jwslab_load_bio_data(
    napari_viewer: napari.Viewer, file_path: Path, physical_sizes: dict
):
    try:
        file_extension = file_path.suffix.lower()
        if file_extension == ".tiff" or file_extension == ".tif":
            # Load TIFF file using tifffile
            bio_data = tifffile.imread(file_path)
            transformed_data = np.moveaxis(bio_data, 1, 0)
            napari_viewer.add_image(
                transformed_data,
                channel_axis=0,
                name=[f"Channel {i}" for i in range(bio_data.shape[0])],
            )
            ## get physical size of the data
            with tifffile.TiffFile(file_path) as tiff:
                page = tiff.pages[0]
                # Extract resolution-related tags
                x_resolution = page.tags.get("XResolution", None)
                y_resolution = page.tags.get("YResolution", None)

                unit_name = None
                z_physical_size = 1.0
                if tiff.imagej_metadata:
                    unit_name = tiff.imagej_metadata["unit"]
                    if "spacing" in tiff.imagej_metadata:
                        z_physical_size = tiff.imagej_metadata["spacing"]

                print(x_resolution)
                print(y_resolution)
                # Decode values
                if x_resolution and y_resolution:
                    x_res = x_resolution.value
                    y_res = y_resolution.value

                    # physical size (numerator, denominator)
                    x_res_value = (
                        x_res[0] / x_res[1] if isinstance(x_res, tuple) else x_res
                    )
                    y_res_value = (
                        y_res[0] / y_res[1] if isinstance(y_res, tuple) else y_res
                    )
                    xyz: dict = {
                        "x": x_res_value,
                        "y": y_res_value,
                        "z": z_physical_size,
                        "unit": unit_name,
                    }
                    physical_sizes.update(xyz)
            print(physical_sizes)

        elif file_extension in [".oir", ".nd2"]:
            image = BioImage(file_path)
            bio_data = image.get_image_data("CZYX")
            napari_viewer.add_image(
                bio_data,
                channel_axis=0,
                name=[f"Channel {i}" for i in range(bio_data.shape[0])],
            )
            ## get physical size of the data
            metadata = image.metadata.images[0]
            xyz: dict = {
                key: getattr(metadata.pixels, f"physical_size_{key}")
                for key in ["x", "y", "z"]
            }

            # Assume the same unit is used on every axis
            xyz["unit"] = getattr(metadata.pixels, "physical_size_x_unit")
            physical_sizes.update(xyz)

        else:
            # Raise exception for unsupported formats
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        print(e)


def create_load_data_widget(viewer: napari.Viewer, physical_sizes: dict):
    @magicgui(
        call_button="Open BioImage ...",
        auto_call=False,
        file_path={"label": "Choose a file", "mode": "r"},
    )
    def select_bio_data_widget(file_path: Path = None):
        jwslab_load_bio_data(viewer, file_path, physical_sizes)

    return select_bio_data_widget
