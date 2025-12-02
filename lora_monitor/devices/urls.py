from django.urls import path
from . import views
from .api import TTNWebhookView

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='list'),
    path('<int:pk>/', views.device_detail, name='detail'),
    path('create/', views.device_create, name='create'),
    path('<int:pk>/update/', views.device_update, name='update'),
    path('<int:pk>/delete/', views.device_delete, name='delete'),
    path("api/ttn/webhook/", TTNWebhookView.as_view(), name="ttn_webhook"),
]
