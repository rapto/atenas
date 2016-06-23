from django.conf import settings

def claveAleatoria():
    import random
    import string
    ret=''
    for _ in range(settings.LONGITUD_CLAVE):
        ret+=random.choice(string.lowercase)
    return ret
