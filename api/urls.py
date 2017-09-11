from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^session-create', views.session_create, name='session'),
    url(r'^api/', views.api, name='api'),
    url(r'^recommend-questions/', views.recommend_questions, name='userapi'),
    url(r'^session_destroy', views.session_destroy, name='session_destroy'),
]