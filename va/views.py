from django.shortcuts import render

# Create your views here.
import json
from django.http import HttpResponse
from rest_framework.views import APIView
from pyecharts.charts import Bar, Line  # 同时导入Bar和Line
from pyecharts import options as opts
from django_redis import get_redis_connection
import time

def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str, 
        content_type='application/json',
    )
    response['Access-Control-Allow-Origin'] = '*'
    return response

def json_response(data, code=200):
    data = {
        'code': code,
        'msg': 'success',
        'data': data,
    }
    return response_as_json(data)

JsonResponse = json_response


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

class BaseLineView(APIView):
    start = 0
    
    def line_base(self):
        conn = get_redis_connection('default')
        total = conn.zcard('orders-result') - 1
        if self.start + 6 > total:
            self.start = 0
        result = conn.zrange('orders-result', self.start, self.start + 6, withscores=True, score_cast_func=int)
        self.start += 1
        
        amount_list = list()
        time_list = list()
        pay_list = list()
        
        str_data = result[0][0].decode('utf-8')
        n_index = str_data.find(':')
        name = str_data[:n_index]
        
        for item in result:
            temp_list = item[0].decode('utf-8').split(':')
            pay_list.append(float(temp_list[1]))
            amount_list.append(int(temp_list[2]))
            order_time = time.strftime('%H:%M:%S', time.localtime(item[1]/100))
            time_list.append(order_time)
        
        line = (
            Line()
            .add_xaxis(time_list)
            .add_yaxis(
                series_name='销售总金额',
                y_axis=pay_list,
                symbol='emptyCircle',
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=name+'销售趋势图'),
                xaxis_opts=opts.AxisOpts(type_='category'),
                yaxis_opts=opts.AxisOpts(
                    type_='value',
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
            )
            .dump_options_with_quotes()
        )
        return line

class BarPayTagViews(BaseBarView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.bar_base()[0]))

class BarAmountTagViews(BaseBarView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.bar_base()[1]))

class LineTagViews(BaseLineView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.line_base()))

class BarViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/bar.html', encoding='utf-8').read())

class LineViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/line.html', encoding='utf-8').read())
