from django.http import FileResponse

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound

from config.exceptions import Conflict
from files import service
from files.serializers import build_resource


# Create your views here.

class BaseFileView(APIView):
    permission_classes = [IsAuthenticated]


class DirectoryView(BaseFileView):

    def get(self, request):
        path = request.query_params.get('path')
        user_id = request.user.id

        if path is None:
            raise ValidationError('Невалидный или отсутствующий путь')
        content, prefixes = service.list_directory(user_id, path)

        if not content and not prefixes and path:
            raise NotFound('Папка не существует')

        prefix = f'user-{user_id}-files/'
        result = []
        for c in content:
            item_path, size = c['Key'][len(prefix):], c['Size']
            if item_path == path:
                continue
            result.append(build_resource(item_path, size))
        for p in prefixes:
            item_path = p['Prefix'][len(prefix):]
            if item_path == path:
                continue
            result.append(build_resource(item_path))

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        path = request.query_params.get('path')
        user_id = request.user.id

        if path is None or not path.endswith('/'):
            raise ValidationError('Невалидный или отсутствующий путь к новой папке')

        if service.resource_exists(user_id, path):
            raise Conflict('Папка уже существует')
        clean_path = path.rstrip('/')

        if '/' in clean_path:
            parent_path, _ = clean_path.rsplit('/', 1)
            parent_path = parent_path + '/'
            if service.resource_exists(user_id, parent_path):
                service.create_directory(user_id, path)
                return Response(build_resource(path), status=status.HTTP_201_CREATED)
            else:
                raise NotFound('Родительская папка не существует')
        else:
            service.create_directory(user_id, path)
            return Response(build_resource(path), status=status.HTTP_201_CREATED)


class ResourceView(BaseFileView):

    def get(self, request):
        path = request.query_params.get('path')
        user_id = request.user.id
        if path is None:
            raise ValidationError('Невалидный или отсутствующий путь')
        if not service.resource_exists(user_id, path):
            raise NotFound('Ресурс не найден')
        if path.endswith('/'):
            return Response(build_resource(path), status=status.HTTP_200_OK)
        else:
            size = service.get_resource_info(user_id, path)['ContentLength']
            return Response(build_resource(path, size), status=status.HTTP_200_OK)

    def post(self, request):
        path = request.data.get('path')
        files_list = request.FILES.getlist('object')
        user_id = request.user.id
        if path is None or not files_list:
            raise ValidationError('Невалидное тело запроса')
        result = []
        for f in files_list:
            full_path = path + f.name
            if service.resource_exists(user_id, full_path):
                raise Conflict('Файл уже существует')
        for f in files_list:
            full_path = path + f.name
            service.upload_file(user_id, full_path, f)
            result.append(build_resource(full_path, f.size))
        return Response(result, status=status.HTTP_201_CREATED)

    def delete(self, request):
        path = request.query_params.get('path')
        user_id = request.user.id
        if path is None:
            raise ValidationError('Невалидный или отсутствующий путь')
        if not service.resource_exists(user_id, path):
            raise NotFound('Ресурс не найден')
        service.delete_resource(user_id, path)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourceDownloadView(BaseFileView):

    def get(self, request):
        path = request.query_params.get('path')
        user_id = request.user.id
        if path is None:
            raise ValidationError('Невалидный или отсутствующий путь')
        if not service.resource_exists(user_id, path):
            raise NotFound('Ресурс не найден')
        file = service.download_resource(user_id, path)
        if path.endswith('/'):
            filename = path.rstrip('/').rsplit('/', 1)[-1] + '.zip'
        else:
            filename = path.rsplit('/', 1)[-1]
        return FileResponse(file, as_attachment=True, filename=filename)


class ResourceMoveView(BaseFileView):

    def post(self, request):
        path_from = request.query_params.get('from')
        path_to = request.query_params.get('to')
        user_id = request.user.id

        if path_from is None or path_to is None:
            raise ValidationError('Невалидный или отсутствующий путь')
        if path_from.endswith('/') != path_to.endswith('/'):
            raise ValidationError('Невалидный или отсутствующий путь')
        if not service.resource_exists(user_id, path_from):
            raise NotFound('Ресурс не найден')
        if service.resource_exists(user_id, path_to):
            raise Conflict('Ресурс, лежащий по пути to уже существует')
        service.move_resource(user_id, path_from, path_to)

        if not path_from.endswith('/'):
            size = service.get_resource_info(user_id, path_to)['ContentLength']
            return Response(build_resource(path_to, size), status=status.HTTP_200_OK)
        else:
            return Response(build_resource(path_to), status=status.HTTP_200_OK)


class ResourceSearchView(BaseFileView):

    def get(self, request):
        user_id = request.user.id
        query = request.query_params.get('query')
        if query is None:
            raise ValidationError('Невалидный или отсутствующий поисковый запрос')
        response = service.search_resource(user_id, query)
        result = []
        prefix = f'user-{user_id}-files/'
        for obj in response:
            path = obj['Key'][len(prefix):]
            size = obj['Size']
            result.append(build_resource(path, size))
        return Response(result, status=status.HTTP_200_OK)
