from qtpy.QtWidgets import QVBoxLayout, QWidget, QScrollArea
import yaml
from pathlib import Path
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer
from jaworski_cellseg.load_data_widget import create_load_data_widget
from jaworski_cellseg.pre_process_data_widget import create_pre_process_data_widget
from jaworski_cellseg.label_counting_widget import create_label_counting_widget
from jaworski_cellseg.subregion_selection_widget import create_region_selection_widget

# This one requires more work because of the need for a JaworskiWidget object
# from jaworski_cellseg.configuration_widget import create_configuration_widget
from jaworski_cellseg.binary_maps_widget import create_binary_map_widget


def test_create_load_file_widget(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    physical_sizes = {"x": 0.0, "y": 0.0, "z": 0.0, "unit": None}
    widget = create_load_data_widget(viewer,physical_sizes)
    assert widget is not None
    # Layout exists
    assert widget.native.layout() is not None
    assert widget.call_button.options['text'] == "Open BioImage ..."


def test_pre_process_data_widget(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    inferer_widget = Inferer(viewer)
    config_file_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_file_path, "r") as f:
            config = yaml.safe_load(f)
            settings = config.get("settings", {})
            current_config = settings.get("default", {})
    
    widget = create_pre_process_data_widget(viewer, inferer_widget, current_config)
    assert widget is not None
    # Layout exists
    assert widget.native.layout() is not None
    assert widget.call_button.options['text'] == "Pre process BioImage"

def test_create_label_counting_widget(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    physical_sizes = {"x": 0.0, "y": 0.0, "z": 0.0, "unit": None}
    widget = create_label_counting_widget(viewer,physical_sizes)
    assert widget is not None
    # Layout exists
    assert widget.native.layout() is not None
    assert widget.call_button.options['text'] == "Label and count"

def test_create_region_selection_widget(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    widget = create_region_selection_widget(viewer)
    assert widget is not None
    # Layout exists
    assert widget.native.layout() is not None
    assert widget.call_button.options['text'] == "Select region"

def test_create_binary_map_widget(make_napari_viewer_proxy):
    viewer = make_napari_viewer_proxy()
    widget = create_binary_map_widget(viewer)
    assert widget is not None
    # Layout exists
    assert widget.native.layout() is not None
    assert widget.call_button.options['text'] == "Create Binary Mask"