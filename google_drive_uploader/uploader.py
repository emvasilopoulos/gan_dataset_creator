import os

from google_drive_uploader.utils import get_service
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

if __name__ == '__main__':

    credential_json = 'client_secret ... .json'

    base_uri = 'https://www.googleapis.com/upload/drive/v3/files'
    uploadType = 'media'

    # Prepare Service - Connect to google Drive
    service = get_service(credential_json)

    folder = 'local path of directory with images to upload'
    files_to_upload = os.listdir(folder)

    parent_folder_id = 'find it from folder\'s URL'
    n_files = len(files_to_upload)
    failed_to_upload = []
    n_succesful = 2523 + 3646
    i = 2523 + 3646
    while i < n_files:
        try:
            file_metadata = {
                'name': f'{files_to_upload[i]}',
                'parents': ['']
            }
            media = MediaFileUpload(f'{folder}/{files_to_upload[i]}')
            # pylint: disable=maybe-no-member
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            n_succesful += 1
            print(f'- Uploaded ({n_succesful}/{n_files})')
        except HttpError as error:
            print(F'---\nAn error occurred: {error}')
            print(f'Failed to upload: {files_to_upload[i]}\n---')
            failed_to_upload.append(files_to_upload[i])
        except Exception as e:
            print(e)
            failed_to_upload.append(files_to_upload[i])
            continue

    if len(failed_to_upload) > 0:
        with open('failed_to_upload.txt', 'w+') as f:
            f.writelines(failed_to_upload)

