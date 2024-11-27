from magicgui import magicgui
import napari
from skimage.measure import regionprops
import pandas as pd
from typing import List, Optional, Iterable
from pathlib import Path


def calculate_center_pixel(bbox: Iterable):
    min_slice, min_row, min_col, max_slice, max_row, max_col = bbox
    return (
        (min_col + max_col) // 2,
        (min_row + max_row) // 2,
        (min_slice + max_slice) // 2,
    )


def calculate_volume(region: "RegionProperties", physical_sizes: dict):
    voxel_volume = physical_sizes["x"] * physical_sizes["y"] * physical_sizes["z"]
    return region.area * voxel_volume


def extract_region_data(region: "RegionProperties", physical_sizes: dict):
    region_data = {
        "label": region.label,
        "area": region.area,
        "centroid_row": region.centroid[2],
        "centroid_col": region.centroid[1],
        "centroid_depth": region.centroid[0],
        "bbox": region.bbox,
    }
    region_data["center_x"], region_data["center_y"], region_data["center_z"] = (
        calculate_center_pixel(region.bbox)
    )

    volume_key = f"volume_{physical_sizes['unit']}"
    region_data[volume_key] = calculate_volume(region, physical_sizes)
    return region_data


def generate_statistics(
    regions: List["RegionProperties"], physical_sizes: dict, save_file_path: Path
):
    # Extract data for each region and compile into a DataFrame
    data = [extract_region_data(region, physical_sizes) for region in regions]
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
            "filter": "*.csv",
        },  # Dynamic choices will be set later
    )
    ## The number of params in the function MUST match
    #  the number of params in the @magicgui annotation
    def cell_counting_widget(
        label_layer_name: Optional[str] = None,
        binary_layer_name: Optional[str] = None,
        total_count: Optional[str] = "",
        save_results: Optional[str] = None,
    ):
        labeled_layer = viewer.layers[label_layer_name]
        binary_mask = viewer.layers[binary_layer_name]

        ## filter lables outside the binary mask
        result_image = labeled_layer.data * binary_mask.data
        filtered_labels_regions = regionprops(result_image)
        count = len(filtered_labels_regions)
        cell_counting_widget.total_count.value = str(count)

        viewer.add_labels(
            result_image, name=f"{count} Filtered Labled layer", opacity=1.0
        )

        file_path = cell_counting_widget.save_results.value
        if file_path:
            path = Path(file_path)
            # Ensure the file has a ".csv" extension
            if not path.suffix:
                path = path.with_suffix(
                    ".csv"
                )  # Add default ".csv" extension if missing

            generate_statistics(filtered_labels_regions, physical_sizes, path)

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
            layer.name for layer in viewer.layers if "binary mask" in layer.name
        ]
        # Update the dropdown choices for label_layer_name
        cell_counting_widget.binary_layer_name.choices = binary_masks_layer_names

        # Optionally, set the default selection to the last label layer if any are available
        if label_layer_names:
            cell_counting_widget.label_layer_name.value = label_layer_names[-1]

    viewer.layers.events.inserted.connect(update_layer_dropdown)
    return cell_counting_widget
