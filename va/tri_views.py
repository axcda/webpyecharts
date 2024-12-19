from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from pyecharts.charts import Bar, Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from django_redis import get_redis_connection
import json

class BaseTriView(APIView):
    def tri_base(self):
        conn = get_redis_connection('default')
        name_list = list()
        amount_list = list()
        pay_list = list()
        price_list = list()
        
        for item in conn.hscan_iter('trident-test'):
            try:
                name = item[0].decode('utf-8')
                value_str = item[1].decode('utf-8')
                
                value_str = value_str.replace('[', '').replace(']', '').replace('"', '')
                amount_str, pay_price_str = value_str.split(',')
                pay_str, price_str = pay_price_str.split(':')
                
                amount = float(amount_str.strip())
                pay = float(pay_str.strip())
                price = float(price_str.strip())
                
                name_list.append(name)
                amount_list.append(amount)
                pay_list.append(pay)
                price_list.append(price)
                
            except Exception as e:
                print(f"Error processing item: {item}, Error: {e}")
                continue

        # 创建组合图表
        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
            .add_xaxis(name_list)
            .add_yaxis(
                "销售量",
                amount_list,
                yaxis_index=0,
                label_opts=opts.LabelOpts(is_show=True)
            )
            .add_yaxis(
                "销售额",
                pay_list,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=True)
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="销售额",
                    type_="value",
                    position="right",
                    axislabel_opts=opts.LabelOpts(formatter="{value}")
                )
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="单价",
                    type_="value",
                    position="right",
                    offset=80,
                    axislabel_opts=opts.LabelOpts(formatter="{value}")
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="商品销售数据分析",
                    subtitle="销售量/销售额/单价对比"
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross"
                ),
                legend_opts=opts.LegendOpts(pos_top="5%"),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axislabel_opts=opts.LabelOpts(rotate=-30),
                    boundary_gap=True
                ),
                yaxis_opts=opts.AxisOpts(
                    name="销售量",
                    type_="value",
                    position="left",
                    axislabel_opts=opts.LabelOpts(formatter="{value}"),
                    splitline_opts=opts.SplitLineOpts(is_show=True)
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside", range_start=0, range_end=100)
                ]
            )
        )

        # 添加折线图
        line = (
            Line()
            .add_xaxis(name_list)
            .add_yaxis(
                "单价",
                price_list,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=True),
                linestyle_opts=opts.LineStyleOpts(width=2)
            )
        )

        # 组合图表
        bar.overlap(line)
        
        result = bar.dump_options_with_quotes()
        return result

class TriView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open('./templates/tri.html', encoding='utf-8').read())

class TriDataView(BaseTriView):
    def get(self, request, *args, **kwargs):
        try:
            data = self.tri_base()
            print("Raw data from tri_base:", data)
            json_data = json.loads(data)
            print("Parsed JSON data:", json_data)
            response_data = {
                'code': 200,
                'msg': 'success',
                'data': json_data
            }
            print("Final response data:", response_data)
            return JsonResponse(response_data)
        except Exception as e:
            print(f"Error in TriDataView: {str(e)}")
            return JsonResponse({
                'code': 500,
                'msg': str(e),
                'data': None
            }) 