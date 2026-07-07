from django.http import FileResponse
from config.settings import BASE_DIR

def serve_index(request, path=None):
    index_path = BASE_DIR / 'frontend' / 'dist' / 'index.html'
    return FileResponse(open(index_path, 'rb'))

def serve_config(request):
    config_path = BASE_DIR / 'frontend' / 'dist' / 'config.js'
    return FileResponse(open(config_path, 'rb'), content_type='application/javascript')