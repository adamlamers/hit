from requests.auth import AuthBase

class CustomAuth(AuthBase):

    def __init__(self, file, variables):
        self.file = file
        self.variables = variables

    def __call__(self, request):
        with open(self.file, "r") as custom_auth_file:
            exec(custom_auth_file.read(), self.variables)
            self.variables["hit_custom_auth"](request, self.variables)
        return request
