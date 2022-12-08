import os

import cv2

from editor.component import Component
import numpy as np


# Support only for squares for the time being.
def calculate_new_dimensions(h, w, bg_dim=1024):
    bg_h = bg_dim
    bg_w = bg_dim
    original_image_ratio = h / w

    if bg_h < h and bg_w < w:
        if h < w:  # Big dimension is 'w'
            new_w = bg_w
            new_h = int(original_image_ratio * new_w)
        else:
            new_h = bg_h
            new_w = int(new_h // original_image_ratio)
        interpolation = cv2.INTER_AREA
    elif bg_h >= h and bg_w < w:
        new_w = bg_w
        new_h = original_image_ratio * new_w
        interpolation = cv2.INTER_AREA
    elif bg_h < h and bg_w >= w:
        new_h = bg_h
        new_w = int(new_h // original_image_ratio)
        interpolation = cv2.INTER_AREA
    elif bg_h >= h and bg_w >= w:
        if h < w:
            new_w = bg_w
            new_h = int(original_image_ratio * new_w)
        else:
            new_h = bg_h
            new_w = int(new_h // original_image_ratio)
        interpolation = cv2.INTER_CUBIC
    else:
        raise Exception(f"Missed a case that is not implemented. bg_dim={bg_dim}, h={h}, w={w}")
    return new_h, new_w, interpolation


class InFramePlacer(Component):

    def __init__(self, frame_dimension, color=(0, 0, 0)) -> None:
        self.frame_height = frame_dimension
        self.frame_width = frame_dimension
        self.color = color

    def edit(self, frame, *kwargs):
        h, w, c = frame.shape
        new_h, new_w, interpolation = calculate_new_dimensions(h, w, self.frame_width)

        resized_frame = cv2.resize(frame, (new_w, new_h), interpolation=interpolation)
        if new_h == self.frame_height:
            pixels_left = int((self.frame_width - new_w) / 2)
            pixels_right = self.frame_width - pixels_left - new_w
            # center horizontally
            self.new_frame = np.pad(resized_frame, ((0, 0), (pixels_left, pixels_right), (0, 0)),
                                    constant_values=(0, 0))

            self.new_frame[:, :pixels_left, 0].fill(self.color[0])
            self.new_frame[:, pixels_left + new_w:, 0].fill(self.color[0])

            self.new_frame[:, :pixels_left, 1].fill(self.color[1])
            self.new_frame[:, pixels_left + new_w:, 1].fill(self.color[1])

            self.new_frame[:, :pixels_left, 2].fill(self.color[2])
            self.new_frame[:, pixels_left + new_w:, 2].fill(self.color[2])

        elif new_w == self.frame_width:
            pixels_up = int((self.frame_height - new_h) / 2)
            pixels_down = self.frame_height - pixels_up - new_h
            # center horizontally
            self.new_frame = np.pad(resized_frame, ((pixels_up, pixels_down), (0, 0), (0, 0)),
                                    constant_values=(0, 0))

            self.new_frame[:pixels_up, :, 0].fill(self.color[0])
            self.new_frame[pixels_up + new_h:, :, 0].fill(self.color[0])

            self.new_frame[:pixels_up, :, 1].fill(self.color[1])
            self.new_frame[pixels_up + new_h:, :, 1].fill(self.color[1])

            self.new_frame[pixels_up:, :, 2].fill(self.color[2])
            self.new_frame[pixels_up + new_h:, :, 2].fill(self.color[2])
        else:
            raise Exception(
                f'Incorrect dimensions: new_w={new_w}, new_w={new_h}. Both are different from {self.frame_width}')

        return self.new_frame

    def get_component_name(self) -> str:
        return f'place_in_frame{self.frame_height}x{self.frame_width}'


if __name__ == '__main__':
    component = InFramePlacer(1024, color=(255, 255, 255))
    images_dir = 'E:/Projects/Animation Alternatives/detective_comics_v1_1937_to_2011/covers/good'
    save_dir = 'E:/Projects/Animation Alternatives/detective_comics_v1_1937_to_2011/covers/good_padded'
    os.makedirs(save_dir, exist_ok=True)

    images = os.listdir(images_dir)
    for image in images:
        img = cv2.imread(f'{images_dir}/{image}')
        new_image = component.edit(img)
        cv2.imwrite(f'{save_dir}/{image}', new_image)
