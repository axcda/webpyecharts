from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^bar_pay_tag/$', views.BarPayTagViews.as_view(), name='va'),
    re_path(r'^bar_amount_tag/$', views.BarAmountTagViews.as_view(), name='va'),
    re_path(r'^bar/$', views.BarViews.as_view(), name='va'),
    re_path(r'^line_tag/$', views.LineTagViews.as_view(), name='line_tag'),
    re_path(r'^line/$', views.LineViews.as_view(), name='line'),
]