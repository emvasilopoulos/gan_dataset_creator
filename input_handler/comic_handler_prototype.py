import subprocess

if __name__ == '__main__':
    winrar_exe_path = '\"C:/Program Files/Winrar/winrar.exe\"'
    rar_file_path = '\'\"E:/Projects/Animation Alternatives/Raw Data/COMICS/Justice League/Justice League ~ 000.rar\"\''
    comic_types = '(\'*.jpg\')'
    extracted_files_directory1 = '\'\"E:/Projects/Animation Alternatives/Raw Data/COMICS/Justice League/test_folder4/\"\''
    argument_list = f'@(\"e\",{rar_file_path},{comic_types},{extracted_files_directory1})'

    # print(f'powershell -Command Start-Process -FilePath {winrar_exe_path} -ArgumentList {argument_list}')
    # os.system(f'powershell -Command Start-Process -FilePath {winrar_exe_path} -ArgumentList {argument_list}')
    subprocess.run(
        [
            'powershell',
            '-Command',
            f'Start-Process -FilePath {winrar_exe_path} -ArgumentList {argument_list}'
        ]
    )