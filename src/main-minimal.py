from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

class MaterialData:
    def __init__(self):
        self.data = []
        self.file_path = 'saved_material_data.pkl'
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'rb') as f:
                    self.data = pickle.load(f)
            except Exception as e:
                self.data = []
        else:
            self.data = []
    
    def save_data(self):
        with open(self.file_path, 'wb') as f:
            pickle.dump(self.data, f)
    
    def import_from_excel(self, excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            new_data = []
            
            for index, row in df.iterrows():
                year_month = row.iloc[0]
                material_name = row.iloc[2]
                specification = row.iloc[3]
                unit = row.iloc[4]
                price = row.iloc[6]
                
                new_data.append({
                    '材料编号': index + 1,
                    '材料名称': material_name,
                    '材料规格': specification,
                    '单位': unit,
                    '除税单价': price,
                    '年月': year_month
                })
            
            self.data.extend(new_data)
            self.save_data()
            return True, f'成功导入 {len(new_data)} 条数据'
        except Exception as e:
            return False, f'导入失败：{str(e)}'
    
    def search(self, material_name, specification, year_month):
        results = []
        for item in self.data:
            name_match = material_name.lower() in str(item['材料名称']).lower() if material_name else True
            spec_match = specification.lower() in str(item['材料规格']).lower() if specification else True
            ym_match = year_month in str(item['年月']) if year_month else True
            
            if name_match and spec_match and ym_match:
                results.append(item)
        
        results.sort(key=lambda x: x['年月'], reverse=True)
        return results

class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 搜索表单
        search_form = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.name_input = TextInput(hint_text='材料名称', size_hint_y=None, height=40)
        self.spec_input = TextInput(hint_text='材料规格', size_hint_y=None, height=40)
        self.ym_input = TextInput(hint_text='年月', size_hint_y=None, height=40)
        
        search_button = Button(text='搜索', size_hint_y=None, height=40)
        search_button.bind(on_press=self.perform_search)
        
        search_form.add_widget(self.name_input)
        search_form.add_widget(self.spec_input)
        search_form.add_widget(self.ym_input)
        search_form.add_widget(search_button)
        
        # 结果显示
        self.results_label = Label(text='未找到匹配的数据')
        
        layout.add_widget(search_form)
        layout.add_widget(self.results_label)
        
        self.add_widget(layout)
    
    def perform_search(self, instance):
        material_name = self.name_input.text.strip()
        specification = self.spec_input.text.strip()
        year_month = self.ym_input.text.strip()
        
        app = App.get_running_app()
        results = app.material_data.search(material_name, specification, year_month)
        self.results_label.text = f'找到 {len(results)} 条匹配数据'

class MaterialPriceApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.material_data = MaterialData()
    
    def build(self):
        sm = ScreenManager()
        search_screen = SearchScreen(name='search')
        sm.add_widget(search_screen)
        return sm

if __name__ == '__main__':
    MaterialPriceApp().run()
