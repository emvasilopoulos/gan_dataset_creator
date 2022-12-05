import os

class InputHandler:
    unacceptable_chars = ['\\', '/', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}', ',', '?',
                          ';', ':', '<', '>', '|', '~']
    allowed_special_chars = ['-', '_', '.']

    acceptable_formats = ['cbr', 'cbz', 'cbt']

    def __init__(self, series_directory: str, series_name: str, editor=None) -> None:
        print('- Listing episodes...')

        self.acceptable_files = [x for x in os.listdir(series_directory) if self.is_acceptable_format(x)]
        self.acceptable_files_paths = [f'{series_directory}/{comic}' for comic in self.acceptable_files]

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

    def check_series_name(self, series_name: str):
        for char in series_name:
            for unacceptable_char in self.unacceptable_chars:
                if char == unacceptable_char:
                    return False
        return True

    def is_acceptable_format(self, filename: str):
        for format in self.acceptable_formats:
            if filename.endswith(format):
                return True
        return False
