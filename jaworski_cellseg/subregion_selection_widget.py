from magicgui import magicgui
import napari
from typing import Optional
from napari.layers import Shapes
from skimage.draw import polygon
import numpy as np


def create_region_selection_widget(viewer: napari.Viewer):
    @magicgui(
        call_button="Select region",
        auto_call=False,
        shape_layer_name={
            "widget_type": "ComboBox",
            "choices": [],
        },
        binary_layer_name={
            "widget_type": "ComboBox",
            "choices": [],
        }
    )
    def region_selection_widget(shape_layer_name: Optional[str] = None,
                                binary_layer_name: Optional[str] = None,
                                ):
        shapes_layer = viewer.layers[shape_layer_name]
        binary_layer = viewer.layers[binary_layer_name]
        
        if not shapes_layer.data:
            return

        mask_3d = np.zeros_like(binary_layer.data, dtype=bool)

        # apply subtraction within shape and binary map
        for shape_coords in shapes_layer.data:
            rr, cc = polygon(shape_coords[:, 1], shape_coords[:, 2], binary_layer.data.shape[1:])
            mask_2d  = np.zeros(binary_layer.data.shape[1:], dtype=bool)
            mask_2d [rr, cc] = True 
            # Create a mask based on the shape coordinates
            mask_3d |= np.repeat(mask_2d[np.newaxis, :, :], binary_layer.data.shape[0], axis=0)
        
        modified_data = binary_layer.data * mask_3d
        
        viewer.add_image(modified_data , name="cloud binary region")

    # Update dropdown menu options in the `region_selection_widget` to display
    # available shape and binary layers in the Napari viewer.
    def update_binary_layers_dropdown(event=None):
        # Get names of shape layers in the viewer
        shape_layer_names = [
            layer.name for layer in viewer.layers if isinstance(layer, Shapes)
        ]
        region_selection_widget.shape_layer_name.choices = shape_layer_names

        # Get names of binary masks layers in the viewer
        binary_layer_names = [
            layer.name for layer in viewer.layers if "cloud binary" in layer.name
        ]
        # Update the dropdown choices for label_layer_name
        region_selection_widget.binary_layer_name.choices = binary_layer_names
    
    viewer.layers.events.inserted.connect(update_binary_layers_dropdown)
    return region_selection_widget
