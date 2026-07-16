from django.urls import path
from files import views

urlpatterns = [
    path('directory', views.DirectoryView.as_view(), name='directory'),
    path('resource/download', views.ResourceDownloadView.as_view(), name='resource_download'),
    path('resource/move', views.ResourceMoveView.as_view(), name='resource_move'),
    path('resource/search', views.ResourceSearchView.as_view(), name='resource_search'),
    path('resource', views.ResourceView.as_view(), name='resource'),
]
