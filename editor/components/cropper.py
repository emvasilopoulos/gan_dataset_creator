from editor.component import Component


class Cropper(Component):
    TOP_LEFT_WIDTH_HEIGHT = 1
    CENTER_WIDTH_HEIGHT = 2
    TOP_LEFT_BOTTOM_RIGHT = 3

    def __init__(self, x, y, w, h, style=1) -> None:

        if style == Cropper.CENTER_WIDTH_HEIGHT:
            self.x1, self.x2 = int(x - w / 2), int(x + w / 2)
            self.y1, self.y2 = int(y - h / 2), int(y + h / 2)
        elif style == Cropper.TOP_LEFT_WIDTH_HEIGHT:
            self.x1, self.x2 = x, x + w
            self.y1, self.y2 = y, y + h
        elif style == Cropper.TOP_LEFT_BOTTOM_RIGHT:
            self.x1, self.x2 = x, w
            self.y1, self.y2 = y, h
        else:
            raise Exception('Unrecognized style of cropping coordinates.')

    def update_crop_coords(self, x, y, w, h, style=1):
        if style == Cropper.CENTER_WIDTH_HEIGHT:
            self.x1, self.x2 = int(x - w / 2), int(x + w / 2)
            self.y1, self.y2 = int(y - h / 2), int(y + h / 2)
        elif style == Cropper.TOP_LEFT_WIDTH_HEIGHT:
            self.x1, self.x2 = x, x + w
            self.y1, self.y2 = y, y + h
        elif style == Cropper.TOP_LEFT_BOTTOM_RIGHT:
            self.x1, self.x2 = x, w
            self.y1, self.y2 = y, h
        else:
            raise Exception('Unrecognized style of cropping coordinates.')

    def edit(self, frame, *kwargs):

        return frame[self.x1:self.x2, self.y1: self.y2]

    def get_component_name(self) -> str:
        return 'cropper'
