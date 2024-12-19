from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from pyecharts.charts import Bar
from pyecharts import options as opts
from django_redis import get_redis_connection
import json

class BaseBarView(APIView):
    def bar_base(self):
        conn = get_redis_connection('default')
        name_list = list()
        pay_list = list()
        amount_list = list()
        
        # 从total-result获取汇总数据
        for item in conn.hscan_iter('total-result'):
            name_list.append(item[0].decode('utf-8'))
            pay_amount_mix = item[1].decode('utf-8').split(':')
            pay_list.append(float(pay_amount_mix[0]))
            amount_list.append(int(pay_amount_mix[1]))
            
        c_pay = (
            Bar()
            .add_xaxis(name_list)
            .add_yaxis('销售额', pay_list)
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=-30),
                ),
                title_opts=opts.TitleOpts(title='xxx促销活动', subtitle='各类商品销售额对比')
            )
            .dump_options_with_quotes()
        )
        
        c_amount = (
            Bar()
            .add_xaxis(name_list)
            .add_yaxis('销量', amount_list, color='pink')
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=-30)
                ),
                title_opts=opts.TitleOpts(
                    title='xxx促销活动',
                    subtitle='各类商品销量对比'
                )
            )
            .dump_options_with_quotes()
        )
        return [c_pay, c_amount]

class BarPayTagViews(BaseBarView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.bar_base()[0]))

class BarAmountTagViews(BaseBarView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.bar_base()[1]))

class BarViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/bar.html', encoding='utf-8').read()) 