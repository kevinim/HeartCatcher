# Creating a LOGIN page

# Creating the App

from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.factory import Factory

Window.size = (500,800)


class Myapp(MDApp):
	def build(self):       
		return
    
#def open_bottom_sheet(self):
#		self.obj = MDCustomBottomSheet(screen = Factory.CustomBottomSheet)
    
Myapp().run()

