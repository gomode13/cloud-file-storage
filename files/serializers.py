def build_resource(path, size=None):
    is_folder = path.endswith('/')
    clean_path = path.rstrip('/')

    if '/' in clean_path:
        parent_path, name = clean_path.rsplit('/', 1)
        parent_path += '/'
    else:
        parent_path = ''
        name = clean_path

    if is_folder and name:
        name += '/'

    response = {
        'path': parent_path,
        'name': name,
        'type': 'DIRECTORY' if is_folder else 'FILE',
    }

    if size is not None and not is_folder:
        response['size'] = size

    return response