from magicgui import magicgui
import napari
import numpy as np
from typing import Optional
from skimage.morphology import remove_small_objects


def create_binary_map_widget(
    viewer: napari.Viewer,
):
    """
    Widget to create biary map from the multiple channels
    in the dataset
    """

    @magicgui(
        call_button="Create Binary Mask",
        auto_call=False,
        channel_name={
            "widget_type": "ComboBox",
            "choices": [],
        },
        binary_map_threshold={"label": "Threshold", "min": 0.0, "max": 100.0},
    )
    def binary_map_widget(
        channel_name: Optional[str] = None,
        binary_map_threshold: float = 90.0,
    ):
        cloud_channel = viewer.layers[channel_name].data
        cloud_percentile_float = np.percentile(
            cloud_channel.astype(np.float64), binary_map_threshold
        )

        # Create a binary mask using the percentile as a threshold
        binary_mask = cloud_channel > cloud_percentile_float
        binary_mask = remove_small_objects(binary_mask, min_size=100)
        viewer.add_image(
            binary_mask, name=f"{channel_name} binary mask perc={binary_map_threshold}"
        )

    def update_channel_names_dropdown(event=None):
        channel_layer_names = []
        for layer in viewer.layers:
            if "Channel" in layer.name:
                channel_layer_names.append(layer.name)

        binary_map_widget.channel_name.choices = channel_layer_names

    viewer.layers.events.inserted.connect(update_channel_names_dropdown)
    return binary_map_widget
