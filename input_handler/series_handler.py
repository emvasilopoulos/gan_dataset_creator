import os
import cv2

from input_handler.inputhandler import InputHandler


class SeriesHandler(InputHandler):
    acceptable_formats = ['mp4', 'avi', 'mkv']
    image_counter = 0

    def __init__(self, series_directory: str, series_name: str, editor=None) -> None:
        super().__init__(series_directory, series_name, editor)

        self.last_episode = len(self.acceptable_files) - 1

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
        for i, (episode, episode_path) in enumerate(zip(self.acceptable_files, self.acceptable_files_paths)):
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

    def extract_images2(self, directory: str, skip_segments_in_seconds=None,
                        starting_episode=1, ending_episode=None, save_every_n_frames=None):
        # TODO - implement condition "start_1 < end_1 < start_2 < ..."
        if skip_segments_in_seconds is not None and type(skip_segments_in_seconds) != list:
            raise Exception(
                "skipping_frames variable should be a 'list' of 'tuple's indicating segments that should be left out of the extraction process."
                "Example: [(start_1, end_1), (start_2, end_2), ...]. It is critical for start_1 < end_1 < start_2 < ...")

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
        for i, (episode, episode_path) in enumerate(zip(self.acceptable_files, self.acceptable_files_paths)):
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

            if skip_segments_in_seconds is not None:
                skips = [(int(s * fps), int(e * fps)) for (s, e) in skip_segments_in_seconds]
            else:
                skips = []
            if len(skips) > 0:
                skips.reverse()  # We do this because we will use skips.pop() which returns the last element AND pops it out of the list
                skip_frames = skips.pop()
                print(f'Skipping frames of seconds: {skip_frames}')
            else:
                skip_frames = (-1, -1)
            current_frame = 0

            while cap.isOpened():
                # Extract frame
                ret, frame = cap.read()

                if not ret:
                    break

                if current_frame < skip_frames[0]:
                    # Save image
                    if current_frame % save_every_n_frames == 0:
                        edit_names = ''
                        # If an editor is defined, preprocess image before saving
                        if self.editor is not None:
                            edit_names, frame = self.editor.edit_frame(frame)

                        cv2.imwrite(f'{save_dir}/{self.series_name}_{edit_names}{self.image_counter}.jpg', frame)
                        self.image_counter += 1
                        print(f'Saved image: {self.image_counter}')
                        if current_frame % 100 == 0:
                            print(f'Current Frame: {current_frame}')
                elif skip_frames[0] < current_frame < skip_frames[1]:
                    # print('Skipping frames...')
                    pass
                elif skip_frames[1] <= current_frame:
                    print(f'Current Frame: {current_frame}. Preparing new skipping frames...')
                    if len(skips) > 0:
                        skip_frames = skips.pop()
                        print(f'New Skipping frames of seconds: {skip_frames}')
                    else:
                        skip_frames = (-1, -1)  # Flag to indicate to write everything.

                if skip_frames[0] > 0 and skip_frames[1] < 0 and current_frame >= skip_frames[0]:
                    print('Skipping outro...')
                    break
                #
                current_frame += 1
            print(f'| Finished with episode: {episode}\n------------------')
            # Release video Capture
            cap.release()

            if i >= ending_episode:
                print(f'This was the last episode of the series: {self.series_name}...')
                break

    def convert_to_mp4(self, mkv_file: str, temp_directory: str):
        # name, ext = os.path.splitext(mkv_file)  # From: "C:/path/t.txt" --> To: ('C:/path/t', '.txt')
        out_name = f"{temp_directory}/temp_mp4_from_mkv.mp4"
        # Way 1 - Very slow
        # ffmpeg.input(mkv_file).output(out_name).run()
        # Way 2 - Very fast
        os.system(
            f'cmd /c ffmpeg -i "{mkv_file}" -codec copy "{out_name}" -y -hide_banner -loglevel error'
        )
        print("Finished converting {} to mp4".format(mkv_file))
        return out_name


if __name__ == '__main__':
    series_directory = '../Raw Data/Batman The Animated Series - Full HD/Version 1'
    series_name = 'batman_T.A.S._v1'
    series_handler = SeriesHandler(series_directory, series_name)

    extraction_directory = f'../{series_name}/original_images'
    end_of_intro = 76  # seconds
    series_handler.extract_images(extraction_directory, end_of_intro, starting_episode=1)
