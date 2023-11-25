from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='home'),
    path('prediction/', views.prediction, name='prediction'),
    path('result/<int:pk>', views.result, name='result'),
    path('booking/<int:pk>/<str:result>', views.booking, name='booking'),
    path('downloads/<str:csv_file_path>', views.download, name='download')
]
