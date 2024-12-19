from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from pyecharts.charts import Line
from pyecharts import options as opts
from django_redis import get_redis_connection
import json
import time

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

class LineTagViews(BaseLineView):
    def get(self, request, *args, **kwargs):
        try:
            data = self.line_base()
            print("Raw line data:", data)
            json_data = json.loads(data)
            print("Parsed line data:", json_data)
            response_data = {
                'code': 200,
                'msg': 'success',
                'data': json_data
            }
            print("Final line response:", response_data)
            return JsonResponse(response_data)
        except Exception as e:
            print(f"Error in LineTagViews: {str(e)}")
            return JsonResponse({
                'code': 500,
                'msg': str(e),
                'data': None
            })

class LineViews(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/line.html', encoding='utf-8').read()) 