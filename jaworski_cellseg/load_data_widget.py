from magicgui import magicgui
import napari
from pathlib import Path
from bioio import BioImage
import tifffile


def jwslab_load_bio_data(napari_viewer: napari.Viewer, file_path: Path):
    try:
        file_extension = file_path.suffix.lower()
        if file_extension == ".tiff" or file_extension == ".tif":
            # Load TIFF file using tifffile
            bio_data = tifffile.imread(file_path)
            napari_viewer.add_image(bio_data, name="TIFF Image")
            return bio_data, {"format": "TIFF"}

        elif file_extension in [".oir", ".nd2"]:
            image = BioImage(file_path)
            bio_data = image.get_image_data("CZYX")
            napari_viewer.add_image(
                bio_data,
                channel_axis=0,
                name=[f"Channel {i}" for i in range(bio_data.shape[0])],
            )
            return bio_data, image.metadata

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
        _, metadata = jwslab_load_bio_data(viewer, file_path)
        image_metadata = metadata.images[0]
        xyz: dict = {
            key: getattr(image_metadata.pixels, f"physical_size_{key}")
            for key in ["x", "y", "z"]
        }
        physical_sizes.update(xyz)

    return select_bio_data_widget
