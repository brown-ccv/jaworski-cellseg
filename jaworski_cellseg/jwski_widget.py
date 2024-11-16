from magicgui import magicgui
import napari
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer
from qtpy.QtWidgets import QVBoxLayout, QWidget
from .load_data_widget import create_load_data_widget
from .pre_process_data_widget import create_pre_process_data_widget
from .label_counting_widget import create_label_counting_widget
from .subregion_selection_widget import create_region_selection_widget
import yaml


class JaworskiWidget(QWidget):
    """
    A custom QWidget for napari that integrates multiple data-processing widgets
    into a single interface. It initializes data loading, preprocessing, and
    label counting widgets, as well as configuring an inference model.
    """

    def __init__(self, napari_viewer: napari.viewer.Viewer, parent=None):
        super().__init__(parent)
        self.viewer = napari_viewer
        self.physical_sizes = {"x": 0.0, "y": 0.0, "z": 0.0}
        # Read the configuration file
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        self.init_ui()

    def init_ui(self):
        # Create the main widget to hold both widgets
        layout = QVBoxLayout(self)
        inferer_widget = Inferer(self.viewer)
        # Create each widget, passing the viewer to each
        data_widget = create_load_data_widget(self.viewer, self.physical_sizes)
        pre_process_data_widget = create_pre_process_data_widget(
            self.viewer, inferer_widget, self.config
        )
        count_widget = create_label_counting_widget(self.viewer, self.physical_sizes)
        region_selection_widget = create_region_selection_widget(self.viewer)
        self.configure_inferer_widget(inferer_widget)

        # # Add widgets to the main layout
        for widget in [
            data_widget.native,
            pre_process_data_widget.native,
            count_widget.native,
            region_selection_widget.native,
            inferer_widget,
        ]:
            layout.addWidget(widget)

    def configure_inferer_widget(self, inferer_widget):
        """
        Configure default settings for the inference widget.
        """
        # Model selection and inference settings
        inferer_widget.model_choice.setCurrentIndex(1)  # Select SwinUNetR
        inferer_widget.use_window_choice.setChecked(
            self.config["settings"]["inference_use_window_choice"]
        )
        inferer_widget.model_input_size.setValue(
            self.config["settings"]["inference_input"]
        )
        inferer_widget.window_overlap_slider.setValue(
            self.config["settings"]["inference_overlap"]
        )
        inferer_widget.thresholding_checkbox.setChecked(
            self.config["settings"]["inference_perform_threhold"]
        )

        # Set probability threshold (0.6) and instance segmentation settings
        inferer_widget.thresholding_slider.setValue(
            self.config["settings"]["inference_perform_threhold_value"]
        )
        inferer_widget.use_instance_choice.setChecked(
            self.config["settings"]["inference_instance_segmentation"]
        )

        # Configure instance segmentation with Voronoi-Otsu method parameters
        voronoi_widget = inferer_widget.instance_widgets.methods[
            self.config["settings"]["inference_instance_segmentation_option"]
        ]
        voronoi_widget.counters[0].setValue(
            self.config["settings"]["inference_instance_segmentation_spot_signma"]
        )
        voronoi_widget.counters[1].setValue(
            self.config["settings"]["inference_instance_segmentation_outline_signma"]
        )
        voronoi_widget.counters[2].setValue(
            self.config["settings"][
                "inference_instance_segmentation_small_object_removal"
            ]
        )
