import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup


class Widgets(Widget):
    def btn(self):
        show_popup()

class P(FloatLayout):
    pass


class MyApp(App):
    def build(self):
        return Widgets()


def show_popup():
    show = P()

    popupWindow = Popup(title="Log out", content=show, size_hint=(None,None),size=(400,400))

    popupWindow.open()


if __name__ == "__main__":
    MyApp().run()
  
    
    
My.kv
    <Widgets>:
        Button:
            text: "Close"
            on_release: root.btn()

    <P>:
        Label:
            text: "You have logged out"
            size_hint: 0.6, 0.2
            pos_hint: {"x":0.2, "top":1}

        Button:
            text: "Back to login page"
            size_hint: 0.8, 0.2
            pos_hint: {"x":0.1, "y":0.1}
