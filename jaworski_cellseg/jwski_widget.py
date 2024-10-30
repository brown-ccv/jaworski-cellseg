from magicgui import magicgui
import napari
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer

viewer = napari.Viewer()
inferer_widget = Inferer(viewer)

from qtpy.QtWidgets import QVBoxLayout, QWidget
import napari
from .load_data_widget import create_load_data_widget
from .pre_process_data_widget import create_pre_process_data_widget
from .label_counting_widget import create_label_counting_widget


def create_combined_widget(viewer: napari.Viewer):
    # Create the main widget to hold both widgets
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)

    # Create each widget, passing the viewer to each
    data_widget = create_load_data_widget(viewer)
    pre_process_data_widget = create_pre_process_data_widget(viewer, inferer_widget)
    count_widget = create_label_counting_widget(viewer)

    # Add both widgets to the main layout
    layout.addWidget(data_widget.native)  # .native provides the actual Qt widget
    layout.addWidget(pre_process_data_widget.native)
    layout.addWidget(count_widget.native)
    layout.addWidget(inferer_widget.native)

    return main_widget
