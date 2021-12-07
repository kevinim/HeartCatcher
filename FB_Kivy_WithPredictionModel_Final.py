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
from kivy.uix.recycleview import RecycleView
from kivymd.font_definitions import theme_font_styles
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty, BoundedNumericProperty
from firebase import firebase
import json
import requests

import pandas as pd
import numpy as np
from numpy import percentile
from imblearn.over_sampling import SMOTE
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split

#df = pd.read_csv('healthcare-dataset-stroke-data.csv')
firebase = firebase.FirebaseApplication('https://cis9590-355fe-default-rtdb.firebaseio.com/', None)

###stroke_data = firebase.get('cis9590-355fe-default-rtdb/Stroke_Data/','')
###df = pd.DataFrame(stroke_data)
###df['bmi'] = df['bmi'].astype(float)
###df['avg_glucose_level'] = df['avg_glucose_level'].astype(float)
###df['age'] = pd.to_numeric(df['age'],errors='coerce')
stroke_data = firebase.get('cis9590-355fe-default-rtdb/Stroke_Data/','')
df = pd.DataFrame(stroke_data)
##pre-processing
#replace missing values in bmi column using using mean() imputation
df['bmi'] = df['bmi'].replace("N/A", np.nan)
df['bmi'] = df['bmi'].astype(float)
df['bmi'].fillna(df['bmi'].mean(),inplace=True)
#drop rows with gender=other
df.drop(df.index[df["gender"]=="Other"], inplace=True)
#replace "children" values with "never_worked"
df["work_type"] = df["work_type"].replace(["children"], "Never_worked")
#rename the residence_type for consistency
df.rename(columns = {"Residence_type": "residence_type"}, inplace=True)
#change age column into integer from float
df["age"] = df["age"].astype("int")
#define categorical variables
cols = ["stroke", "gender", "hypertension", "heart_disease", "ever_married", "work_type", "residence_type", "smoking_status"]
df[cols] = df[cols].astype("category")
#drop id column
df.drop(["id"], axis="columns", inplace=True)
#creating a function to remove outliers
def remove_outliers(data):
    ##calculate interquartile range
    q25 = np.percentile(data, 25)
    q75 = np.percentile(data, 75)
    iqr = q75 - q25
    
    ##calculate lower and upper limits
    low_lim = q25 - (1.5 * iqr)
    up_lim = q75 + (1.5 * iqr)
    
    ##identify and remove outliers
    outliers = []
    for x in data:
        if x < low_lim:
            x = low_lim
            outliers.append(x)
        elif x > up_lim:
            x = up_lim
            outliers.append(x)
        else:
            outliers.append(x)
    return outliers
#removing outliers
df["bmi"] = remove_outliers(df['bmi'])
df["avg_glucose_level"] = remove_outliers(df["avg_glucose_level"])
#get dummies and identify predictor and outcome variables
predictors = df.drop(columns = ["stroke"])
outcome = "stroke"
X = pd.get_dummies(predictors, drop_first=True)
y = df[outcome]
##model building
#split validation
train_X, valid_X, train_y, valid_y= train_test_split(X, y, test_size=0.30, random_state=1)
#oversampling our train and test set
smote = SMOTE()
train_X, train_y = smote.fit_resample(train_X, train_y)
#creating a function to choose best features
import statsmodels.api as smd
def forward_selection(data, target, significance_level=0.05):
    initial_features = data.columns.tolist()
    best_features = []
    while (len(initial_features)>0):
        remaining_features = list(set(initial_features)-set(best_features))
        new_pval = pd.Series(index=remaining_features)
        for new_column in remaining_features:
            model = smd.OLS(target, smd.add_constant(data[best_features+[new_column]])).fit()
            new_pval[new_column] = model.pvalues[new_column]
        min_p_value = new_pval.min()
        if(min_p_value<significance_level):
            best_features.append(new_pval.idxmin())
        else:
            break
    return best_features
##selecting best features
forward_selection(X,y)
X_for_selected=X[['age',
                'work_type_Never_worked',
                'heart_disease_1',
                'avg_glucose_level',
                'ever_married_Yes',
                'hypertension_1',
                'work_type_Private']]

#splitting the new dataset with best selected features
trainx, validx, trainy, validy= train_test_split(X_for_selected, y, test_size=0.30, random_state=1)
#run naive Bayes
nb = GaussianNB()
nb.fit(trainx,trainy)
#predict class membership
prediction_train_nb=nb.predict(validx)
#predict probabilities
pred_train_prob_nb = nb.predict_proba(validx)



help_str = '''
ScreenManager:
    WelcomeScreen:
    MainScreen:
    LoginScreen:
    SignupScreen:
    ResultScreen:

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
        pos_hint: {'center_y':0.8,'center_x':0.25}
        size_hint : (0.4,0.1)
        hint_text: 'How old are you?'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:work
        pos_hint: {'center_y':0.8,'center_x':0.75}
        size_hint : (0.4,0.1)
        hint_text: 'Have you ever worked? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:heartd
        pos_hint: {'center_y':0.6,'center_x':0.25}
        size_hint : (0.4,0.1)
        hint_text: 'Do you have any heart disease? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:avgglu
        pos_hint: {'center_y':0.6,'center_x':0.75}
        size_hint : (0.4,0.1)
        hint_text: 'What is your average glucose level?'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:married
        pos_hint: {'center_y':0.4,'center_x':0.25}
        size_hint : (0.4,0.1)
        hint_text: 'Have you ever been married? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:hypert
        pos_hint: {'center_y':0.4,'center_x':0.75}
        size_hint : (0.4,0.1)
        hint_text: 'Do you have hypertension? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDTextField:
        id:privsec
        pos_hint: {'center_y':0.2,'center_x':0.25}
        size_hint : (0.4,0.1)
        hint_text: 'Do you work in private sector? (Y/N)'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account-details'
        icon_right_color: app.theme_cls.primary_color
        required: True
        mode: "rectangle"

    MDRaisedButton:
        text:'Submit'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.6,'center_y':0.2}
        on_press: app.biosubmit()

    MDRaisedButton:
        text:'Result'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.85,'center_y':0.2}
        on_press: root.manager.current = 'resultscreen'

    MDLabel:
        id:biomet_info
        text:'Hello Main'
        pos_hint: {'center_x':0.5,'center_y':0.9}
        font_size : 20
        color: [40/255,65/255,100/255,1]
        font_style:'H3'
        halign:'center'

<ResultScreen>:
    name:'resultscreen'

    canvas.before:
        Color:
            rgba: 0.3,0.6,0.6,0.3
        Rectangle:
            pos: self.pos
            size: self.size

    MDLabel:
        id:result_info
        text:'Result Page'
        font_style:'H3'
        halign:'center'

    MDRaisedButton:
        text:'Result'
        size_hint: (0.13,0.07)
        font_size : 20
        pos_hint: {'center_x':0.35,'center_y':0.1}
        on_press:
            app.get()

    MDRaisedButton:
        text: 'Another input?'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.65,'center_y':0.1}
        on_press:
            root.manager.current = 'mainscreen'
            root.manager.transition.direction = 'up'

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
        bio_avgglu = self.strng.get_screen('mainscreen').ids.avgglu.text
        bio_married = self.strng.get_screen('mainscreen').ids.married.text
        bio_hypert = self.strng.get_screen('mainscreen').ids.hypert.text
        bio_privsec = self.strng.get_screen('mainscreen').ids.privsec.text

        if bio_age.split() == [] or bio_work.split() == [] or bio_heartd.split() == []:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Input',text = 'Please Enter a valid Input',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        if bio_avgglu.split() == [] or bio_hypert.split() == [] or bio_married.split() == []:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Input',text = 'Please Enter a valid Input',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        if ((bio_work or bio_heartd or bio_married or bio_hypert or bio_privsec) != "Y") and ((bio_work or bio_heartd or bio_married or bio_hypert or bio_privsec) != "N"):
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Input',text = 'Please Enter a valid Input',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        if len(bio_heartd.split())>1:
            cancel_btn_username_dialogue = MDFlatButton(text = 'Retry',on_release = self.close_username_dialog)
            self.dialog = MDDialog(title = 'Invalid Username',text = 'Please enter without space',size_hint = (0.7,0.2),buttons = [cancel_btn_username_dialogue])
            self.dialog.open()
        else:
            print(bio_age,bio_work,bio_heartd,bio_avgglu,bio_married,bio_hypert,bio_privsec)
            
            bio_info = {
                        'Age': bio_age,
                        'Employment': bio_work,
                        'HeartDisease': bio_heartd,
                        'AvgGlucose': bio_avgglu,
                        'Married': bio_married,
                        'Hypertension': bio_hypert,
                        'PrivSector': bio_privsec
                        }

            firebase.post('cis9590-355fe-default-rtdb/Biometrics', bio_info)            
                    
            #work type
            if bio_work == "Y" :
                bio_work = 0
            elif bio_work == "N" :
                bio_work = 1

            #heart disease
            if bio_heartd == "Y":
                bio_heartd = 1
            elif bio_heartd == "N":
                bio_heartd = 0

            #ever_married_yes
            if bio_married == "Y":
                bio_married = 1
            elif bio_married == "N":
                bio_married = 0

            #hypertension_1
            if bio_hypert == "Y":
                bio_hypert = 1
            elif bio_hypert == "N":
                bio_hypert = 0

            #work_type_private
            if bio_privsec == "Y":
                bio_privsec = 1
            elif bio_privsec == "N":
                bio_privsec = 0

            bio_age = int(bio_age)
            bio_avgglu = int(bio_avgglu)

            user_input = [[bio_age,bio_work,bio_heartd,bio_avgglu,bio_married,bio_hypert,bio_privsec]]


            pred_user_output = nb.predict(user_input)
            pred_prob_user_output = nb.predict_proba(user_input)
            result = np.round((100 * pred_prob_user_output), 1)
###            print(pred_user_output)
###            print(pred_user_output)

            result_info = {
                           'Prediction_Result': result[0][1],
                          }

            firebase.post('cis9590-355fe-default-rtdb/Result', result_info)
            print(result[0][1])

            auth = '7CWlh4kuYDiKSsKoD1quK1tY5BW08BxpjXIgLc28'

    urls = 'https://cis9590-355fe-default-rtdb.firebaseio.com/cis9590-355fe-default-rtdb/Result.json'
    auth_key = '7CWlh4kuYDiKSsKoD1quK1tY5BW08BxpjXIgLc28'

    def get(self):
##        request = requests.get(self.urls + '?auth=' + self.auth_key)
##        self.strng.get_screen('resultscreen').ids.result_info.text = f"The result is {self.request}"
        dataset = requests.get(self.urls + '?auth=' + self.auth_key)
        ds2 = dataset.json()
        ds3 = list(ds2)[-1]
        ds4 = ds2[ds3].get('Prediction_Result')
##        self.strng.get_screen('resultscreen').ids.result_info.text = f"Your unique key is {ds3} Here's your result {ds2} %"
        self.strng.get_screen('resultscreen').ids.result_info.text = f"There is a {ds4}% chance that the user will get a stroke"

LoginApp().run()
