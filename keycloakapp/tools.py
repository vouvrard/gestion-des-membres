import os

def getsecret(name):
    v1 = os.getenv(name)
    
    secret_fpath = f'/run/secrets/{name}'
    existence = os.path.exists(secret_fpath)
    
    if v1 is not None:
        return v1
    
    if existence:
        v2 = open(secret_fpath).read().rstrip('\n')
        return v2
    
    if all([v1 is None, not existence]):
        return KeyError(f'{name}')