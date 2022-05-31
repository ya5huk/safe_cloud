from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from DBClient import DBClient
from DBObjects import DBFile
from IconGrabber import IconGrabber
import os

ig = IconGrabber('images/extension_icons/')
db = DBClient('private/firestore_json.json')
class LoginWindow(Screen):
    pass

class RegisterWindow(Screen):
    pass

class CloudWindow(Screen):
    def __init__(self, **kw):
        super(CloudWindow, self).__init__(**kw)
        Window.bind(on_drop_file=self.file_dropped)
        self.files_counter = 0

    def file_dropped(self, window, filename, x, y, *args):  
        # Frontend
        filename = filename.decode()
        showed_filename = self.prepare_filename(filename)
        bl = BoxLayout(spacing=5, size_hint=(.1,.2), orientation="vertical")
        bl.add_widget(AsyncImage(source=ig.grab_filepath(filename), keep_ratio=True, size_hint=(1,.5)))
        bl.add_widget(Label(font_name="lbrite", text=showed_filename, halign="center", valign="top", text_size = (bl.size[0], None),size_hint = (1, .5)))
        self.ids.files_stack.add_widget(bl)
        
        self.files_counter += 1

        # Backend

        with open(filename, 'rb') as f:
            fcontent = f.read()

        db.add_file(DBFile(False, os.path.basename(filename), fcontent))

    @staticmethod
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
        
class WindowManager(ScreenManager):
    pass


class SafeCloudApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Safe Cloud"
        super().__init__(**kwargs)

    # def build(self):
    #     self.root = Builder.load_file("safecloud.kv")

if __name__ == '__main__':
    SafeCloudApp().run()