from django.urls import path

import views

urlpatterns = [
    path('dict', views.dict_response),
    path('tuple2', views.tuple2_response),
    path('tuple3', views.tuple3_response),
    path('django-response', views.django_response),
    path('stream-response', views.stream_response),
    path('request-json', views.request_json),
    path('request-user', views.request_user),
    path('require-login', views.require_login),
    path('require-staff', views.require_staff),
    path('query-validation', views.query_validation),
    path('json-validation', views.json_validation),
]
