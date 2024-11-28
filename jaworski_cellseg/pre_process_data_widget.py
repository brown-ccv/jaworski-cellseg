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

        return img_rescale

    except Exception as e:
        print(e)


def create_pre_process_data_widget(
    viewer: napari.Viewer, inferer_widget: Inferer, config: dict
):
    @magicgui(
        call_button="Pre process BioImage",
        auto_call=False,
        gaussian_checkbox={"label": "Gaussian Filter"},
        gaussian_factor={"label": "Gaussian sigma"},
        contrast_adjustment={"label": "Contrast Adjustment (Percentiles)"},
        contrast_lower={"label": "min", "min": 0.0, "max": 100.0},
        contrast_upper={"label": "max", "min": 0.0, "max": 100.0},
    )
    def pre_process_data_widget(
        gaussian_checkbox: bool = config.get("gausianFilter", True),
        gaussian_factor: float = config.get("gaussian_sigma", 1.0),
        contrast_adjustment: bool = config.get("contrast_adjustment", True),
        contrast_lower: float = config.get("contrast_min", 5.0),
        contrast_upper: float = config.get("contrast_max", 95.0),
    ) -> "napari.types.LabelsData":

        result_image = pre_process_bio_data(
            viewer,
            gaussian_checkbox,
            gaussian_factor,
            contrast_adjustment,
            contrast_lower,
            contrast_upper,
        )
        viewer.add_image(result_image, name="Pre processed data")
        ## In case more layers are added, lets set the Tiff layer by default
        index = inferer_widget.image_layer_loader.layer_list.findText(
            "Pre processed data"
        )
        inferer_widget.image_layer_loader.layer_list.setCurrentIndex(index)

    return pre_process_data_widget
