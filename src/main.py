from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

# Android平台特定导入
try:
    from android.permissions import request_permissions, Permission
except ImportError:
    pass

class MaterialData:
    def __init__(self):
        self.data = []
        # 本地数据文件路径，保存在软件文件夹中
        self.file_path = 'saved_material_data.pkl'
        # 共享数据文件路径 - 与TRAE生成的软件共用数据
        # 在安卓平台上，使用相对路径，与软件安装在同一文件夹
        self.shared_file_path = 'saved_material_data.pkl'
        self.load_data()
    
    def load_data(self):
        # 直接加载数据文件，位于软件安装文件夹中
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'rb') as f:
                    self.data = pickle.load(f)
            except Exception as e:
                # 如果加载失败，初始化空数据
                self.data = []
        else:
            # 如果文件不存在，初始化空数据
            self.data = []
    
    def save_data(self):
        # 保存到本地文件
        with open(self.file_path, 'wb') as f:
            pickle.dump(self.data, f)
        
        # 同时保存到共享数据文件，实现数据共用
        try:
            # 确保共享数据文件所在目录存在
            shared_dir = os.path.dirname(self.shared_file_path)
            if not os.path.exists(shared_dir):
                os.makedirs(shared_dir, exist_ok=True)
            
            # 保存到共享数据文件
            with open(self.shared_file_path, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            # 如果保存到共享文件失败，不影响本地保存
            pass
    
    def import_from_excel(self, excel_path):
        try:
            # 尝试读取Excel文件，支持不同格式
            df = pd.read_excel(excel_path, engine='openpyxl')
            new_data = []
            
            # 创建现有数据的唯一标识集合，用于去重
            existing_data_set = set()
            for item in self.data:
                unique_key = f"{item['年月']}_{item['材料名称']}_{item['材料规格']}"
                existing_data_set.add(unique_key)
            
            # 统计各种情况的数量
            total_rows = len(df)
            imported_count = 0
            duplicate_count = 0
            invalid_price_count = 0
            invalid_date_count = 0
            
            for index, row in df.iterrows():
                # 识别A列为年月，使用列索引而不是列名
                year_month = row.iloc[0]  # A列
                material_name = row.iloc[2]  # C列
                specification = row.iloc[3]  # D列
                unit = row.iloc[4]  # E列
                price = row.iloc[6]  # G列
                
                # 跳过空行
                if pd.isna(material_name) or pd.isna(specification):
                    continue
                
                # 过滤掉价格为空或非数值的行
                if pd.isna(price) or not isinstance(price, (int, float)):
                    invalid_price_count += 1
                    continue
                
                # 确保年月格式为YYYYMM
                year_month_str = str(year_month).strip()
                # 只接受YYYYMM格式
                valid_date = True
                if len(year_month_str) == 6:  # 格式：202301
                    try:
                        year_month = datetime.strptime(year_month_str, '%Y%m').strftime('%Y-%m')
                    except:
                        valid_date = False
                else:
                    valid_date = False
                
                if not valid_date:
                    invalid_date_count += 1
                    continue
                
                # 生成唯一标识，用于去重
                unique_key = f"{year_month}_{material_name}_{specification}"
                if unique_key not in existing_data_set:
                    new_data.append({
                        '年月': year_month,
                        '材料名称': str(material_name),
                        '材料规格': str(specification),
                        '单位': str(unit),
                        '除税单价': float(price)
                    })
                    existing_data_set.add(unique_key)
                    imported_count += 1
                else:
                    duplicate_count += 1
            
            self.data.extend(new_data)
            self.save_data()
            
            return True, f"成功导入 {imported_count} 条数据\n" \
                      f"跳过 {duplicate_count} 条重复数据\n" \
                      f"跳过 {invalid_price_count} 条价格无效数据\n" \
                      f"跳过 {invalid_date_count} 条日期格式无效数据\n" \
                      f"总处理行数：{total_rows}"
        except Exception as e:
            return False, f"导入失败：{str(e)}，请检查Excel文件格式是否正确，确保A列为YYYYMM格式的年月"
    
    def search(self, material_name, specification, year_month):
        results = []
        for item in self.data:
            # 模糊匹配
            name_match = material_name.lower() in str(item['材料名称']).lower() if material_name else True
            spec_match = specification.lower() in str(item['材料规格']).lower() if specification else True
            ym_match = year_month in str(item['年月']) if year_month else True
            
            if name_match and spec_match and ym_match:
                results.append(item)
        
        # 按年月排序
        results.sort(key=lambda x: x['年月'], reverse=True)
        return results
    
    def get_material_history(self, material_name, specification):
        history = []
        for item in self.data:
            if item['材料名称'] == material_name and item['材料规格'] == specification:
                history.append(item)
        # 按年月排序
        history.sort(key=lambda x: x['年月'])
        return history

class SearchScreen(Screen):
    def __init__(self, material_data, **kwargs):
        super().__init__(**kwargs)
        self.material_data = material_data
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 顶部导入区域
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # 导入Excel按钮
        import_btn = Button(
            text='导入Excel文件',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.4, 0.6, 1)
        )
        import_btn.bind(on_press=self.show_file_chooser)
        top_layout.add_widget(import_btn)
        
        # 已导入数据统计
        self.data_count_label = Label(
            text=f'已导入文件，共 {len(self.material_data.data)} 条数据',
            font_size=dp(16),
            halign='left',
            valign='middle'
        )
        self.data_count_label.size_hint_x = 2
        top_layout.add_widget(self.data_count_label)
        
        # 删除已导入数据按钮
        delete_btn = Button(
            text='删除已导入价格信息',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_press=self.delete_all_data)
        top_layout.add_widget(delete_btn)
        
        layout.add_widget(top_layout)
        
        # 第一行查询条件
        search_row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # 材料名称
        search_row1.add_widget(Label(text='材料名称:', font_size=dp(16), halign='right', valign='middle'))
        self.name_input = TextInput(hint_text='输入材料名称', font_size=dp(16), size_hint_y=None, height=dp(40))
        self.name_input.size_hint_x = 2
        search_row1.add_widget(self.name_input)
        
        # 材料规格
        search_row1.add_widget(Label(text='材料规格:', font_size=dp(16), halign='right', valign='middle'))
        self.spec_input = TextInput(hint_text='输入材料规格', font_size=dp(16), size_hint_y=None, height=dp(40))
        self.spec_input.size_hint_x = 2
        search_row1.add_widget(self.spec_input)
        
        # 查询按钮
        search_btn = Button(
            text='查询',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.6, 0.2, 1)
        )
        search_btn.bind(on_press=self.perform_search)
        search_row1.add_widget(search_btn)
        
        # 清空查询按钮
        clear_btn = Button(
            text='清空查询',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.7, 0.7, 0.7, 1)
        )
        clear_btn.bind(on_press=self.clear_search)
        search_row1.add_widget(clear_btn)
        
        layout.add_widget(search_row1)
        
        # 第二行查询条件
        search_row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # 查询月份
        search_row2.add_widget(Label(text='查询月份:', font_size=dp(16), halign='right', valign='middle'))
        self.ym_input = TextInput(hint_text='输入年月，如202310', font_size=dp(16), size_hint_y=None, height=dp(40))
        search_row2.add_widget(self.ym_input)
        
        # 查询月份按钮
        ym_btn = Button(
            text='查询月份',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.6, 0.2, 0.8, 1)
        )
        ym_btn.bind(on_press=self.search_by_month)
        search_row2.add_widget(ym_btn)
        
        layout.add_widget(search_row2)
        
        # 精确查询时间范围
        precise_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        precise_layout.add_widget(Label(text='精确查询时间范围:', font_size=dp(16), halign='right', valign='middle'))
        precise_layout.add_widget(Label(text='起始月份:', font_size=dp(16), halign='right', valign='middle'))
        self.start_ym_input = TextInput(hint_text='如201901', font_size=dp(16), size_hint_y=None, height=dp(40))
        precise_layout.add_widget(self.start_ym_input)
        
        precise_layout.add_widget(Label(text='终止月份:', font_size=dp(16), halign='right', valign='middle'))
        self.end_ym_input = TextInput(hint_text='如202510', font_size=dp(16), size_hint_y=None, height=dp(40))
        precise_layout.add_widget(self.end_ym_input)
        
        # 精确查询按钮
        precise_btn = Button(
            text='精确查询材料信息',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 0.4, 1)
        )
        precise_btn.bind(on_press=self.precise_search)
        precise_layout.add_widget(precise_btn)
        
        layout.add_widget(precise_layout)
        
        # 移除查询结果导出Excel功能
        
        # 结果显示区域
        self.results_label = Label(text='查询结果将显示在这里', font_size=dp(16), size_hint_y=None, height=dp(30))
        layout.add_widget(self.results_label)
        
        # 结果表格标题
        table_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        headers = ['材料编号', '材料名称', '材料规格', '单位', '除税单价', '年月']
        for header in headers:
            header_label = Label(
                text=header,
                font_size=dp(14),
                bold=True,
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(40),
                color=(0, 0, 0, 1)
            )
            # 使用正确的方式添加背景色，不绑定属性
            with header_label.canvas.before:
                Color(0.8, 0.8, 0.8, 1)
                Rectangle(pos=header_label.pos, size=header_label.size)
            # 手动更新背景位置和大小
            header_label.bind(
                pos=lambda instance, value: instance.canvas.before.clear() or instance.canvas.before.add(Color(0.8, 0.8, 0.8, 1)) or instance.canvas.before.add(Rectangle(pos=instance.pos, size=instance.size)),
                size=lambda instance, value: instance.canvas.before.clear() or instance.canvas.before.add(Color(0.8, 0.8, 0.8, 1)) or instance.canvas.before.add(Rectangle(pos=instance.pos, size=instance.size))
            )
            table_header.add_widget(header_label)
        layout.add_widget(table_header)
        
        # 结果列表
        self.results_scroll = ScrollView()
        self.results_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_scroll.add_widget(self.results_layout)
        layout.add_widget(self.results_scroll)
        
        self.add_widget(layout)
    
    def perform_search(self, instance):
        material_name = self.name_input.text.strip()
        specification = self.spec_input.text.strip()
        year_month = self.ym_input.text.strip()
        
        results = self.material_data.search(material_name, specification, year_month)
        self.display_results(results)
    
    def display_results(self, results):
        # 保存当前结果，用于导出
        self.current_results = results
        
        # 清空之前的结果
        self.results_layout.clear_widgets()
        
        if not results:
            self.results_label.text = f'未找到匹配的数据，共0条'
            return
        
        self.results_label.text = f'找到 {len(results)} 条匹配数据'
        
        for index, result in enumerate(results):
            # 结果行
            result_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
            
            # 材料编号（这里用索引代替）
            id_label = Label(
                text=str(index + 1),
                font_size=dp(14),
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(40)
            )
            result_row.add_widget(id_label)
            
            # 材料名称
            name_label = Label(
                text=str(result['材料名称']),
                font_size=dp(14),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(40)
            )
            name_label.size_hint_x = 2
            result_row.add_widget(name_label)
            
            # 材料规格
            spec_label = Label(
                text=str(result['材料规格']),
                font_size=dp(14),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(40)
            )
            spec_label.size_hint_x = 2
            result_row.add_widget(spec_label)
            
            # 单位
            unit_label = Label(
                text=str(result['单位']),
                font_size=dp(14),
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(40)
            )
            result_row.add_widget(unit_label)
            
            # 除税单价
            price_label = Label(
                text=f"￥{result['除税单价']}",
                font_size=dp(14),
                halign='right',
                valign='middle',
                size_hint_y=None,
                height=dp(40)
            )
            result_row.add_widget(price_label)
            
            # 年月
            ym_label = Label(
                text=str(result['年月']),
                font_size=dp(14),
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(40)
            )
            result_row.add_widget(ym_label)
            
            # 添加点击事件
            result_row.bind(on_touch_down=lambda instance, touch, res=result: self.on_result_touch(instance, touch, res))
            
            # 交替行背景色
            if index % 2 == 0:
                with result_row.canvas.before:
                    Color(0.95, 0.95, 0.95, 1)
                    Rectangle(pos=result_row.pos, size=result_row.size)
                # 手动更新背景位置和大小
                result_row.bind(
                    pos=lambda instance, value: instance.canvas.before.clear() or instance.canvas.before.add(Color(0.95, 0.95, 0.95, 1)) or instance.canvas.before.add(Rectangle(pos=instance.pos, size=instance.size)),
                    size=lambda instance, value: instance.canvas.before.clear() or instance.canvas.before.add(Color(0.95, 0.95, 0.95, 1)) or instance.canvas.before.add(Rectangle(pos=instance.pos, size=instance.size))
                )
            
            self.results_layout.add_widget(result_row)
    
    def on_result_touch(self, instance, touch, result):
        # 点击结果行时显示详情
        if instance.collide_point(*touch.pos):
            self.show_detail(result)
    
    def delete_all_data(self, instance):
        # 确认删除
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text='确定要删除所有已导入的数据吗？', font_size=dp(16)))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10))
        cancel_btn = Button(text='取消', font_size=dp(16))
        confirm_btn = Button(text='确定', font_size=dp(16), background_color=(0.8, 0.2, 0.2, 1))
        
        popup = Popup(title='确认删除', content=content, size_hint=(0.8, 0.4))
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.confirm_delete(popup))
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(confirm_btn)
        content.add_widget(btn_box)
        
        popup.open()
    
    def confirm_delete(self, popup):
        # 执行删除操作
        self.material_data.data = []
        self.material_data.save_data()
        self.data_count_label.text = f'已导入文件，共 {len(self.material_data.data)} 条数据'
        self.results_layout.clear_widgets()
        self.results_label.text = '查询结果将显示在这里'
        popup.dismiss()
        
        # 显示删除成功提示
        success_popup = Popup(
            title='删除成功',
            content=Label(text='所有数据已成功删除', font_size=dp(16)),
            size_hint=(0.8, 0.4)
        )
        success_popup.open()
    
    def clear_search(self, instance):
        # 清空所有查询条件
        self.name_input.text = ''
        self.spec_input.text = ''
        self.ym_input.text = ''
        self.start_ym_input.text = ''
        self.end_ym_input.text = ''
        
        # 清空结果
        self.results_layout.clear_widgets()
        self.results_label.text = '查询结果将显示在这里'
    
    def search_by_month(self, instance):
        # 按月份查询
        year_month = self.ym_input.text.strip()
        if not year_month:
            self.results_label.text = '请输入查询月份'
            return
        
        results = self.material_data.search('', '', year_month)
        self.display_results(results)
    
    def precise_search(self, instance):
        # 精确查询时间范围
        start_ym = self.start_ym_input.text.strip()
        end_ym = self.end_ym_input.text.strip()
        
        if not start_ym or not end_ym:
            self.results_label.text = '请输入完整的时间范围'
            return
        
        # 验证年月格式
        try:
            start_date = datetime.strptime(start_ym, '%Y%m')
            end_date = datetime.strptime(end_ym, '%Y%m')
        except ValueError:
            self.results_label.text = '年月格式错误，请使用YYYYMM格式'
            return
        
        # 执行时间范围查询
        results = []
        for item in self.material_data.data:
            # 转换年月格式
            item_ym = str(item['年月']).replace('-', '')
            try:
                item_date = datetime.strptime(item_ym, '%Y%m')
                if start_date <= item_date <= end_date:
                    results.append(item)
            except:
                continue
        
        self.display_results(results)
    
    def show_file_chooser(self, instance):
        filechooser = FileChooserListView()
        filechooser.filters = ["*.xlsx", "*.xls"]
        
        box = BoxLayout(orientation='vertical')
        box.add_widget(filechooser)
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(50))
        cancel_btn = Button(text='取消')
        select_btn = Button(text='选择')
        
        popup = Popup(title='选择Excel文件', content=box, size_hint=(0.9, 0.9))
        
        cancel_btn.bind(on_press=popup.dismiss)
        select_btn.bind(on_press=lambda x: self.import_excel(filechooser.path, filechooser.selection, popup))
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(select_btn)
        box.add_widget(btn_box)
        
        popup.open()
    
    def import_excel(self, path, selection, popup):
        if not selection:
            popup.dismiss()
            return
        
        file_path = selection[0]
        success, message = self.material_data.import_from_excel(file_path)
        
        popup.dismiss()
        
        # 更新数据统计标签
        self.data_count_label.text = f'已导入文件，共 {len(self.material_data.data)} 条数据'
        
        # 显示导入结果
        result_popup = Popup(
            title='导入结果',
            content=Label(text=message, font_size=dp(16)),
            size_hint=(0.8, 0.4)
        )
        result_popup.open()
    
    def show_detail(self, result):
        # 切换到详情页面
        app = App.get_running_app()
        app.root.current = 'detail'
        app.root.get_screen('detail').update_detail(result, self.material_data)

class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 返回按钮
        back_btn = Button(text='返回', font_size=dp(18), size_hint_y=None, height=dp(50))
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        # 详情信息
        self.detail_info = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        layout.add_widget(self.detail_info)
        
        # 历史价格列表
        self.history_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        layout.add_widget(self.history_layout)
        
        self.add_widget(layout)
    
    def update_detail(self, result, material_data):
        # 清空之前的内容
        self.detail_info.clear_widgets()
        self.history_layout.clear_widgets()
        
        # 显示详细信息
        self.detail_info.add_widget(Label(text='年月:', font_size=dp(16), bold=True))
        self.detail_info.add_widget(Label(text=str(result['年月']), font_size=dp(16)))
        
        self.detail_info.add_widget(Label(text='材料名称:', font_size=dp(16), bold=True))
        self.detail_info.add_widget(Label(text=str(result['材料名称']), font_size=dp(16)))
        
        self.detail_info.add_widget(Label(text='材料规格:', font_size=dp(16), bold=True))
        self.detail_info.add_widget(Label(text=str(result['材料规格']), font_size=dp(16)))
        
        self.detail_info.add_widget(Label(text='单位:', font_size=dp(16), bold=True))
        self.detail_info.add_widget(Label(text=str(result['单位']), font_size=dp(16)))
        
        self.detail_info.add_widget(Label(text='除税单价:', font_size=dp(16), bold=True))
        self.detail_info.add_widget(Label(text=f"￥{result['除税单价']}", font_size=dp(16)))
        
        # 显示历史价格列表
        self.show_history(result, material_data)
    
    def show_history(self, result, material_data):
        # 获取该材料的历史数据
        history = material_data.get_material_history(result['材料名称'], result['材料规格'])
        
        if not history:
            self.history_layout.add_widget(Label(text='没有历史价格数据', font_size=dp(16)))
            return
        
        # 按年月排序
        history.sort(key=lambda x: x['年月'], reverse=True)
        
        # 获取最近12个月的数据
        recent_history = history[:12]  # 显示最近12条记录
        
        # 显示历史价格标题
        self.history_layout.add_widget(Label(text='最近12个月价格记录:', font_size=dp(16), bold=True))
        
        # 使用滚动视图显示历史价格
        history_scroll = ScrollView()
        history_list = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        history_list.bind(minimum_height=history_list.setter('height'))
        
        # 添加表头
        history_list.add_widget(Label(text='年月', font_size=dp(14), bold=True))
        history_list.add_widget(Label(text='除税单价 (元)', font_size=dp(14), bold=True))
        
        # 添加历史价格数据
        for item in recent_history:
            history_list.add_widget(Label(text=str(item['年月']), font_size=dp(14)))
            history_list.add_widget(Label(text=f"￥{item['除税单价']}", font_size=dp(14)))
        
        history_scroll.add_widget(history_list)
        self.history_layout.add_widget(history_scroll)
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'search'

class MaterialPriceApp(App):
    def build(self):
        # 请求Android权限
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.MANAGE_EXTERNAL_STORAGE
            ])
        except ImportError:
            pass
        
        self.material_data = MaterialData()
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加搜索屏幕
        search_screen = SearchScreen(self.material_data, name='search')
        sm.add_widget(search_screen)
        
        # 添加详情屏幕
        detail_screen = DetailScreen(name='detail')
        sm.add_widget(detail_screen)
        
        return sm

if __name__ == '__main__':
    MaterialPriceApp().run()
