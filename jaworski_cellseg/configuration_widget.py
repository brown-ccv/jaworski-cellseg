
from magicgui import magicgui
from typing import Optional
from .jwski_widget import JaworskiWidget
import yaml
import copy

def create_configuration_widget(configurations: list[str],
                                jwski_widget: JaworskiWidget):
    @magicgui(
        call_button="Save Configuration",
        auto_call=False,
        configuration_names={
            "label": "Config",
            "widget_type": "ComboBox",
            "choices": configurations,
        },
        save_confg={
            "label": "Save",
        },
    )
    def configuration_widget(configuration_names: str = configurations[0],
                             save_confg: Optional[str] = ""):
        if save_confg.value:
            file_name = f"{save_confg.value}.yaml"
            with open(jwski_widget.config_directory / file_name, "w") as file:
                data = copy.deepcopy(jwski_widget.config)
                data["settings"]["gausianFilter"] = jwski_widget.pre_process_data_widget.gaussian_checkbox.value
                data["settings"]["gaussian_sigma"] = jwski_widget.pre_process_data_widget.gaussian_factor.value
                data["settings"]["contrast_adjustment"] = jwski_widget.pre_process_data_widget.contrast_adjustment.value
                data["settings"]["contrast_min"] = jwski_widget.pre_process_data_widget.contrast_lower.value
                data["settings"]["contrast_max"] = jwski_widget.pre_process_data_widget.contrast_upper.value
                data["settings"]["binary_map_threshold"] =  jwski_widget.pre_process_data_widget.binary_map_threshold.value
                data["settings"]["inference_use_window_choice"] = jwski_widget.inferer_widget.model_choice.value
                data["settings"]["inference_input"] = jwski_widget.inferer_widget.model_input_size.value
                data["settings"]["inference_overlap"] = jwski_widget.inferer_widget.window_overlap_slider.value
                data["settings"]["inference_perform_threhold"] = jwski_widget.inferer_widget.thresholding_checkbox.value
                data["settings"]["inference_perform_threhold_value"] = jwski_widget.inferer_widget.thresholding_slider.value
                data["settings"]["inference_instance_segmentation"] = jwski_widget.inferer_widget.use_instance_choice.value
                data["settings"]["inference_instance_segmentation_option"] = jwski_widget.inferer_widget.instance_widgets.methods.value
                data["settings"]["inference_instance_segmentation_spot_signma"] = jwski_widget.inferer_widget.methods.counters[0].value
                data["settings"]["inference_instance_segmentation_outline_signma"] = jwski_widget.inferer_widget.methods.counters[1].value
                data["settings"]["inference_instance_segmentation_small_object_removal"] = jwski_widget.inferer_widget.methods.counters[2].value
                yaml.dump(jwski_widget.config, file)
    
    return configuration_widget
