from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.addUser, name='addUser'),
    path('edit/<id>/', views.editUser, name='editUser'),
    path('delete/<id>/', views.deleteUser, name='deleteUser'),
    
    path('export/data', views.dataExport, name='dataExport'),
    path('import/data', views.dataImport, name='dataImport'),
    
    # API
    path('api/user/add/', views.addUserAPI, name='addUserAPI'), # Add API
    path('api/user/update/<id>/', views.UpdateUserListAPI, name='UpdateUserListAPI'), # Update list API
    path('api/user_details/', views.userDetailsAPI, name='userDetailsAPI'), # Get all data API
    path('api/user/list/<id>/', views.userListAPI, name='userListAPI'), # Get single data API
    path('api/user/delete/<id>/', views.deleteUserListAPI, name='deleteUserListAPI'), # Get single data API
]
