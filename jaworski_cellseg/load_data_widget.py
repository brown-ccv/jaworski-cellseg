from magicgui import magicgui
import napari
from pathlib import Path
from bioio import BioImage


def jwslab_load_bio_data(napari_viewer, file_path):
    print("enter jwslab_pre_process_file")
    try:
        image = BioImage(file_path)
        bio_data = image.get_image_data("CZYX")
        napari_viewer.add_image(
            bio_data,
            channel_axis=0,
            name=[f"Channel {i}" for i in range(bio_data.shape[0])],
        )
        return bio_data, image.metadata
    except Exception as e:
        print(e)


def create_load_data_widget(viewer: napari.Viewer, physical_sizes: dict):
    @magicgui(
        call_button="Open BioImage",
        auto_call=False,
        file_path={"label": "Choose a file", "mode": "r"},
    )
    def select_bio_data_widget(file_path: Path = None):
        _, metadata = jwslab_load_bio_data(viewer, file_path)
        physical_sizes["x"] = metadata.images[0].pixels.physical_size_x
        physical_sizes["y"] = metadata.images[0].pixels.physical_size_y
        physical_sizes["z"] = metadata.images[0].pixels.physical_size_z

    return select_bio_data_widget
