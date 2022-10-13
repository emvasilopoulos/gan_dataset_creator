from editor.component import Component


class Editor:
    def __init__(self, list_of_editing_tools: list) -> None:
        # Check for types
        for tool in list_of_editing_tools:
            if not isinstance(tool, Component):
                raise Exception(f"Use only a list of Component objects, not {type(tool)}...")
        #
        self.components = list_of_editing_tools

    def edit_frame(self, frame):
        extra_name = ''
        for tool in self.components:
            frame = tool.edit(frame)
            extra_name += f'{tool.get_component_name()}_'

        return extra_name, frame