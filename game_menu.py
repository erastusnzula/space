from kivy.properties import ObjectProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen


class GameMenuWidget(Screen):
    screen_title_object = ObjectProperty()

    def on_touch_down(self, touch):
        if self.opacity == 0:
            return False
        return super(Screen, self).on_touch_down(touch)


class WelcomeWidget(Screen):
    screen_title_object = ObjectProperty()

    def on_touch_down(self, touch):
        if self.opacity == 0:
            return False
        return super(Screen, self).on_touch_down(touch)
