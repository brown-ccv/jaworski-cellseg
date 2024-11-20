
from magicgui import magicgui
from typing import Optional
import yaml

def create_configuration_widget(configurations: list[str],
                               current_config,
                               config_file_path,
                               jaworski_obj):
    """ 
     Widget to save and load values from the GUI
    """
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
    def configuration_widget(configuration_names: str = configurations[current_config],
                             save_confg: Optional[str] = ""):
        
        if configuration_widget.save_confg.value:
            with open(config_file_path, "w") as file:
                data = {}
                data["gausianFilter"] = jaworski_obj.pre_process_data_widget.gaussian_checkbox.value
                data["gaussian_sigma"] = jaworski_obj.pre_process_data_widget.gaussian_factor.value
                data["contrast_adjustment"] = jaworski_obj.pre_process_data_widget.contrast_adjustment.value
                data["contrast_min"] = jaworski_obj.pre_process_data_widget.contrast_lower.value
                data["contrast_max"] = jaworski_obj.pre_process_data_widget.contrast_upper.value
                data["binary_map_threshold"] =  jaworski_obj.pre_process_data_widget.binary_map_threshold.value
                data["inference_use_window_choice"] = jaworski_obj.inferer_widget.use_window_choice.isChecked()
                data["inference_window_size"] = int(jaworski_obj.inferer_widget.window_size_choice.currentText())
                data["inference_input"] = jaworski_obj.inferer_widget.model_input_size.value()
                data["inference_overlap"] = jaworski_obj.inferer_widget.window_overlap_slider.value()
                data["inference_perform_threhold"] = jaworski_obj.inferer_widget.thresholding_checkbox.isChecked()
                data["inference_perform_threhold_value"] = jaworski_obj.inferer_widget.thresholding_slider.value()
                data["inference_instance_segmentation"] = jaworski_obj.inferer_widget.use_instance_choice.isChecked()
                data["inference_instance_segmentation_option"] = "Voronoi-Otsu"
                voronoi_widget = jaworski_obj.inferer_widget.instance_widgets.methods[ "Voronoi-Otsu" ]
                data["inference_instance_segmentation_spot_signma"] = voronoi_widget.counters[0].value()
                data["inference_instance_segmentation_outline_signma"] = voronoi_widget.counters[1].value()
                data["inference_instance_segmentation_small_object_removal"] = voronoi_widget.counters[2].value()
                jaworski_obj.config['settings'][configuration_widget.save_confg.value] = data
                yaml.dump(jaworski_obj.config, file)
                ## Add configuration to the dropdown list
                configuration_widget.configuration_names.choices = (
                    list(configuration_widget.configuration_names.choices)
                      + [configuration_widget.save_confg.value])
    
    def update_layer_dropdown(event, jaworski_obj):
        print(f"Load configuration: {event} ")
        configuration = jaworski_obj.config['settings'][event]
        jaworski_obj.pre_process_data_widget.gaussian_checkbox.value = configuration["gausianFilter"]
        jaworski_obj.pre_process_data_widget.gaussian_factor.value = configuration["gaussian_sigma"]
        jaworski_obj.pre_process_data_widget.contrast_adjustment.value = configuration["contrast_adjustment"]
        jaworski_obj.pre_process_data_widget.contrast_lower.value = configuration["contrast_min"]
        jaworski_obj.pre_process_data_widget.contrast_upper.value = configuration["contrast_max"]
        jaworski_obj.pre_process_data_widget.binary_map_threshold.value = configuration["binary_map_threshold"]
        jaworski_obj.inferer_widget.use_window_choice.setChecked(configuration["inference_use_window_choice"])
        jaworski_obj.inferer_widget.window_size_choice.setCurrentIndex(configuration["inference_window_size"])
        jaworski_obj.inferer_widget.model_input_size.setValue(configuration["inference_input"])
        jaworski_obj.inferer_widget.window_overlap_slider.setValue(configuration["inference_overlap"])
        jaworski_obj.inferer_widget.thresholding_checkbox.setChecked(configuration["inference_perform_threhold"])
        jaworski_obj.inferer_widget.thresholding_slider.setValue(configuration["inference_perform_threhold_value"])
        jaworski_obj.inferer_widget.use_instance_choice.setChecked(configuration["inference_instance_segmentation"])
        voronoi_widget = jaworski_obj.inferer_widget.instance_widgets.methods[ "Voronoi-Otsu" ]
        voronoi_widget.counters[0].setValue(configuration["inference_instance_segmentation_spot_signma"])
        voronoi_widget.counters[1].setValue(configuration["inference_instance_segmentation_outline_signma"])
        voronoi_widget.counters[2].setValue(configuration["inference_instance_segmentation_small_object_removal"])


    configuration_widget.configuration_names.changed.connect(
        lambda event: update_layer_dropdown(event, jaworski_obj))

    return configuration_widget
