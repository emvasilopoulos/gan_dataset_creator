import cv2
from PIL import Image, ExifTags

class AbstractGen:

    def preprocess_image(self, image):
        pass

    def sample_image_info(self, image_path):
        image = Image.open(image_path)
        print(f'Image dimensions: width={image.width()}, height={image.height()}')
        exif = {ExifTags.TAGS[k]: v for k, v in image._getexif().items() if k in ExifTags.TAGS}

        for key in exif.keys():
            print(f'{key}: {exif[key]}')
        # TODO - Extract any other information relevant to the model that will be trained


