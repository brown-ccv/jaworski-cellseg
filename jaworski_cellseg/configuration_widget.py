from magicgui import magicgui
from typing import Optional
import yaml
from pathlib import Path


def create_configuration_widget(
    configurations: list[str], current_config: int, config_file_path: Path, jaworski_obj
):
    """
    Widget to save and load values from the GUI
    """

    def generate_configuration_data(jaworski_obj):
        try:
            # get configuration values
            data = {
                "gausianFilter": jaworski_obj.pre_process_data_widget.gaussian_checkbox.value,
                "gaussian_sigma": jaworski_obj.pre_process_data_widget.gaussian_factor.value,
                "contrast_adjustment": jaworski_obj.pre_process_data_widget.contrast_adjustment.value,
                "contrast_min": jaworski_obj.pre_process_data_widget.contrast_lower.value,
                "contrast_max": jaworski_obj.pre_process_data_widget.contrast_upper.value,
                "binary_map_threshold": jaworski_obj.pre_process_data_widget.binary_map_threshold.value,
                "inference_use_window_choice": jaworski_obj.inferer_widget.use_window_choice.isChecked(),
                "inference_window_size": int(
                    jaworski_obj.inferer_widget.window_size_choice.currentText()
                ),
                "inference_input": jaworski_obj.inferer_widget.model_input_size.value(),
                "inference_overlap": jaworski_obj.inferer_widget.window_overlap_slider.value(),
                "inference_perform_threhold": jaworski_obj.inferer_widget.thresholding_checkbox.isChecked(),
                "inference_perform_threhold_value": jaworski_obj.inferer_widget.thresholding_slider.value(),
                "inference_instance_segmentation": jaworski_obj.inferer_widget.use_instance_choice.isChecked(),
                "inference_instance_segmentation_option": "Voronoi-Otsu",
            }

            # Voronoi-Otsu items
            voronoi_widget = jaworski_obj.inferer_widget.instance_widgets.methods[
                "Voronoi-Otsu"
            ]
            data.update(
                {
                    "inference_instance_segmentation_spot_signma": voronoi_widget.counters[
                        0
                    ].value(),
                    "inference_instance_segmentation_outline_signma": voronoi_widget.counters[
                        1
                    ].value(),
                    "inference_instance_segmentation_small_object_removal": voronoi_widget.counters[
                        2
                    ].value(),
                }
            )

            return data
        except AttributeError as e:
            print(f"Error accessing configuration values: {e}")
            return {}

    # Called when the config dropdown current value changes.
    # Updates all the config widget values
    def set_widget_values(widget, config, mappings):
        try:
            for attr, key in mappings.items():
                # Split the attribute path
                parts = attr.split(".")

                obj_path = getattr(widget, parts[-2])
                obj_property = parts[-1]
                if callable(getattr(obj_path, obj_property, None)):  # If it's a method
                    method = getattr(obj_path, obj_property)
                    method(config[key])
                else:  # If it's a direct attribute
                    setattr(obj_path, obj_property, config[key])
        except Exception as e:
            print(f"Error accessing configuration values: {e}")

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
    def configuration_widget(
        configuration_names: str = configurations[current_config],
        save_confg: Optional[str] = "",
    ):
        config_name = configuration_widget.save_confg.value
        if config_name:
            with open(config_file_path, "w") as file:

                jaworski_obj.config["settings"][
                    configuration_widget.save_confg.value
                ] = generate_configuration_data(jaworski_obj)
                yaml.dump(jaworski_obj.config, file)
                # Update dropdown
                new_choices = list(configuration_widget.configuration_names.choices)
                if config_name not in new_choices:
                    new_choices.append(config_name)
                    configuration_widget.configuration_names.choices = new_choices
                    configuration_widget.configuration_names.value = config_name

    def update_layer_dropdown(event, jaworski_obj):
        configuration = jaworski_obj.config["settings"][event]
        inference_window_size = jaworski_obj.config["settings"][event][
            "inference_window_size"
        ]
        if isinstance(inference_window_size, int):
            jaworski_obj.config["settings"][event]["inference_window_size"] = str(
                inference_window_size
            )
        pre_process_mappings = {
            "gaussian_checkbox.value": "gausianFilter",
            "gaussian_factor.value": "gaussian_sigma",
            "contrast_adjustment.value": "contrast_adjustment",
            "contrast_lower.value": "contrast_min",
            "contrast_upper.value": "contrast_max",
            "binary_map_threshold.value": "binary_map_threshold",
        }

        inferer_mappings = {
            "use_window_choice.setChecked": "inference_use_window_choice",
            "window_size_choice.setCurrentText": "inference_window_size",
            "model_input_size.setValue": "inference_input",
            "window_overlap_slider.setValue": "inference_overlap",
            "thresholding_checkbox.setChecked": "inference_perform_threhold",
            "thresholding_slider.setValue": "inference_perform_threhold_value",
            "use_instance_choice.setChecked": "inference_instance_segmentation",
        }

        set_widget_values(
            jaworski_obj.pre_process_data_widget, configuration, pre_process_mappings
        )
        set_widget_values(jaworski_obj.inferer_widget, configuration, inferer_mappings)
        voronoi_widget = jaworski_obj.inferer_widget.instance_widgets.methods[
            "Voronoi-Otsu"
        ]
        config_keys = [
            "inference_instance_segmentation_spot_signma",
            "inference_instance_segmentation_outline_signma",
            "inference_instance_segmentation_small_object_removal",
        ]
        for i, key in enumerate(config_keys):
            voronoi_widget.counters[i].setValue(configuration[key])

    configuration_widget.configuration_names.changed.connect(
        lambda event: update_layer_dropdown(event, jaworski_obj)
    )

    return configuration_widget
