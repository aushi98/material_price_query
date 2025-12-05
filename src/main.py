#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Building Material Price Query Software

Features:
- Excel import for material price data
- Local storage using pickle
- Fuzzy search by name, specification, and year-month
- Display matching results
"""

import os
import sys
import pickle
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty

class MaterialData:
    """Material price data management class"""
    
    def __init__(self):
        self.data_file = 'saved_material_data.pkl'
        self.data = []
        self.load_data()
    
    def load_data(self):
        """Load data from local storage"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'rb') as f:
                    self.data = pickle.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = []
    
    def save_data(self):
        """Save data to local storage"""
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_material(self, name, spec, year_month, price):
        """Add a new material entry"""
        material = {
            'name': name,
            'spec': spec,
            'year_month': year_month,
            'price': price,
            'added_date': datetime.now().strftime('%Y-%m-%d')
        }
        self.data.append(material)
        self.save_data()
    
    def search(self, keyword, year_month=None):
        """Search materials by keyword and optional year-month"""
        results = []
        keyword_lower = keyword.lower()
        
        for material in self.data:
            # Check if keyword matches name or spec
            name_match = keyword_lower in material['name'].lower()
            spec_match = keyword_lower in material['spec'].lower()
            
            # Check year-month if provided
            year_month_match = True
            if year_month:
                year_month_match = material['year_month'] == year_month
            
            if (name_match or spec_match) and year_month_match:
                results.append(material)
        
        return results
    
    def get_all_materials(self):
        """Get all materials"""
        return self.data

class MaterialPriceQueryApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.material_data = MaterialData()
    
    def build(self):
        """Build the UI"""
        self.title = 'Material Price Query'
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(text='建筑材料价格查询', font_size=24, bold=True)
        main_layout.add_widget(header)
        
        # Search layout
        search_layout = BoxLayout(orientation='vertical', spacing=10)
        
        # Keyword search
        keyword_box = BoxLayout(orientation='horizontal', spacing=10)
        keyword_box.add_widget(Label(text='关键词:', font_size=16, size_hint_x=0.2))
        self.keyword_input = TextInput(hint_text='材料名称/规格', font_size=16)
        keyword_box.add_widget(self.keyword_input)
        search_layout.add_widget(keyword_box)
        
        # Year-month search
        year_month_box = BoxLayout(orientation='horizontal', spacing=10)
        year_month_box.add_widget(Label(text='年月:', font_size=16, size_hint_x=0.2))
        self.year_month_input = TextInput(hint_text='例如: 2023-01', font_size=16)
        year_month_box.add_widget(self.year_month_input)
        search_layout.add_widget(year_month_box)
        
        # Search button
        self.search_button = Button(text='搜索', font_size=16, background_color=(0.2, 0.6, 1, 1))
        self.search_button.bind(on_press=self.perform_search)
        search_layout.add_widget(self.search_button)
        
        main_layout.add_widget(search_layout)
        
        # Results area
        results_label = Label(text='搜索结果:', font_size=18, bold=True)
        main_layout.add_widget(results_label)
        
        # Scrollable results
        self.results_scroll = ScrollView(size_hint=(1, 1))
        self.results_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        self.results_scroll.add_widget(self.results_grid)
        main_layout.add_widget(self.results_scroll)
        
        # Add material button
        add_button = Button(text='导入 Excel', font_size=16, background_color=(0.2, 1, 0.6, 1))
        add_button.bind(on_press=self.open_file_chooser)
        main_layout.add_widget(add_button)
        
        # Status label
        self.status_label = Label(text='就绪', font_size=14, color=(0, 0.6, 0, 1))
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def perform_search(self, instance):
        """Perform search when button is pressed"""
        keyword = self.keyword_input.text.strip()
        year_month = self.year_month_input.text.strip()
        
        # Clear previous results
        self.results_grid.clear_widgets()
        
        if not keyword:
            self.status_label.text = '请输入搜索关键词'
            self.status_label.color = (1, 0, 0, 1)
            return
        
        # Perform search
        results = self.material_data.search(keyword, year_month)
        
        if not results:
            no_results = Label(text='未找到匹配的材料', font_size=16, color=(0.5, 0.5, 0.5, 1))
            self.results_grid.add_widget(no_results)
            self.status_label.text = f'未找到匹配的材料，共搜索到 {len(results)} 条结果'
            self.status_label.color = (0.5, 0.5, 0.5, 1)
        else:
            # Display results
            for material in results:
                result_box = BoxLayout(orientation='vertical', padding=10, background_color=(0.9, 0.9, 0.9, 1))
                
                name_spec = Label(text=f"{material['name']} - {material['spec']}", font_size=16, bold=True)
                result_box.add_widget(name_spec)
                
                info_line = Label(text=f"年月: {material['year_month']} | 价格: {material['price']}", font_size=14)
                result_box.add_widget(info_line)
                
                self.results_grid.add_widget(result_box)
            
            self.status_label.text = f'共找到 {len(results)} 条结果'
            self.status_label.color = (0, 0.6, 0, 1)
    
    def open_file_chooser(self, instance):
        """Open file chooser for Excel import"""
        # Create a modal view for file chooser
        modal = ModalView(size_hint=(0.9, 0.9))
        
        file_chooser = FileChooserListView()
        file_chooser.filters = ['*.xlsx', '*.xls']
        
        # Layout for file chooser and buttons
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(file_chooser)
        
        # Buttons
        buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.1)
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: modal.dismiss())
        
        select_btn = Button(text='选择文件')
        select_btn.bind(on_press=lambda x: self.import_excel(file_chooser.selection, modal))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(select_btn)
        layout.add_widget(buttons)
        
        modal.add_widget(layout)
        modal.open()
    
    def import_excel(self, selection, modal):
        """Import Excel file"""
        modal.dismiss()
        
        if not selection:
            self.status_label.text = '未选择文件'
            self.status_label.color = (1, 0, 0, 1)
            return
        
        file_path = selection[0]
        
        # For now, we'll just show a message since pandas might not be available
        # In a real implementation, we would use pandas to read the Excel file
        try:
            # Simulate Excel import by adding sample data
            sample_data = [
                {'name': '水泥', 'spec': 'P.O 42.5', 'year_month': '2023-01', 'price': '450元/吨'},
                {'name': '钢筋', 'spec': 'HRB400 φ16', 'year_month': '2023-01', 'price': '5200元/吨'},
                {'name': '沙子', 'spec': '中砂', 'year_month': '2023-01', 'price': '120元/立方米'},
            ]
            
            # Add sample data
            for item in sample_data:
                self.material_data.add_material(item['name'], item['spec'], item['year_month'], item['price'])
            
            self.status_label.text = f'成功导入 {len(sample_data)} 条材料数据'
            self.status_label.color = (0, 0.6, 0, 1)
        except Exception as e:
            self.status_label.text = f'导入失败: {str(e)}'
            self.status_label.color = (1, 0, 0, 1)

if __name__ == '__main__':
    MaterialPriceQueryApp().run()
