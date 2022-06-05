from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from CloudServer import CloudServer, CloudClient
from DBObjects import DBFile
from IconGrabber import IconGrabber
import os

ig = IconGrabber('images/extension_icons/')
cc = CloudClient('127.0.0.1', 8081)
class LoginWindow(Screen):
    pass

class RegisterWindow(Screen):
    pass

class FileIconRepr(BoxLayout): 
    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        
        # Calculation 0 + (heading_y + choice_to_father)/window_y (cuz it's rational)
        self.pos_hint = (.5, .5)

        showed_filename = prepare_filename(filepath)
        file_icon = AsyncImage(source=ig.grab_filepath(filepath), keep_ratio=True, size_hint=(1,.5))
        file_label = Label(font_name="lbrite", text=showed_filename, halign="center", valign="top", text_size = (self.size[0], None),size_hint = (1, .5))

        self.add_widget(file_icon)
        self.add_widget(file_label)

        with self.canvas.before:
            Color(.20, .06, .31, 1)
            self.rect = Rectangle(
                size=self.size,
                pos=self.pos
            )
   

    def on_touch_move(self, touch):
        print('move')

    def on_touch_up(self, touch):
        print('touch_up')

class CloudWindow(Screen):
    def __init__(self, **kw):
        super(CloudWindow, self).__init__(**kw)
        Window.bind(on_drop_file=self.file_dropped)
        
        self.files_counter = 0

    def file_dropped(self, window, filename, x, y, *args):  
        # Frontend
        filename = filename.decode()
        
        
        file_repr = FileIconRepr(filename, spacing=5, size_hint=(.1,.2), orientation="vertical")
        #self.ids.files_stack.add_widget(file_repr)
        
        self.ids.files_stack.add_widget(AnchorLayout(anchor_x="left", anchor_y="top").add_widget(file_repr))
        

        self.files_counter += 1

        # Backend

        with open(filename, 'rb') as f:
            fcontent = f.read()

        cc.send_file(False, os.path.basename(filename), fcontent)
        
class WindowManager(ScreenManager):
    pass


class SafeCloudApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Safe Cloud"
        super().__init__(**kwargs)

    # def build(self):
    #     self.root = Builder.load_file("safecloud.kv")

def prepare_filename(filename: str):
        # Function for shortening too long filenames!
        # Allowing max 20 chars
        # if more -> 17 - len(ext) chars are showed
        orig_filename = os.path.basename(filename)
        if len(orig_filename) > 20:
            ext = orig_filename.split('.')[-1]
            showed_filename = orig_filename[:20-3-len(ext)] + '...' + ext
            return showed_filename
        return orig_filename

if __name__ == '__main__':
    SafeCloudApp().run()