from magicgui import magicgui
import napari
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer
from qtpy.QtWidgets import QVBoxLayout, QWidget
import napari
from .load_data_widget import create_load_data_widget
from .pre_process_data_widget import create_pre_process_data_widget
from .label_counting_widget import create_label_counting_widget
import torch


class JaworskiWidget(QWidget):
    def __init__(self, napari_viewer: "napari.viewer.Viewer", parent=None):
        super().__init__(parent)
        self.viewer = napari_viewer
        self.physical_sizes = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.init_ui()

    def init_ui(self):
        # Create the main widget to hold both widgets
        layout = QVBoxLayout(self)
        inferer_widget = Inferer(self.viewer)
        # Create each widget, passing the viewer to each
        data_widget = create_load_data_widget(self.viewer, self.physical_sizes)
        pre_process_data_widget = create_pre_process_data_widget(
            self.viewer, inferer_widget
        )
        count_widget = create_label_counting_widget(self.viewer, self.physical_sizes)

        # # Add both widgets to the main layout
        layout.addWidget(data_widget.native)
        layout.addWidget(pre_process_data_widget.native)
        layout.addWidget(count_widget.native)

        ## Pre intiialize cellseg3d inference values
        ## Select SwinUNetR and set inference window
        inferer_widget.model_choice.setCurrentIndex(1)
        inferer_widget.use_window_choice.setChecked(True)
        inferer_widget.model_input_size.setValue(96)
        inferer_widget.window_overlap_slider.setValue(50)
        inferer_widget.thresholding_checkbox.setChecked(True)
        ## Probability threshold 0.6 - internally it divides this value by 100
        inferer_widget.thresholding_slider.setValue(60)

        inferer_widget.use_instance_choice.setChecked(True)
        inferer_widget.instance_widgets.methods["Voronoi-Otsu"].counters[0].setValue(
            2.5
        )
        inferer_widget.instance_widgets.methods["Voronoi-Otsu"].counters[2].setValue(
            25.00
        )

        layout.addWidget(inferer_widget)
