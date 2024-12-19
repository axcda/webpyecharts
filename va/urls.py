from django.urls import re_path
from .line_views import LineViews, LineTagViews
from .bar_views import BarViews, BarPayTagViews, BarAmountTagViews
from .tri_views import TriView, TriDataView

urlpatterns = [
    re_path(r'^bar_pay_tag/$', BarPayTagViews.as_view(), name='va'),
    re_path(r'^bar_amount_tag/$', BarAmountTagViews.as_view(), name='va'),
    re_path(r'^bar/$', BarViews.as_view(), name='va'),
    re_path(r'^line_tag/$', LineTagViews.as_view(), name='line_tag'),
    re_path(r'^line/$', LineViews.as_view(), name='line'),
    re_path(r'^tri/$', TriView.as_view(), name='tri'),
    re_path(r'^tri_tag/$', TriDataView.as_view(), name='tri_tag'),
]