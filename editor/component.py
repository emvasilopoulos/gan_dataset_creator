class Component:
    def edit(self, frame, *kwargs):
        raise NotImplementedError
        # raise Exception("Method 'edit' is not implemented yet. Implement it before using it...")

    def get_component_name(self) -> str:
        raise NotImplementedError
        # raise Exception("Method 'get_component_name' is not implemented yet. Implement it before using it...")