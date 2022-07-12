def login(email, password, ltoken):
    return {
        'command': 'login',
        'email': email,
        'password': password,
        'ltoken': ltoken
    }

def getProfile(token, nick):
    return {
        'command': 'getProfile',
        'nick': nick,
        'actPath': f'/{nick}/',
        'token': token
    }