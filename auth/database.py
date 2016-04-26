import authplugin

class AuthDatabase(authplugin.AuthPlugin):
    def login(self, user, password):
        return True
