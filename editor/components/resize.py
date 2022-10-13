import cv2

from editor.component import Component


class Resizer(Component):

    def __init__(self, width: int, height: int) -> None:
        self.height = height
        self.width = width

    def edit(self, frame, *kwargs):
        h, w, c = frame.shape
        if h > self.height and w > self.width:
            return cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_AREA)
        elif h == self.height and w == self.width:
            return frame
        else:
            return cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)



    def get_component_name(self) -> str:
        return f'resize_{self.width}x{self.height}'
