# User Class for Flask
class User():

    def __init__(self,name,email,password, active = True):
        self.name = name
        self.email = email
        self.password = password
        self.active = active

    
