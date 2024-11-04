from magicgui import magicgui
import napari
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer
from qtpy.QtWidgets import QVBoxLayout, QWidget
import napari
from .load_data_widget import create_load_data_widget
from .pre_process_data_widget import create_pre_process_data_widget
from .label_counting_widget import create_label_counting_widget


class CustomWidget(QWidget):
    def __init__(self, napari_viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent)
        self.viewer = napari_viewer
        self.init_ui()

    def init_ui(self):

        # Create the main widget to hold both widgets
        layout = QVBoxLayout(self)
        inferer_widget = Inferer(self.viewer)
        # Create each widget, passing the viewer to each
        data_widget = create_load_data_widget(self.viewer)
        pre_process_data_widget = create_pre_process_data_widget(self.viewer, inferer_widget)
        count_widget = create_label_counting_widget(self.viewer)

        # # Add both widgets to the main layout
        layout.addWidget(data_widget.native) 
        layout.addWidget(pre_process_data_widget.native)
        layout.addWidget(count_widget.native)
        layout.addWidget(inferer_widget)
        


    