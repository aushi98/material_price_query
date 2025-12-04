from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 50
        
        self.add_widget(Label(text='建筑材料价格查询', font_size=30, size_hint_y=0.3))
        self.add_widget(Label(text='这是一个简单的 Kivy 应用程序', font_size=20, size_hint_y=0.2))
        
        button = Button(text='点击我', size_hint_y=0.2, font_size=20)
        button.bind(on_press=self.on_button_click)
        self.add_widget(button)
        
        self.result_label = Label(text='', size_hint_y=0.3, font_size=20)
        self.add_widget(self.result_label)
    
    def on_button_click(self, instance):
        self.result_label.text = '按钮被点击了！'

class MaterialPriceApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    MaterialPriceApp().run()
