from magicgui import magicgui
import napari
from skimage.measure import regionprops


def create_label_counting_widget(viewer: napari.Viewer):
    @magicgui(
        call_button="Label and count",
        label_layer_name={
            "widget_type": "ComboBox",
            "choices": [],
        },  # Dynamic choices will be set later
        binary_layer_name={
            "widget_type": "ComboBox",
            "choices": [],
        },  # Dynamic choices will be set later
        total_count={
            "label": "Total count",
            "enabled": False,
        },  # Make the textbox read-only
    )
    def cell_counting_widget(
        label_layer_name: str = None,
        binary_layer_name: str = None,
        total_count: str = "",
    ):
        print(f"Selected label layer: {label_layer_name}")
        print(f"Total count: {total_count}")
        labeled_layer = viewer.layers[label_layer_name]
        binary_mask = viewer.layers[binary_layer_name]
        ## filter lables outside the binary mask
        result_image = labeled_layer.data * binary_mask.data
        filtered_labels_regions = regionprops(result_image)
        count = len(filtered_labels_regions)
        cell_counting_widget.total_count.value = str(count)
        viewer.add_labels(result_image, name=f"{count} Filtered Labled layer")

    def update_layer_dropdown(event=None):
        # Get names of all label layers in the viewer
        label_layer_names = [
            layer.name
            for layer in viewer.layers
            if isinstance(layer, napari.layers.Labels)
        ]
        # Update the dropdown choices for label_layer_name
        cell_counting_widget.label_layer_name.choices = label_layer_names

        # Get names of binary masks layers in the viewer
        binary_masks_layer_names = [
            layer.name for layer in viewer.layers if "cloud binary" in layer.name
        ]
        # Update the dropdown choices for label_layer_name
        cell_counting_widget.binary_layer_name.choices = binary_masks_layer_names

        # Optionally, set the default selection to the last label layer if any are available
        if label_layer_names:
            cell_counting_widget.label_layer_name.value = label_layer_names[-1]

    viewer.layers.events.inserted.connect(update_layer_dropdown)
    return cell_counting_widget
