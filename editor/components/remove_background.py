from editor.component import Component
from rembg import remove
from rembg.session_factory import new_session


class RemoveBackground(Component):

    def __init__(self, net='u2net', alpha_matting=False) -> None:
        self.session = new_session(net)
        self.alpha_matting = alpha_matting

    def edit(self, frame, *kwargs):
        return remove(frame, session=self.session, alpha_matting=self.alpha_matting)

    def get_component_name(self) -> str:
        return 'remove_background'
