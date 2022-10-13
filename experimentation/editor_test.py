from editor.components.negative_color import NegativeColor
from editor.components.resize import Resizer
from editor.editor import Editor
from input_handler.series_handler import SeriesHandler

if __name__ == '__main__':
    # Editor
    # remove_background = RemoveBackground()
    negative_colors = NegativeColor()
    resizer = Resizer(1024, 1024)
    editor = Editor([resizer, negative_colors])
    print('Created editor...')
    # Series
    series_directory = './Raw Data/Batman The Animated Series - Full HD/Version 1'
    series_name = 'batman_T.A.S._v1'
    series_handler = SeriesHandler(series_directory, series_name, editor=editor)

    #
    extraction_directory = f'./{series_handler.series_name}'
    end_of_intro = 76  # seconds
    series_handler.extract_images(extraction_directory, end_of_intro, starting_episode=1, ending_episode=1, save_every_n_frames=30)
