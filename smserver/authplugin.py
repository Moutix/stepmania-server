""" Auth plugin base module """

class AuthPlugin(object):
    def __init__(self, server, autocreate):
        self.server = server
        self.autocreate = autocreate

    def login(self, _user, _password):
        return True
