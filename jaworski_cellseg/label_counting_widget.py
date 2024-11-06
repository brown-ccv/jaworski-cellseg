from magicgui import magicgui
import napari
from skimage.measure import regionprops
import pandas as pd


def generate_statistics(regions, physical_sizes, save_file_path):
    # Initialize a list to hold the properties data
    data = []

    # Loop through each region and filter for the labels of interest
    for region in regions:
        # Extract properties and add them to the data list as a dictionary
        region_data = {
            "label": region.label,
            "area": region.area,
            "centroid_row": region.centroid[2],
            "centroid_col": region.centroid[1],
            "centroid_depth": region.centroid[0],
            "bbox": region.bbox,  # Add more properties as needed
        }

        min_slice, min_row, min_col, max_slice, max_row, max_col = region.bbox

        # Calculate the center pixel of the bounding box
        center_pixel = (
            (min_col + max_col) // 2,
            (min_row + max_row) // 2,
            (min_slice + max_slice) // 2,
        )
        region_data["center_x"] = center_pixel[0]
        region_data["center_y"] = center_pixel[1]
        region_data["center_z"] = center_pixel[2]

        voxel_count = region.area  # This is the number of voxels in the region
        voxel_volume = (
            physical_sizes["x"] * physical_sizes["y"] * physical_sizes["z"]
        )  # Volume of a single voxel in µm³
        total_volume_um3 = voxel_count * voxel_volume  # Total volume in µm³

        region_data["volume"] = total_volume_um3

        data.append(region_data)
    # Convert the data list to a DataFrame
    df = pd.DataFrame(data)
    # Save the DataFrame to a CSV file
    df.to_csv(save_file_path, index=False)


def create_label_counting_widget(viewer: napari.Viewer, physical_sizes: dict):
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
        save_results={
            "widget_type": "FileEdit",
            "mode": "w",
        },  # Dynamic choices will be set later
    )
    def cell_counting_widget(
        label_layer_name: str = None,
        binary_layer_name: str = None,
        total_count: str = "",
        save_results: str = None,
    ):
        labeled_layer = viewer.layers[label_layer_name]
        binary_mask = viewer.layers[binary_layer_name]

        ## filter lables outside the binary mask
        result_image = labeled_layer.data * binary_mask.data
        filtered_labels_regions = regionprops(result_image)
        count = len(filtered_labels_regions)
        cell_counting_widget.total_count.value = str(count)

        viewer.add_labels(result_image, name=f"{count} Filtered Labled layer")

        if cell_counting_widget.save_results.value:
            file_path = cell_counting_widget.save_results.value
            with open(file_path, "w") as f:
                generate_statistics(filtered_labels_regions, physical_sizes, file_path)

            viewer.status = f"Results saved to {file_path}"

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
