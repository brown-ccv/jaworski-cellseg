from magicgui import magicgui
import napari
from typing import Optional


# Define your callback function
def on_value_change(event):
    print(f"ComboBox value changed to: {event.value}")

def create_region_selection_widget(viewer: napari.Viewer):
    @magicgui(
        call_button="Select region",
        auto_call=False,
        binary_layer_name={
            "widget_type": "ComboBox",
            "choices": [],
        }, 
    )
    def region_selection_widget(binary_layer_name: Optional[str] = None,):
        ...
    
    def update_binary_layers_dropdown(event=None):
        binary_masks_layer_names = [
            layer.name for layer in viewer.layers if "cloud binary" in layer.name
        ]
        region_selection_widget.binary_layer_name.choices = binary_masks_layer_names
    
    region_selection_widget.binary_layer_name.changed.connect(on_value_change)
    viewer.layers.events.inserted.connect(update_binary_layers_dropdown)
    return region_selection_widget
