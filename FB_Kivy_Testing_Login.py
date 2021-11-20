from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.font_definitions import theme_font_styles
from firebase import firebase
import pandas as pd
import json
import requests

firebase = firebase.FirebaseApplication('https://cis9590-355fe-default-rtdb.firebaseio.com/', None)

help_str = '''
ScreenManager:
    WelcomeScreen:
    MainScreen:
    LoginScreen:
    SignupScreen:

<WelcomeScreen>:

    name:'welcomescreen'

    canvas.before:
        Color:
            rgba: 0.3,0.6,0.6,0.3
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        size: root.width, root.height
        padding: 20
        spacing: 30

        Image:
            source: 'app.png'
            size_hint: (0.5,0.5)
            pos_hint : {'center_x':0.5,'center_y':1.5}

    MDLabel:
        text:'HeartCatcher App'
        font_style:'H1'
        font_size : 50
        halign:'center'
        pos_hint: {'center_y':0.9}
        color: [40/255,65/255,100/255,1]

    MDRaisedButton:
        text:'Login'
        pos_hint : {'center_x':0.4,'center_y':0.1}
        size_hint: (0.15,0.1)
        on_press: 
            root.manager.current = 'loginscreen'
            root.manager.transition.direction = 'left'
    MDRaisedButton:
        text:'Signup'
        pos_hint : {'center_x':0.6,'center_y':0.1}
        size_hint: (0.15,0.1)
        on_press:
            root.manager.current = 'signupscreen'
            root.manager.transition.direction = 'left'
        
<LoginScreen>:
    name:'loginscreen'

    canvas.before:
        Color:
            rgba: 0.3,0.6,0.6,0.3
        Rectangle:
            pos: self.pos
            size: self.size

    MDLabel:
        text:'Login'
        font_style:'H2'
        halign:'center'
        pos_hint: {'center_y':0.9}

    MDTextField:
        
        id:login_email
        pos_hint: {'center_y':0.6,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Email'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"
    MDTextField:
        id:login_password
        pos_hint: {'center_y':0.4,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Password'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDRaisedButton:
        text:'Login'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press:
            app.login()
            app.username_changer() 
            
        

    MDTextButton:
        text: 'Create an account'
        pos_hint: {'center_x':0.5,'center_y':0.1}
        on_press:
            root.manager.current = 'signupscreen'
            root.manager.transition.direction = 'up'


<SignupScreen>:
    name:'signupscreen'

    canvas.before:
        Color:
            rgba: 0.3,0.6,0.6,0.3
        Rectangle:
            pos: self.pos
            size: self.size

    MDLabel:
        text:'Signup'
        font_style:'H2'
        halign:'center'
        pos_hint: {'center_y':0.9}

    MDTextField:
        id:signup_email
        pos_hint: {'center_y':0.6,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Email'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"
    MDTextField:
        id:signup_username
        pos_hint: {'center_y':0.75,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Username'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
    MDTextField:
        id:signup_password
        pos_hint: {'center_y':0.4,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Password'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"
    MDRaisedButton:
        text:'Signup'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press: app.signup()

    MDTextButton:
        text: 'Already have an account'
        pos_hint: {'center_x':0.5,'center_y':0.1}
        on_press:
            root.manager.current = 'loginscreen'
            root.manager.transition.direction = 'down'

    

    
<MainScreen>:
    name: 'mainscreen'

    canvas.before:
        Color:
            rgba: 0.3,0.6,0.6,0.3
        Rectangle:
            pos: self.pos
            size: self.size

    MDTextField:
        id:age
        pos_hint: {'center_y':0.8,'center_x':0.5}
        size_hint : (0.4,0.1)
        hint_text: 'How old are you?'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:work
        pos_hint: {'center_y':0.6,'center_x':0.5}
        size_hint : (0.4,0.1)
        hint_text: 'Have you ever worked? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:heartd
        pos_hint: {'center_y':0.4,'center_x':0.5}
        size_hint : (0.4,0.1)
        hint_text: 'Do you have any heart disease? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDRaisedButton:
        text:'Submit'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press: app.biosubmit()

    MDLabel:
        id:biomet_info
        text:'Hello Main'
        pos_hint: {'center_x':0.5,'center_y':0.9}
        font_size : 20
        color: [40/255,65/255,100/255,1]
        font_style:'H3'
        halign:'center'

<ResultScreen>:
    name: 'resultscreen'

    canvas.before:
        Color:
            rgba: 0.3,0.6,0.6,0.3
        Rectangle:
            pos: self.pos
            size: self.size

    MDLabel:
        text:'Prediction Model Result'
        font_style:'H2'
        halign:'center'
        pos_hint: {'center_y':0.9}

'''


class WelcomeScreen(Screen):
    pass
class MainScreen(Screen):
    pass
class LoginScreen(Screen):
    pass
class SignupScreen(Screen):
    pass
class ResultScreen(Screen):
    pass

sm = ScreenManager()
sm.add_widget(WelcomeScreen(name = 'loginscreen'))
sm.add_widget(MainScreen(name = 'mainscreen'))
sm.add_widget(LoginScreen(name = 'loginscreen'))
sm.add_widget(SignupScreen(name = 'signupscreen'))
sm.add_widget(ResultScreen(name = 'resultscreen'))

class LoginApp(MDApp):

    def build(self):
        self.strng = Builder.load_string(help_str)
        self.url  = "https://cis9590-355fe-default-rtdb.firebaseio.com/cis9590-355fe-default-rtdb/Users.json"
        self.bioUrl  = "https://cis9590-355fe-default-rtdb.firebaseio.com/cis9590-355fe-default-rtdb/Biometrics.json"
        
        return self.strng

    def signup(self):
        signupEmail = self.strng.get_screen('signupscreen').ids.signup_email.text
        signupPassword = self.strng.get_screen('signupscreen').ids.signup_password.text
        signupUsername = self.strng.get_screen('signupscreen').ids.signup_username.text
        if signupEmail.split() == [] or signupPassword.split() == [] or signupUsername.split() == []:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Input',text = 'Please Enter a valid Input',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        if len(signupUsername.split())>1:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Username',text = 'Please enter username without space',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        else:
            print(signupEmail,signupPassword)
            signup_info = str({f'\"{signupEmail}\":{{"Password":\"{signupPassword}\","Username":\"{signupUsername}\"}}'})
            signup_info = signup_info.replace(".","-")
            signup_info = signup_info.replace("\'","")
            to_database = json.loads(signup_info)
            print((to_database))
            requests.patch(url = self.url,json = to_database)
            self.strng.get_screen('loginscreen').manager.current = 'loginscreen'
    auth = '7CWlh4kuYDiKSsKoD1quK1tY5BW08BxpjXIgLc28'

    def login(self):
        loginEmail = self.strng.get_screen('loginscreen').ids.login_email.text
        loginPassword = self.strng.get_screen('loginscreen').ids.login_password.text

        self.login_check = False
        supported_loginEmail = loginEmail.replace('.','-')
        supported_loginPassword = loginPassword.replace('.','-')
        request  = requests.get(self.url+'?auth='+self.auth)
        data = request.json()
        emails= set()
        for key,value in data.items():
            emails.add(key)
        if supported_loginEmail in emails and supported_loginPassword == data[supported_loginEmail]['Password']:
            self.username = data[supported_loginEmail]['Username']
            self.login_check=True
            self.strng.get_screen('mainscreen').manager.current = 'mainscreen'
        else:
            print("user no longer exists")
    def close_username_dialog(self,obj):
        self.dialog.dismiss()
    def username_changer(self):
        if self.login_check:
            self.strng.get_screen('mainscreen').ids.biomet_info.text = f"Biometric Input"

    def biosubmit(self):
        bio_age = self.strng.get_screen('mainscreen').ids.age.text
        bio_work = self.strng.get_screen('mainscreen').ids.work.text
        bio_heartd = self.strng.get_screen('mainscreen').ids.heartd.text
        if bio_age.split() == [] or bio_work.split() == [] or bio_heartd.split() == []:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Input',text = 'Please Enter a valid Input',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        if len(bio_heartd.split())>1:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Username',text = 'Please enter without space',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        else:
            print(bio_age,bio_work,bio_heartd)
            
            bio_info = {
                        'Age': bio_age,
                        'Employment': bio_work,
                        'HeartDisease': bio_heartd
                        }
            
##          str({f'\"{signupEmail}\":{{"Age":\"{bio_age}\","Employment":\"{bio_work}\","HeartDisease":\"{bio_heartd}\"}}'})
            ###str({f'\{{"Age":\"{bio_age}\","Password":\"{bio_work}\","Username":\"{bio_heartd}\"}}'})

            firebase.post('cis9590-355fe-default-rtdb/Biometrics', bio_info)
            stroke_data = firebase.get('cis9590-355fe-default-rtdb/Stroke_Data/','')
            stroke_data_df = pd.DataFrame(stroke_data)
            print(stroke_data_df)
            #stroke_data_df = pd.read_json(stroke_data)
            #print(stroke_data_df)
            #print(stroke_data)
##            to_database = json.loads(bio_info)
##            print((to_database))
##            requests.patch(url = self.bioUrl,json = to_database)
            self.strng.get_screen('resultscreen').manager.current = 'resultscreen'
    auth = '7CWlh4kuYDiKSsKoD1quK1tY5BW08BxpjXIgLc28'


LoginApp().run()