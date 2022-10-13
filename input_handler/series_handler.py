import os

import cv2
import ffmpeg


class SeriesHandler:
    unacceptable_chars = ['\\', '/', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}', ',', '?',
                          ';', ':', '<', '>', '|', '~']
    allowed_special_chars = ['-', '_', '.']

    image_counter = 0

    def __init__(self, series_directory: str, series_name: str, editor=None) -> None:
        print('- Listing episodes...')
        self.episodes = [x for x in os.listdir(series_directory) if self.is_video_format(x)]  # Works fine
        self.episodes_paths = [f'{series_directory}/{episode}' for episode in self.episodes]
        self.last_episode = len(self.episodes) - 1

        # This name will be used in extracted images
        is_ok = self.check_series_name(series_name)
        if is_ok:
            self.series_name = series_name
        else:
            raise Exception(
                "The following characters are not allowed for a series_name: " + str(self.unacceptable_chars)
                + "\nUse only " + str(self.allowed_special_chars))

        self.editor = editor
        if self.editor is not None:
            for tool in self.editor.components:
                self.series_name += f'_{tool.get_component_name()}'
        # To save hard disk allocation, MKV files will be converted to MP4 when extracting frames and then will delete
        # the generated MP4

    def extract_images(self, directory: str, end_of_intro_in_seconds=0, start_of_outro_in_seconds=21 * 60,
                       starting_episode=1, ending_episode=None, save_every_n_frames=None):
        starting_episode = starting_episode - 1  # convert to index
        if starting_episode < 0:
            starting_episode = 0
        if ending_episode is None:
            ending_episode = self.last_episode
        print(f'- Extracting images from episode: {starting_episode + 1}. Indices of extracted images start from 0.')
        print(f'- Extracted images will be saved at: {directory}')
        # 0 - Create Temp directory
        temp_directory = f'{directory}/temp_files'
        os.makedirs(temp_directory, exist_ok=True)

        # 1 - Create images directory
        save_dir = f'{directory}/images'
        os.makedirs(save_dir, exist_ok=True)

        # 2 - Scan over episodes of series
        for i, (episode, episode_path) in enumerate(zip(self.episodes, self.episodes_paths)):
            # Skip episodes
            if i < starting_episode:
                continue

            print(f'► Working on episode: {episode}')
            # 3 - Create MP4 from MKV or move on as is
            if episode.endswith('mkv'):
                print('Current Episode is an MKV file. Converting to MP4...')
                video_path = self.convert_to_mp4(episode_path, temp_directory)
            else:
                video_path = episode_path

            # 4 - Create Video Capture
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f'FPS of video: {fps}')

            #
            if save_every_n_frames is None:
                if fps <= 10:
                    save_every_n_frames = 2
                elif fps <= 20:
                    save_every_n_frames = 4
                elif fps <= 30:
                    save_every_n_frames = 8
                elif fps <= 40:
                    save_every_n_frames = 16
                elif fps <= 50:
                    save_every_n_frames = 32
                else:
                    save_every_n_frames = 64

            print(f'Saving every: {save_every_n_frames} frames')
            # If it's the first episode of extracting images, we need the intro as well. Otherwise, skip the intro. We don't need multiple times the same frames
            if i == 0:
                print('Saving intro...')
                start_saving_from_frame = 0
            else:
                print('NOT Saving intro...')
                start_saving_from_frame = int(fps * end_of_intro_in_seconds)

            stop_saving_from_frame = int(fps * start_of_outro_in_seconds)

            current_frame = 0

            while cap.isOpened():
                # Extract frame
                ret, frame = cap.read()

                if not ret:
                    break

                # Save image
                if current_frame >= start_saving_from_frame:
                    if current_frame % save_every_n_frames == 0:
                        edit_names = ''
                        # If an editor is defined, preprocess image before saving
                        if self.editor is not None:
                            edit_names, frame = self.editor.edit_frame(frame)

                        cv2.imwrite(f'{save_dir}/{self.series_name}_{edit_names}{self.image_counter}.jpg', frame)
                        self.image_counter += 1
                        print(f'Saved image: {self.image_counter}')
                if current_frame >= stop_saving_from_frame:
                    break
                #
                current_frame += 1
            print(f'| Finished with episode: {episode}\n------------------')
            # Release video Capture
            cap.release()

            if i >= ending_episode:
                print(f'This was the last episode of the series: {self.series_name}...')
                break

    # TODO - Add all the formats missing
    def is_video_format(self, filename: str):
        video_formats = ['mp4', 'avi', 'mkv']
        for video_format in video_formats:
            if filename.endswith(video_format):
                return True
        return False

    def check_series_name(self, series_name: str):
        for char in series_name:
            for unacceptable_char in self.unacceptable_chars:
                if char == unacceptable_char:
                    return False
        return True

    def convert_to_mp4(self, mkv_file: str, temp_directory: str):
        # name, ext = os.path.splitext(mkv_file)  # From: "C:/path/t.txt" --> To: ('C:/path/t', '.txt')
        out_name = f"{temp_directory}/temp_mp4_from_mkv.mp4"
        ffmpeg.input(mkv_file).output(out_name).run()
        print("Finished converting {} to mp4".format(mkv_file))
        return out_name


if __name__ == '__main__':
    series_directory = '../Raw Data/Batman The Animated Series - Full HD/Version 1'
    series_name = 'batman_T.A.S._v1'
    series_handler = SeriesHandler(series_directory, series_name)

    extraction_directory = f'../{series_name}/original_images'
    end_of_intro = 76  # seconds
    series_handler.extract_images(extraction_directory, end_of_intro, starting_episode=1)
