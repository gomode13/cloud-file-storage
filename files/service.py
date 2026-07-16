import os

from botocore.exceptions import ClientError

from files.client import s3_client
import io
import zipfile


def create_user_folder(user_id):
    s3_client.put_object(Bucket='user-files', Key=f'user-{user_id}-files/')


def upload_file(user_id, path, file_obj):
    s3_client.upload_fileobj(Fileobj=file_obj, Bucket='user-files', Key=f'user-{user_id}-files/{path}')


def list_directory(user_id, path):
    response = s3_client.list_objects_v2(Bucket='user-files', Prefix=f'user-{user_id}-files/{path}', Delimiter='/')
    return response.get('Contents', []), response.get('CommonPrefixes', [])


def delete_file(user_id, path):
    s3_client.delete_object(Bucket='user-files', Key=f'user-{user_id}-files/{path}')


def delete_folder(user_id, path):
    prefix = f'user-{user_id}-files/{path}'
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket='user-files', Prefix=prefix):
        contents = page.get('Contents', [])
        if not contents:
            continue
        list_key_to_delete = [{'Key': obj['Key']} for obj in contents]
        s3_client.delete_objects(Bucket='user-files', Delete={'Objects': list_key_to_delete})


def delete_resource(user_id, path):
    if path.endswith('/'):
        delete_folder(user_id, path)
    else:
        delete_file(user_id, path)


def create_directory(user_id, path):
    s3_client.put_object(Bucket='user-files', Key=f'user-{user_id}-files/{path}')


def get_resource_info(user_id, path):
    return s3_client.head_object(Bucket='user-files', Key=f'user-{user_id}-files/{path}')


def move_resource(user_id, path_from, path):
    if path.endswith('/'):
        prefix = f'user-{user_id}-files/{path_from}'
        paginator = s3_client.get_paginator('list_objects_v2')
        response = []
        for page in paginator.paginate(Bucket='user-files', Prefix=prefix):
            contents = page.get('Contents', [])
            if not contents:
                continue
            response.extend([obj['Key'] for obj in contents])
        for obj in response:
            s3_client.copy_object(Bucket='user-files', CopySource={
                'Bucket': 'user-files', 'Key': obj}, Key=f'user-{user_id}-files/{path}' + obj[len(prefix):])
            s3_client.delete_object(Bucket='user-files', Key=obj)
    else:
        s3_client.copy_object(Bucket='user-files', CopySource={
            'Bucket': 'user-files', 'Key': f'user-{user_id}-files/{path_from}'}, Key=f'user-{user_id}-files/{path}')
        s3_client.delete_object(Bucket='user-files', Key=f'user-{user_id}-files/{path_from}')


def download_resource(user_id, path):
    if path.endswith('/'):
        prefix = f'user-{user_id}-files/{path}'
        paginator = s3_client.get_paginator('list_objects_v2')
        response = []
        for page in paginator.paginate(Bucket='user-files', Prefix=prefix):
            contents = page.get('Contents', [])
            if not contents:
                continue
            response.extend([obj['Key'] for obj in contents])
        files = [s3_client.get_object(Bucket='user-files', Key=obj)['Body'].read() for obj in response]

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w') as zip_file:
            for name, content in zip(response, files):
                name = name[len(prefix):]
                if name:
                    zip_file.writestr(name, content)

        buffer.seek(0)
        return buffer
    else:
        return s3_client.get_object(Bucket='user-files', Key=f'user-{user_id}-files/{path}')['Body']


def search_resource(user_id, query):
    prefix = f'user-{user_id}-files/'
    paginator = s3_client.get_paginator('list_objects_v2')
    response = []
    for page in paginator.paginate(Bucket='user-files', Prefix=prefix):
        contents = page.get('Contents', [])
        if not contents:
            continue
        response.extend([obj for obj in contents if query in obj['Key'].split('/')[-1]])
    return response


def resource_exists(user_id, path):
    response = s3_client.list_objects_v2(Bucket='user-files', Prefix=f'user-{user_id}-files/{path}', MaxKeys=1)
    return response.get('KeyCount', 0) > 0