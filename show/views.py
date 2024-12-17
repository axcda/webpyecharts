from django.shortcuts import render

# Create your views here.

import json
from django.http import HttpResponse
from rest_framework.views import APIView
from pyecharts.charts import Line
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
start = 0 
len = 6 

def line_base():
    global start
    conn = get_redis_connection('default')
    total = conn.zcard('orders-result') - 1  
    if start + len > total: 
        start = 0
    result = conn.zrange('orders-result', start, start + len, withscores=True, score_cast_func=int)
    start += 1
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
        .add_xaxis(xaxis_data = time_list)  # 将时间列表配置给 x 轴
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

class LineTagViews(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(line_base()))
    
class LineViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/line.html',encoding='utf-8').read())

