from editor.component import Component
import cv2

class NegativeColor(Component):

    def edit(self, frame, *kwargs):
        return cv2.bitwise_not(frame)

    def get_component_name(self) -> str:
        return 'negative_colors'