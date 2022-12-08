import os
import shutil
import time

import cv2


def calculate_resize_dimensions(image_shape, new_height=720):
    h, w, _ = image_shape
    image_ratio = h / w
    new_width = int(new_height / image_ratio)

    return new_height, new_width

def main(series_dir, subdir_name='good_ones'):
    # Check if checkpoint exists
    checkpoint_txt = 'last_image_processed.txt'
    if os.path.exists(f'{series_dir}/{checkpoint_txt}'):
        # read last index
        with open(f'{series_dir}/{checkpoint_txt}', 'r+') as f:
            lines = f.readlines()
            first_line = lines[0]
            _, s_number = first_line.split()
            idx = int(s_number)
    else:
        idx = 0
    idx = 0

    # Specify Sub-Directories
    images_directory = f'{series_dir}'
    kept_images_directory = f'{series_dir}/{subdir_name}'

    # Create Directory
    os.makedirs(kept_images_directory, exist_ok=True)

    # List all images
    images = os.listdir(images_directory)

    # flag for inner loop
    exit_program = False

    # Main loop
    for i in range(idx, len(images)):
        image = images[i]
        # Prepare path for imread
        image_path = f'{images_directory}/{image}'
        # Read image
        img_arr = cv2.imread(image_path)

        if img_arr.shape[0] > 720:

            new_h, new_w = calculate_resize_dimensions(img_arr.shape)
            img_arr = cv2.resize(img_arr, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Display image
        cv2.imshow('Image', img_arr)

        # Get Keyboard Input
        k = cv2.waitKey(0)
        # Check key from keyboard
        # W,A,S,D <=> (Up Arrow), (Left Arrow), (Down Arrow), (Right Arrow)
        if k == ord('d'):
            save_path = f'{kept_images_directory}/{image}'

            shutil.move(
                src=image_path,
                dst=save_path
            )
        elif k == ord('a'):
            # Move to the next image
            pass
        elif k == ord('q'):
            exit_program = True

        idx += 1

        if exit_program:
            break
    with open(f'{series_dir}/{checkpoint_txt}', 'w+') as f:
        f.writelines([f'Index: {idx}\n', f'Image: {images[idx]}'])


if __name__ == '__main__':
    series_directory = 'E:/Projects/Animation Alternatives/detective_comics_v1_1937_to_2011/covers'
    save_subdir_name = 'good'
    main(series_directory, save_subdir_name)
