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
        try:
            conn = get_redis_connection('default')
            print("Connected to Redis")
            
            total = conn.zcard('orders-result') - 1
            print(f"Total orders: {total}")
            
            if self.start + 6 > total:
                self.start = 0
            
            result = conn.zrange('orders-result', self.start, self.start + 6, withscores=True, score_cast_func=int)
            print(f"Fetched orders: {result}")
            
            self.start += 1
            
            amount_list = []
            time_list = []
            pay_list = []
            
            for item in result:
                str_data = item[0].decode('utf-8')
                print(f"Processing order: {str_data}")
                
                n_index = str_data.find(':')
                name = str_data[:n_index]
                
                temp_list = str_data.split(':')
                pay_list.append(float(temp_list[1]))
                amount_list.append(int(temp_list[2]))
                order_time = time.strftime('%H:%M:%S', time.localtime(item[1]/100))
                time_list.append(order_time)
            
            print(f"Processed data - Times: {time_list}, Pays: {pay_list}")
            
            line = (
                Line()
                .add_xaxis(time_list)
                .add_yaxis(
                    series_name='销售总金额',
                    y_axis=pay_list,
                    symbol='emptyCircle',
                    is_symbol_show=True,
                    label_opts=opts.LabelOpts(is_show=True),
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
            )
            
            result = line.dump_options_with_quotes()
            print("Generated chart config:", result)
            return result
            
        except Exception as e:
            print(f"Error in line_base: {str(e)}")
            raise

class BarPayTagViews(BaseBarView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.bar_base()[0]))

class BarAmountTagViews(BaseBarView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(self.bar_base()[1]))

class LineTagViews(BaseLineView):
    def get(self, request, *args, **kwargs):
        try:
            data = self.line_base()
            print("Raw line data:", data)  # 打印原始数据
            json_data = json.loads(data)
            print("Parsed line data:", json_data)  # 打印解析后的数据
            response_data = {
                'code': 200,
                'msg': 'success',
                'data': json_data
            }
            print("Final line response:", response_data)  # 打印最终响应
            return JsonResponse(response_data)
        except Exception as e:
            print(f"Error in LineTagViews: {str(e)}")
            return JsonResponse({
                'code': 500,
                'msg': str(e),
                'data': None
            })

class BarViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/bar.html', encoding='utf-8').read())

class LineViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/line.html', encoding='utf-8').read())

class BaseTriView(APIView):
    def tri_base(self):
        conn = get_redis_connection('default')
        name_list = list()
        amount_list = list()
        pay_list = list()
        price_list = list()
        
        # 添加调试日志
        print("Starting data fetch from Redis...")
        
        # 从trident-test获取数据
        for item in conn.hscan_iter('trident-test'):
            try:
                name = item[0].decode('utf-8')
                value_str = item[1].decode('utf-8')
                print(f"Processing item - Key: {name}, Value: {value_str}")
                
                # 处理数据
                value_str = value_str.replace('[', '').replace(']', '').replace('"', '')
                amount_str, pay_price_str = value_str.split(',')
                pay_str, price_str = pay_price_str.split(':')
                
                # 转换数据
                amount = float(amount_str.strip())
                pay = float(pay_str.strip())
                price = float(price_str.strip())
                
                # 添加到列表
                name_list.append(name)
                amount_list.append(amount)
                pay_list.append(pay)
                price_list.append(price)
                
                print(f"Processed data - Name: {name}, Amount: {amount}, Pay: {pay}, Price: {price}")
                
            except Exception as e:
                print(f"Error processing item: {item}, Error: {e}")
                continue
        
        print(f"Final data lengths - Names: {len(name_list)}, Amounts: {len(amount_list)}")
        
        # 创建图表配置
        c = (
            Bar()
            .add_xaxis(name_list)
            .add_yaxis(
                series_name='销售量',
                y_axis=amount_list,
                category_gap='20%',
                label_opts=opts.LabelOpts(is_show=True)
            )
            .add_yaxis(
                series_name='销售额',
                y_axis=pay_list,
                label_opts=opts.LabelOpts(is_show=True)
            )
            .add_yaxis(
                series_name='单价',
                y_axis=price_list,
                color='#675bba',
                label_opts=opts.LabelOpts(is_show=True)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title='商品销售数据分析'),
                xaxis_opts=opts.AxisOpts(
                    type_='category',
                    axislabel_opts=opts.LabelOpts(rotate=-30)
                ),
                yaxis_opts=opts.AxisOpts(
                    type_='value',
                    name='数值'
                ),
                tooltip_opts=opts.TooltipOpts(trigger='axis'),
                legend_opts=opts.LegendOpts(pos_top='5%')
            )
        )
        
        # 打印最终的图表配置
        result = c.dump_options_with_quotes()
        print("Chart configuration:", result)
        return result

class TriView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/tri.html', encoding='utf-8').read())

class TriDataView(BaseTriView):
    def get(self, request, *args, **kwargs):
        try:
            data = self.tri_base()
            print("Raw data from tri_base:", data)  # 打印原始数据
            json_data = json.loads(data)
            print("Parsed JSON data:", json_data)  # 打印解析后的数据
            response_data = {
                'code': 200,
                'msg': 'success',
                'data': json_data
            }
            print("Final response data:", response_data)  # 打印最终响应数据
            return JsonResponse(response_data)
        except Exception as e:
            print(f"Error in TriDataView: {str(e)}")
            return JsonResponse({
                'code': 500,
                'msg': str(e),
                'data': None
            })
