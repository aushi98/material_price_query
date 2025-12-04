from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text='Hello World!', font_size=30))
        layout.add_widget(Button(text='Click Me!', font_size=20))
        return layout

if __name__ == '__main__':
    TestApp().run()
