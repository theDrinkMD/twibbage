import random
import string

def createNewGameId():
    #insert code to randomly generate
    resp = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return str(resp)
