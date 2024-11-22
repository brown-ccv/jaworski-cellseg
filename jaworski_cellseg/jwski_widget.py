from magicgui import magicgui
import napari
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer
from qtpy.QtWidgets import QVBoxLayout, QWidget
from .load_data_widget import create_load_data_widget
from .pre_process_data_widget import create_pre_process_data_widget
from .label_counting_widget import create_label_counting_widget
from .subregion_selection_widget import create_region_selection_widget
from .configuration_widget import create_configuration_widget
import yaml
from pathlib import Path

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
        self.config_file_path = Path(__file__).parent / "config"  / "config.yaml"
        with open(self.config_file_path, "r") as f:
            self.config = yaml.safe_load(f)
            settings = self.config.get('settings', {})
            self.configurations = list(settings)
            self.current_config = settings.get('default', {})
        self.init_ui()

    def init_ui(self):
        # Create the main widget to hold both widgets
        layout = QVBoxLayout(self)
        self.inferer_widget = Inferer(self.viewer)
        # Create each widget, passing the viewer to each
        default_index = self.configurations.index("default")
        self.config_widget = create_configuration_widget(self.configurations,
                                                         default_index,
                                                         self.config_file_path,
                                                         self)
        self.data_widget = create_load_data_widget(self.viewer, self.physical_sizes)
        self.pre_process_data_widget = create_pre_process_data_widget(
            self.viewer, self.inferer_widget, self.current_config
        )
        self.count_widget = create_label_counting_widget(self.viewer, self.physical_sizes)
        self.region_selection_widget = create_region_selection_widget(self.viewer)
        self.configure_inferer_widget(self.inferer_widget)

        # # Add widgets to the main layout
        for widget in [
            self.config_widget.native,
            self.data_widget.native,
            self.pre_process_data_widget.native,
            self.count_widget.native,
            self.region_selection_widget.native,
            self.inferer_widget,
        ]:
            layout.addWidget(widget)

    def configure_inferer_widget(self, inferer_widget):
        """
        Configure default settings for the inference widget.
        """
        # Get configuration

        # Model selection and inference settings
        inferer_widget.model_choice.setCurrentIndex(1)  # Select SwinUNetR
        inferer_widget.use_window_choice.setChecked(
            self.current_config["inference_use_window_choice"]
        )
        inferer_widget.window_size_choice.setCurrentIndex(
            inferer_widget.window_size_choice.findText(
                str(self.current_config["inference_window_size"])))
        
        inferer_widget.model_input_size.setValue(
           self.current_config["inference_input"]
        )
        inferer_widget.window_overlap_slider.setValue(
            self.current_config["inference_overlap"]
        )
        inferer_widget.thresholding_checkbox.setChecked(
            self.current_config["inference_perform_threhold"]
        )

        # Set probability threshold (0.6) and instance segmentation settings
        inferer_widget.thresholding_slider.setValue(
            self.current_config["inference_perform_threhold_value"]
        )
        inferer_widget.use_instance_choice.setChecked(
            self.current_config["inference_instance_segmentation"]
        )

        # Configure instance segmentation with Voronoi-Otsu method parameters
        voronoi_widget = inferer_widget.instance_widgets.methods[
            self.current_config["inference_instance_segmentation_option"]
        ]
        voronoi_widget.counters[0].setValue(
            self.current_config["inference_instance_segmentation_spot_signma"]
        )
        voronoi_widget.counters[1].setValue(
            self.current_config["inference_instance_segmentation_outline_signma"]
        )
        voronoi_widget.counters[2].setValue(
            self.current_config[
                "inference_instance_segmentation_small_object_removal"
            ]
        )
