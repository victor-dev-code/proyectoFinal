import requests, base64, os, sys
from pagina1 import models
token = '1873124072:AAEhS9ew_KO8SID0lHb2ydpWLUtd-24r67s'
chat_id = '524454403'

#def mandar_mensaje_bot(mensaje, token=token, chat_id=chat_id):
#    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + mensaje
#    response = requests.get(send_text)
#    mensaje = base64.b64encode(os.urandom(5)).decode('utf-8')

def mandar_mensaje_bot(mensaje, token=token, chat_id=chat_id):
    mensaje = base64.b64encode(os.urandom(5)).decode('utf-8')
    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + mensaje
    response = requests.get(send_text)


if __name__ == '__main__':
    mensaje = base64.b64encode(os.urandom(5)).decode('utf-8')
    mandar_mensaje_bot(mensaje)