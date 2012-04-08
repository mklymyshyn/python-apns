"""The most basic chat protocol possible.

run me with twistd -y chatserver.py, and then connect with multiple
telnet clients to port 1025
"""

try:
    import json
except ImportError:
    import simplejson as json

import base64
import logging
import sys
import ssl

from APNSWrapper.connection import DummyConnection, APNSConnection
from APNSWrapper.notifications import APNSNotificationWrapper

from twisted.internet import protocol, reactor
from twisted.protocols import basic
from twisted.python import log


LISTEN_PORT = 1025
CERT_PATH='cert.pem'
SANDBOX = True

try:
    CERT_PATH = sys.argv[1]
except:
    sys.stderr.write("Please, specify path to your certificate file"\
                     " as first argument of service.py\n\n")
    sys.exit(1)

try:
    SANDBOX = bool(sys.argv[2])
except:
    sys.stderr.write("Please, specify 1/0 or true/false value"\
                     " for second argument - it will be sandbox or"\
                     " production mode of service connection\n\n")
    sys.exit(1)


class APNSServiceListener(basic.LineReceiver):
    _wrapper = None
    _connection = 0

    def __init__(self, *args, **kwargs):
        self.__class__.establish_connection()
        self.__class__._connection += 1

    @property
    def connection(self):
        """Return number of connection"""
        return self._connection

    @classmethod
    def establish_connection(cls):
        """
        Class method to establish connection to the APNS service
        for whole service (for all clients)
        """
        log.msg("Estabilishing connection to the APNS Service...",
                logLevel=logging.INFO)
        cls._ssl_connection = APNSConnection(certificate=CERT_PATH,
                                         force_ssl_command=False,
                                         debug=True)
        cls._wrapper = APNSNotificationWrapper('', sandbox=SANDBOX,
                                      connection=cls._ssl_connection)
        cls._wrapper.connect()
        return cls._wrapper

    @property
    def wrapper(self):
        if not hasattr(self.__class__, '_wrapper'):
            wrapper = APNSServiceListener.establish_connection()
            return wrapper

        # TODO: check that connection in wrapper still exist
        return self._wrapper

        """
        encoded_token = '0/w68oJxIYlFpDDC/4eeo/bpt/44JTzZ6ZEXEgVvU6c='

        badge(wrapper, encoded_token)

        sound(wrapper, encoded_token)

        alert(wrapper, encoded_token)

        wrapper.notify()
        """

    def connectionMade(self):
        """
        Service method to add new client to the list of clients of
        the service
        """
        log.msg("Got new client on connection %d!" % self.connection,
                logLevel=logging.DEBUG)
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        """
        It's just service method to remove client from the factory.
        Nothing special happened on the service.
        """
        log.msg("Client disconnected", logLevel=logging.DEBUG)
        self.factory.clients.remove(self)

    def error(self, msg=""):
        log.msg(msg, logLevel=logging.ERROR)

    def lineReceived(self, line):
        """
        Receive one line from the client. The main idea is to
        work like Twitter Stream API when different messages splitted
        by newline character.
        """

        response = json.loads(line)

        if not 'message' in response:
            return self.error(msg=u"You're not specified message to send")

        msg_data = base64.standard_b64decode(response['message'])
        log.msg("Received message for APNS: %s" % msg_data,
                logLevel=logging.INFO)
        self.wrapper.connection.write(data=msg_data)

    def response(self, response):
        """
        Method to send response to the client. Response should be
        always sort of tuple, list or dict.

        Method automatically dump it to JSON and send response to the client.
        """
        self.transport.write(json.dumps(response))


factory = protocol.ServerFactory()
factory.protocol = APNSServiceListener
factory.clients = []

reactor.listenTCP(LISTEN_PORT, factory)
log.msg("  > Starting APNS service "\
                 "listener on port %d ...\n\n" % LISTEN_PORT,
                 logLevel=logging.INFO)


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    reactor.run()
