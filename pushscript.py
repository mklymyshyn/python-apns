import sys

from APNSWrapper.connection import APNSServiceConnection
from APNSWrapper import APNSNotificationWrapper, APNSNotification, APNSAlert, APNSProperty

encoded_token = 'PIpQK61TJ55KuCIYIzhgMiD40t+PR8o4y/0FRoB5GAE='

try:
    encoded_token = sys.argv[1]
except IndexError:
    pass

connection = APNSServiceConnection(host='127.0.0.1', port=1025)
wrapper = APNSNotificationWrapper(None, connection=connection)

message = APNSNotification()
message.tokenBase64(encoded_token)
message.badge(7)
message.sound('basso')
wrapper.append(payload=message)
wrapper.notify()

