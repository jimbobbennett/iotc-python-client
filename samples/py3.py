import os
import asyncio
import configparser
import sys

from random import randint

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "samples.ini"))

if config["DEFAULT"].getboolean("Local"):
    sys.path.insert(0, "src")

from iotc import (
    IOTCConnectType,
    IOTCLogLevel,
    IOTCEvents,
    Command,
    CredentialsCache,
    Storage,
)
from iotc.aio import IoTCClient

device_id = config["DEVICE_M3"]["DeviceId"]
scope_id = config["DEVICE_M3"]["ScopeId"]
key = config["DEVICE_M3"]["DeviceKey"]


class MemStorage(Storage):
    def retrieve(self):
        return CredentialsCache(
            "iotc-1f9e162c-eacc-408d-9fb2-c9926a071037.azure-devices.net",
            "javasdkcomponents2",
            key,
        )

    def persist(self, credentials):
        return None


# optional model Id for auto-provisioning
try:
    model_id = config["DEVICE_M3"]["ModelId"]
except:
    model_id = None


async def on_props(property_name, property_value, component_name):
    print("Received {}:{}".format(property_name, property_value))
    return True


async def on_commands(command: Command):
    print("Received command {} with value {}".format(command.name, command.value))
    await command.reply()


async def on_enqueued_commands(command_name, command_data):
    print(command_name)
    print(command_data)


# change connect type to reflect the used key (device or group)
client = IoTCClient(
    device_id,
    scope_id,
    IOTCConnectType.IOTC_CONNECT_DEVICE_KEY,
    key,
    storage=MemStorage(),
)
if model_id != None:
    client.set_model_id(model_id)

client.set_log_level(IOTCLogLevel.IOTC_LOGGING_ALL)
client.on(IOTCEvents.IOTC_PROPERTIES, on_props)
client.on(IOTCEvents.IOTC_COMMAND, on_commands)
client.on(IOTCEvents.IOTC_ENQUEUED_COMMAND, on_enqueued_commands)

# iotc.setQosLevel(IOTQosLevel.IOTC_QOS_AT_MOST_ONCE)

async def telemetry_loop():
    while client.is_connected():
        await client.send_telemetry(
            {
                "acceleration": {
                    "x": str(randint(20, 45)),
                    "y": str(randint(20, 45)),
                    "z": str(randint(20, 45)),
                }
            }
        )
        await asyncio.sleep(3)

async def main():
    await client.connect()
    await client.send_property({"writeableProp": 50})
    await client.run_telemetry_loop(telemetry_loop)
    

asyncio.run(main())
