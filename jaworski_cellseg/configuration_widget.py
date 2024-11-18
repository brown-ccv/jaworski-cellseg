
from magicgui import magicgui
from typing import Optional
from .jwski_widget import JaworskiWidget
import yaml

def create_configuration_widget( configurations: list[str],
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
                yaml.dump(data, file)
    
    return configuration_widget
