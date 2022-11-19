from editor.components.resize import Resizer
from editor.editor import Editor
from input_handler.series_handler import SeriesHandler

if __name__ == '__main__':
    # Editor
    checkpoint_path = "../editor/components/super_resolution_waifu2x/model_check_points/CRAN_V2/CARN_model_checkpoint.pt"
    # super_resolution = SuperResolutionWaifu2x(checkpoint_path, (1080, 1440))
    resizer = Resizer(1024, 1024)
    editor = Editor([resizer])
    print('Created editor...')
    # Series
    series_directory = 'path of directory of series'
    series_name = 'series_name (will be used to store output of current program)'
    series_handler = SeriesHandler(series_directory, series_name, editor=editor)

    #
    extraction_directory = f'... path_to_datasets_storage/{series_handler.series_name}'
    series_handler.extract_images2(extraction_directory, skip_segments_in_seconds=[(0, 5), (60, 240), (1380, -1)],
                                   starting_episode=1, save_every_n_frames=30)
