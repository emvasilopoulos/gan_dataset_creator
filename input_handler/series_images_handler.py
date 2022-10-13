import os

import cv2

# This is the first version of series handling - discontinued. Followerd a different design pattern. See series_handler.py
class SeriesImagesHandler:

    def __init__(self, series_images_directory: str) -> None:

        self.original_images_dir = series_images_directory
        self.images_names = os.listdir(series_images_directory)
        self.images_paths = [f'{series_images_directory}/{image}' for image in self.images_names]

    def crop_images(self, width: int, height: int, top_left_pixel_coordinates: tuple, save_directory: str):
        if save_directory == self.original_images_dir:
            raise Exception(
                "Cannot save cropped images in the same directory of original images. Specify another directory")

        # Create directory
        os.makedirs(save_directory, exist_ok=True)

        # Crop all images
        for image_name, image_path in zip(self.images_names, self.images_paths):
            # Original image
            image = cv2.imread(image_path)
            # Coordinates for cropping
            x, y = top_left_pixel_coordinates
            # Cropped image
            new_image = image[y: y + height, x: x + width]
            # Save image
            cv2.imwrite(f'{save_directory}/{width}x{height}_{image_name}', new_image)

    def resize_images(self, width: int, height: int, save_directory: str):
        if save_directory == self.original_images_dir:
            raise Exception(
                "Cannot save resized images in the same directory of original images. Specify another directory")

        # Create directory
        os.makedirs(save_directory, exist_ok=True)

        # Resize all images
        i = 0
        for image_name, image_path in zip(self.images_names, self.images_paths):
            # Original image
            image = cv2.imread(image_path)
            # Resized image
            new_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
            # Save image
            cv2.imwrite(f'{save_directory}/{width}x{height}_{image_name}', new_image)

    def is_image_format(self, filename: str):
        image_formats = ['jpg', 'jpeg', 'JPG', 'png', 'PNG']
        for image_format in image_formats:
            if filename.endswith(image_format):
                return True
        return False


if __name__ == '__main__':
    series_dir = 'your series dir'
    save_dir = 'your save dir'

    series_images_handler = SeriesImagesHandler(series_dir)

    # Resize is better than cropping for stylegan images, meaning creating square images
    series_images_handler.resize_images(1024, 1024, save_dir)
