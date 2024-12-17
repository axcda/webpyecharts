from django.urls import re_path
from . import views
urlpatterns = [
    re_path(r'^line_tag/$', views.LineTagViews.as_view(), name='va'),
    re_path(r'^index/$', views.LineViews.as_view(), name='va'),
]