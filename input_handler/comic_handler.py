import os
import re
import tarfile
import time
import zipfile
import shutil

import cv2

from editor.components.place_in_frame import InFramePlacer
from editor.editor import Editor
from input_handler.inputhandler import InputHandler


# CBR files are RAR files
# CBT files are TAR files

# TAR extension are uncompressed files --> UNIX
# RAR files are compressed files --> Windows


class ComicHandler(InputHandler):
    acceptable_formats = ['cbr', 'cbz', 'cbt']
    winrar_exe_path = '\"C:/Program Files/Winrar/winrar.exe\"'
    covers_subdir = 'covers'
    pages_subdir = 'pages'
    endings_subdir = 'endings'
    cover_counter = 0
    page_counter = 0
    ending_counter = 0

    def __init__(self, series_directory: str, series_name: str, editor=None) -> None:
        super().__init__(series_directory, series_name, editor)
        self.series_directory = series_directory
        self.acceptable_files = self.sort_as_human(self.acceptable_files)
        self.acceptable_files_paths = self.sort_as_human(self.acceptable_files_paths)

    def extract(self, directory: str, covers=1, ending_pages=-1):

        os.makedirs(f'{directory}/{self.series_name}/{self.covers_subdir}', exist_ok=True)
        os.makedirs(f'{directory}/{self.series_name}/{self.pages_subdir}', exist_ok=True)
        os.makedirs(f'{directory}/{self.series_name}/{self.endings_subdir}', exist_ok=True)

        os.makedirs(f'{directory}/{self.series_name}/{self.endings_subdir}', exist_ok=True)

        for filename in self.acceptable_files:
            print(f'Making archive file of {filename}')
            new_filename, new_file_path = self.comic_file_to_archive(filename)
            if new_filename is None:
                continue
            if new_file_path is None:
                continue

            extraction_dir = f'{self.series_directory}/temp'
            if new_filename.endswith('rar'):
                extracted_files_directory = self.extract_from_rar(extraction_dir, new_file_path)
            elif new_filename.endswith('tar'):
                # TODO - Implement Extract from TAR
                continue
                raise NotImplementedError
            elif new_filename.endswith('zip'):
                # TODO - Implement Extract from ZIP
                extracted_files_directory = self.extract_from_zip(extraction_dir, new_file_path)
            else:
                print(f'Unknown archive format of file: {new_filename}. Skipping...')
                continue

            # find
            """ Sort the list of extracted images in the way that humans expect."""
            extracted_images = self.sort_as_human(os.listdir(extracted_files_directory))

            #
            if covers > len(extracted_images):
                print(
                    f'Number of covers set is greater than the extracted files. Setting covers to {len(extracted_images)}.')
                covers = len(extracted_images)

            # Save Covers
            self.cover_counter = self.move_sectioned_pages(
                0,
                covers,
                extracted_files_directory,
                extracted_images,
                directory,
                subdir=self.covers_subdir,
                starting_counter=self.cover_counter
            )

            if covers < len(extracted_images):
                if covers < len(extracted_images) - ending_pages:
                    if ending_pages > 0:
                        last_pages_idx = len(extracted_images) - ending_pages
                    else:
                        last_pages_idx = len(extracted_images)
                    # Save pages
                    self.page_counter = self.move_sectioned_pages(
                        covers,
                        last_pages_idx,
                        extracted_files_directory,
                        extracted_images,
                        directory,
                        subdir=self.pages_subdir,
                        starting_counter=self.page_counter
                    )
                elif covers > len(extracted_images) - ending_pages:
                    last_pages_idx = len(extracted_images)
                    # Save pages
                    self.page_counter = self.move_sectioned_pages(
                        covers,
                        last_pages_idx,
                        extracted_files_directory,
                        extracted_images,
                        directory,
                        subdir=self.pages_subdir,
                        starting_counter=self.page_counter
                    )
                    print('- Saved Covers and Pages')
                    continue

                # Save Endings
                if ending_pages <= 0:
                    print('Skipping Endings..')
                else:
                    self.ending_counter = self.move_sectioned_pages(
                        len(extracted_images) - ending_pages,
                        len(extracted_images),
                        extracted_files_directory,
                        extracted_images,
                        directory,
                        subdir=self.endings_subdir,
                        starting_counter=self.ending_counter
                    )
                    print('- Saved Covers, Pages and Endings')

            else:
                print('- Saved only covers')
            print(f'-- Finished with: {filename}\n')
        print('Finished all succesfully...')

        [os.remove(f'{self.series_directory}/temp/{file}') for file in os.listdir(f'{self.series_directory}/temp/')]
        # os.remove(f'{self.series_directory}/temp/')
        os.remove(f'{self.series_directory}/temp.rar')

    def move_sectioned_pages(self, start_idx, end_idx, extracted_files_directory, extracted_images, directory, subdir,
                             starting_counter=0):

        for i in range(start_idx, end_idx):
            image = extracted_images[i]
            if self.editor is not None:
                edit_names = ''
                img = cv2.imread(f'{extracted_files_directory}/{image}')
                edit_names, frame = self.editor.edit_frame(img)
                cv2.imwrite(
                    f'{directory}/{self.series_name}/{subdir}/{self.series_name}_{subdir}_{edit_names}_{starting_counter}.jpg',
                    frame
                )
            else:
                shutil.move(
                    src=f'{extracted_files_directory}/{image}',
                    dst=f'{directory}/{self.series_name}/{subdir}/{self.series_name}_{subdir}_{starting_counter}.jpg'
                )
            starting_counter += 1
        return starting_counter

    def comic_file_to_archive(self, filename: str):

        if filename.lower().endswith('cbr'):
            new_filename = 'temp.rar'
        elif filename.lower().endswith('cbt'):
            new_filename = 'temp.tar'
        elif filename.lower().endswith('cbz'):
            new_filename = 'temp.zip'
        else:
            print(f'Unknown format of file: "{filename}"')
            return None, None

        new_file_path = f'{self.series_directory}/{new_filename}'
        shutil.copy(
            src=f'{self.series_directory}/{filename}',
            dst=new_file_path
        )

        #
        return new_filename, new_file_path

    def extract_from_rar(self, extraction_directory: str, rar_file_path: str):
        # Prepare command
        comic_types = '(\'*.jpg\')'

        #
        extracted_files_directory = self.__check_extraction_dir(extraction_directory)

        extracted_files_directory_quoted = f'\'\"{extracted_files_directory}\"\''
        rar_file_path_quoted = f'\'\"{rar_file_path}\"\''
        argument_list = f'@(\"e\",{rar_file_path_quoted},{comic_types},{extracted_files_directory_quoted},\"y\")'

        # Run Powershell command that uses winrar.
        subprocess.run(
            [
                'powershell',
                '-Command',
                f'Start-Process -FilePath {self.winrar_exe_path} -ArgumentList {argument_list} -Wait'
            ],
            capture_output=True
        )

        return extracted_files_directory

    def extract_from_zip(self, extraction_directory: str, zip_file_path: str):
        extracted_files_directory = self.__check_extraction_dir(extraction_directory)
        with zipfile.ZipFile(f'{zip_file_path}', 'r') as archive:
            archive.extractall(extracted_files_directory)
        self.__crawl_to_bring_to_root(extracted_files_directory)
        return extracted_files_directory

    def __check_extraction_dir(self, extraction_dir: str):
        if extraction_dir.endswith('/'):
            return extraction_dir
        else:
            return f'{extraction_dir}/'

    def __crawl_to_bring_to_root(self, extraction_dir: str):
        for root, dirs, files in os.walk(extraction_dir):
            for name in files:
                print(root, '|||', name)

    def sort_as_human(self, extracted_images):
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(extracted_images, key=alphanum_key)


"""
POWERSHELL COMMANDS TO UNRAR

Example:
1) $argList = @("x",  ('"E:/Projects/Animation Alternatives/Raw Data/COMICS/Justice League/Justice League ~ 000.rar"'), ('*jpg'),('"E:/Projects/Animation Alternatives/Raw Data/COMICS/Justice League/test_folder/"'))
2) Start-Process -FilePath "C:\Program Files\Winrar\winrar.exe" -ArgumentList $argList

Theory:
1) Create a variable that holds a tuple of arguments. They will be passed on to the executable
$argList = @("x", <rar_file_path>, <destination_folder>)
2) Start-Process -FilePath <winrar_executable_path> -ArgumentList $argList
or Directly
Start-Process -FilePath <winrar_executable_path> -ArgumentList @("x", <rar_file_path>, <destination_folder>)

"""
import subprocess

if __name__ == '__main__':
    series_directory = 'E:/Projects/Animation Alternatives/Raw Data/COMICS/test_zip'
    series_name = 'test_zip'

    editor = Editor([InFramePlacer(1024, color=(255, 255, 255))])
    comic_handler = ComicHandler(series_directory, series_name, editor=editor)

    save_dir = 'E:/Projects/Animation Alternatives'
    comic_handler.extract(save_dir, covers=1, ending_pages=1)
