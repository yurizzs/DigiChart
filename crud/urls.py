from django.urls import path
from . import views

urlpatterns = [
    path('user/add', views.add_user),
    path('user/list', views.user_list),
    path('patient/add', views.add_patient),
]