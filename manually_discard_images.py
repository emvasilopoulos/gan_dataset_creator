import os
import time

import cv2


def main(series_dir):
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
    # Specify Sub-Directories
    images_directory = f'{series_dir}/images'
    discarded_images_directory = f'{series_dir}/discarded_images'
    kept_images_directory = f'{series_dir}/manually_optimized_dataset'

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

        # Display image
        cv2.imshow('Image', img_arr)

        while 1:
            # Get Keyboard Input
            k = cv2.waitKey(0)

            # Check key from keyboard
            # W,A,S,D <=> (Up Arrow), (Left Arrow), (Down Arrow), (Right Arrow)
            if k == ord('d'):
                save_path = f'{kept_images_directory}/{image}'
                cv2.imwrite(save_path, img_arr)
                break
            elif k == ord('a'):
                # Move to the next image
                break
            elif k == ord('q'):
                exit_program = True
                break

        idx += 1

        if exit_program:
            break
    with open(f'{series_dir}/{checkpoint_txt}', 'w+') as f:
        f.writelines([f'Index: {idx}\n', f'Image: {images[idx]}'])


if __name__ == '__main__':
    series_directory = 'E:/Projects/Animation Alternatives/justice_league_2001-2004'
    main(series_directory)
