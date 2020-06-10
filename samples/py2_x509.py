import sys
import os
import configparser
import time
from random import randint


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'samples.ini'))

device_id = config['x509']['DeviceId']
scope_id = config['x509']['ScopeId']
key = {'certFile': config['x509']['CertFilePath'],'keyFile':config['x509']['KeyFilePath'],'certPhrase':config['x509']['CertPassphrase']}

if config['DEFAULT'].getboolean('Local'):
    sys.path.insert(0, 'src')

from iotc import IoTCClient, IOTCConnectType, IOTCLogLevel, IOTCEvents

# optional model Id for auto-provisioning
try:
    model_id = config['x509']['ModelId']
except:
    model_id = None


def onProps(propName, propValue):
    print(propValue)
    return True


def onCommands(command, ack):
    print(command.name)
    ack(command.name, 'Command received', command.request_id)


# see client.Device documentation above for x509 argument sample
client = IoTCClient(device_id, scope_id,
                  IOTCConnectType.IOTC_CONNECT_X509_CERT, key)
client.set_model_id(model_id)
client.set_log_level(IOTCLogLevel.IOTC_LOGGING_ALL)
client.on(IOTCEvents.IOTC_PROPERTIES, onProps)
client.on(IOTCEvents.IOTC_COMMAND, onCommands)



def main():
    client.connect()
    while client.is_connected():
        client.send_telemetry({
            'accelerometerX': str(randint(20, 45)),
            'accelerometerY': str(randint(20, 45)),
            "accelerometerZ": str(randint(20, 45))
        })
        time.sleep(3)


main()
