import asyncio

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout


class ChatLog(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.row_force_default=True
        self.row_default_height=40
        self.bind(minimum_height=self.setter('height'))

    def add_message(self, message):
        self.add_widget(Label(text=message, size_hint_y=None, height=40))

class ChatLayout(FloatLayout):
    send_button = ObjectProperty(None)
    user_input = ObjectProperty(None)
    chat_log = ObjectProperty(None)

    def __init__(self, requests, **kwargs):
        super().__init__(**kwargs)
        self.requests = requests
        self.send_button.bind(on_press=self.send_message)

    def send_message(self, instance) -> None:
        message = self.user_input.text
        self.requests.put_nowait(message)
        self.user_input.text = ''
        print('Message sent: ', message)




class ChatApp(App):
    def __init__(self, requests, **kwargs):
        super().__init__(**kwargs)
        self.requests = requests

    def build(self):
        layout = ChatLayout(requests=self.requests)
        Window.size = (400, 600)
        return layout


if __name__ == '__main__':
    requests = asyncio.Queue()
    app = ChatApp(requests, title='Chat')
    app.run()