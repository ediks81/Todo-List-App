import json
from hashlib import sha256
from kivymd.app import MDApp
from kivy.factory import Factory
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivymd.uix.navigationbar import MDNavigationItem
from kivymd.toast import toast
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from plyer import stt

Window.softinput_mode = 'pan'#below_target

class NavigationItemTemplate(MDNavigationItem):
   icon, text = StringProperty(), StringProperty()

class Credentials(MDTextField):
   hint_text = StringProperty()
   def reset(self):
      self.text = ''

class RegisterScreen(MDScreen):
   def register_user(self, username, password):
      if len(username) and len(password):
         try:
            with open('users.json', 'r') as file:
               data = json.load(file)
               users, tasks = data['users'], data['tasks']
         except FileNotFoundError:
            users = {}
            tasks = {'personal': {}, 'work': {}, 'study': {}, 'shopping': {}}
         with open('users.json', 'w') as file:
            users[username] = sha256(password.encode()).hexdigest()
            for i in tasks:
               tasks[i][username] = []
            json.dump({'users': users, 'tasks': tasks}, file, indent = 3)
            self.ids.new_username.text = ''
         toast('User Registered Successfully')

class Tab(MDScreen):
   scr_name = StringProperty()
   def start_listening(self):
      if stt.listening:
         stt.stop()
      stt.start()
   def stop_listening(self):
      stt.stop()
      return ' '.join(stt.partial_results)

class InputBox(MDTextField):
   def reset(self):
      self.text = ''

class Confirm(MDDialog):
   def __init__(self, activity, **kwargs):
      super().__init__(**kwargs)
      self.activity = activity

class NewActivity(MDBoxLayout):
   content = StringProperty()

class Activities(MDStackLayout):
   def add_item(self, content):
      if len(content):
         self.add_widget(Factory.NewActivity(content = content))
   def delete_item(self, activity):
      self.remove_widget(activity)

class todo_list(MDApp):
   def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.screens = ['personal', 'work', 'study', 'shopping']
   def check_login(self, username, password):
      if len(username) and len(password):
         try:
            with open("users.json", "r") as file:
               data = json.load(file)
               users = data['users']
            if username in users and users[username] == sha256(password.encode()).hexdigest():
               toast('Login Successful')
               self.user = username
               self.root.current = 'main_interface'
               self.widget_map = self.root.ids
               tasks = data['tasks']
               for i in tasks:
                  for j in tasks[i][username]:
                     self.widget_map[i].ids.activities.add_item(j)
            else:
               toast('Invalid Username or Password')
         except FileNotFoundError:
            toast('Invalid Username or Password')
   def save_widget(self, content, tab):
      if len(content):
         with open("users.json", "r") as file:
            data = json.load(file)
            tasks = data['tasks']
            tasks[tab][self.user] += [content]
         with open("users.json", "w") as file:
            json.dump({'users': data['users'], 'tasks': tasks}, file, indent=3)
   def on_switch_tabs(self, next_scr):
      if self.screens.index(next_scr) > self.screens.index(self.root.ids.tabs.current):
         self.root.ids.tabs.current = next_scr
         self.root.ids.tabs.transition.direction = 'left'
      else:
         self.root.ids.tabs.current = next_scr
         self.root.ids.tabs.transition.direction = 'right'
   def show_alert(self, activity):
      Confirm(activity = activity).open()
   def delete_item(self, activity):
      self.widget_map[self.root.ids.tabs.current].ids.activities.delete_item(activity)
      with open("users.json", "r") as file:
         data = json.load(file)
         tasks = data['tasks']
      with open("users.json", "w") as file:
         index = tasks[self.root.ids.tabs.current][self.user].index(activity.ids.activity.text)
         del tasks[self.root.ids.tabs.current][self.user][index]
         json.dump({'users': data['users'], 'tasks': tasks}, file, indent = 3)

if __name__ == '__main__':
   todo_list().run()
