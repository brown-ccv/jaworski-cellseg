from skimage import data
from skimage.util import img_as_float
from magicgui import magicgui
import napari
import numpy as np
from skimage import exposure
from scipy.ndimage import gaussian_filter
from skimage.morphology import remove_small_objects
from napari_cellseg3d.code_plugins.plugin_model_inference import Inferer


def pre_process_bio_data(
    napari_viewer,
    gaussian_checkbox,
    gaussian_factor,
    contrast_adjustment,
    contrast_lower,
    contrast_upper,
    binary_map_threshold,
):
    try:
        channel_data = napari_viewer.layers["Channel 0"].data
        if contrast_adjustment:
            lower_limit = contrast_lower
            upper_limit = contrast_upper
            pLow, pUp = np.percentile(channel_data, (lower_limit, upper_limit))
            img_rescale = exposure.rescale_intensity(
                channel_data, in_range=(pLow, pUp), out_range="dtype"
            )
        else:
            img_rescale = exposure.rescale_intensity(
                channel_data, in_range="image", out_range="dtype"
            )

        if gaussian_checkbox:
            # Apply gaussian
            print(f"Applying Gaussian fileter sigma {gaussian_factor}")
            img_rescale = gaussian_filter(img_rescale, sigma=gaussian_factor)

        cloud_channel = napari_viewer.layers["Channel 2"].data
        cloud_percentile_float = np.percentile(
            cloud_channel.astype(np.float64), binary_map_threshold
        )

        # Create a binary mask using the percentile as a threshold
        binary_mask = cloud_channel > cloud_percentile_float
        binary_mask = remove_small_objects(binary_mask, min_size=100)
        return img_rescale, binary_mask
    except Exception as e:
        print(e)


def create_pre_process_data_widget(viewer: napari.Viewer, inferer_widget: Inferer):
    @magicgui(
        call_button="Pre process BioImage",
        auto_call=False,
        gaussian_checkbox={"label": "Gaussian Filter"},
        gaussian_factor={"label": "Gaussian sigma"},
        contrast_adjustment={"label": "Contrast Adjustment (Percentiles)"},
        contrast_lower={"label": "min", "min": 0.0, "max": 100.0},
        contrast_upper={"label": "max", "min": 0.0, "max": 100.0},
        binary_map_threshold={"label": "Binary Threshold", "min": 0.0, "max": 100.0},
    )
    def pre_process_data_widget(
        gaussian_checkbox: bool = True,
        gaussian_factor: float = 1.0,
        contrast_adjustment: bool = True,
        contrast_lower: float = 5.0,
        contrast_upper: float = 95.0,
        binary_map_threshold: float = 90.0,
    ) -> "napari.types.LabelsData":

        result_image, binary_mask = pre_process_bio_data(
            viewer,
            gaussian_checkbox,
            gaussian_factor,
            contrast_adjustment,
            contrast_lower,
            contrast_upper,
            binary_map_threshold,
        )
        viewer.add_image(
            binary_mask, name=f"cloud binary mask perc={binary_map_threshold}"
        )
        viewer.add_image(result_image, name="Pre processed data")
        ## In case more layers are added, lets set the Tiff layer by default
        index = inferer_widget.image_layer_loader.layer_list.findText(
            "Pre processed data"
        )
        inferer_widget.image_layer_loader.layer_list.setCurrentIndex(index)

    return pre_process_data_widget
