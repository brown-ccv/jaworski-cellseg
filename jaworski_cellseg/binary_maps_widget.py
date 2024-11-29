from magicgui import magicgui
import napari
import numpy as np
from typing import Optional
from skimage.morphology import remove_small_objects


def create_binary_map(cloud_channel, binary_map_threshold):
    cloud_percentile_float = np.percentile(
        cloud_channel.astype(np.float64), binary_map_threshold
    )

    # Create a binary mask using the percentile as a threshold
    return cloud_channel > cloud_percentile_float


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
        binary_map_1_threshold={"label": "Threshold", "min": 0.0, "max": 100.0},
        channel_2_name={
            "widget_type": "ComboBox",
            "choices": [],
        },
        binary_map_2_threshold={"label": "Threshold", "min": 0.0, "max": 100.0},
    )
    def binary_map_widget(
        channel_name: Optional[str] = None,
        binary_map_1_threshold: float = 90.0,
        channel_2_name: Optional[str] = None,
        binary_map_2_threshold: float = 90.0,
    ):
        cloud_channel = viewer.layers[channel_name].data
        binary_mask = create_binary_map(cloud_channel, binary_map_1_threshold)
        viewer_channel_name = (
            f"{channel_name} binary mask perc={binary_map_1_threshold}"
        )

        # If a second channel is selected, combine the binary masks
        if channel_2_name and channel_2_name in viewer.layers:
            cloud_channel_2 = viewer.layers[channel_2_name].data
            binary_mask_2 = create_binary_map(cloud_channel_2, binary_map_2_threshold)

            # Combine the two masks (logical AND)
            binary_mask = np.logical_and(binary_mask, binary_mask_2)
            viewer_channel_name = (
                f"Combinend {channel_name}-{channel_2_name}"
                f"binary mask"
                f"perc={binary_map_1_threshold}-{binary_map_2_threshold}"
            )

        binary_mask = remove_small_objects(binary_mask, min_size=100)
        viewer.add_image(binary_mask, name=viewer_channel_name)

    def update_channel_names_dropdown(event=None):
        channel_layer_names = []
        for layer in viewer.layers:
            if "Channel" in layer.name:
                channel_layer_names.append(layer.name)

        binary_map_widget.channel_name.choices = channel_layer_names
        binary_map_widget.channel_2_name.choices = channel_layer_names

    viewer.layers.events.inserted.connect(update_channel_names_dropdown)
    return binary_map_widget
