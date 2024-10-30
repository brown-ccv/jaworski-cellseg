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
        return bio_data
    except Exception as e:
        print(e)


def create_load_data_widget(viewer: napari.Viewer):
    @magicgui(
        call_button="Select BioImage",
        auto_call=False,
        file_path={"label": "Choose a file", "mode": "r"},
    )
    def select_bio_data_widget(file_path: Path = None) -> "napari.types.LabelsData":
        jwslab_load_bio_data(viewer, file_path)

    return select_bio_data_widget


# load_data_dock = viewer.window.add_dock_widget(
#     select_bio_data_widget, name="Select BioImage"
# )
# pre_process_data_dock = viewer.window.add_dock_widget(
#     pre_process_data_widget, name="Pre process BioImage"
# )
# labe_count_dock = viewer.window.add_dock_widget(
#     cell_counting_widget, name="Label and count"
# )
# # viewer.window.add_dock_widget(cell_counting_widget, name="Label and count")

# # Connect the update function to the layer added event


# ## load cell seg 3d plugin
# inferer_widget.model_choice.setCurrentIndex(1)
# inferer_widget.use_window_choice.setChecked(True)
# inferer_widget.model_input_size.setValue(96)
# inferer_widget.window_overlap_slider.setValue(50)

# inferer_widget.thresholding_checkbox.setChecked(True)

# ## Probability threshold 0.6 - internally it divides this value by 100
# inferer_widget.thresholding_slider.setValue(60)

# inferer_widget.use_instance_choice.setChecked(True)
# inferer_widget.instance_widgets.methods["Voronoi-Otsu"].counters[0].setValue(2.5)
# inferer_widget.instance_widgets.methods["Voronoi-Otsu"].counters[2].setValue(25.00)
# viewer.window.add_dock_widget(inferer_widget, area="right")

# load_data_dock.setFixedSize(300, 100)
# pre_process_data_dock.setFixedSize(300, 220)
# labe_count_dock.setFixedSize(300, 140)
