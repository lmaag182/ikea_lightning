import paho.mqtt.client as mqtt
import logging
import json
from datetime import datetime

# --- Configuration ---
MQTT_BROKER = "192.168.50.161"
MQTT_PORT = 1883
DEVICE_INFO_TOPIC = "zigbee2mqtt/bridge/devices"
DEVICE_MOTION_SENSOR_LIVING_ROOM = "zigbee2mqtt/0x8c65a3fffe868d86"
DEVICE_MOTION_SENSOR_TEST = "zigbee2mqtt/motion_sensor_test"
DEVICE_SHINY_BUTTON = "zigbee2mqtt/shiny_4_button"
LOG_TOPIC = "zigbee2mqtt/#"
LOG_FILE = "zigbee_activity.log"

ignore_motion = False

# --- Set up logging ---
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe([(DEVICE_INFO_TOPIC, 0), (LOG_TOPIC, 0)])
        print(f"Subscribed to {DEVICE_INFO_TOPIC} and {LOG_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    global ignore_motion
    try:
        # Get the current time
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Decode the message payload
        payload_str = msg.payload.decode("utf-8")
        
        # Log the raw message
        log_message = f"Topic: {msg.topic} | Payload: {payload_str}"
        logging.info(log_message)
        #print(f"Logged: {log_message}")

        if msg.topic == DEVICE_MOTION_SENSOR_LIVING_ROOM:
            payload = json.loads(payload_str)
            print(f"DEVICE_MOTION_SENSOR_LIVING_ROOM:{payload['occupancy']}")
            if not ignore_motion:
                # Switch on or off the lamp based on occupancy
                if payload.get("occupancy") is True:
                    lamp_topic = "zigbee2mqtt/lamp_livingroom/set"
                    command = json.dumps({"state": "ON"})
                    client.publish(lamp_topic, command)
                    print(f"Sent ON command to {lamp_topic}")
                elif payload.get("occupancy") is False:
                    lamp_topic = "zigbee2mqtt/lamp_livingroom/set"
                    command = json.dumps({"state": "OFF"})
                    client.publish(lamp_topic, command)
                    print(f"Sent OFF command to {lamp_topic}")

        if msg.topic == DEVICE_MOTION_SENSOR_TEST:
            payload = json.loads(payload_str)
            print(f"DEVICE_MOTION_SENSOR_TEST:{payload["occupancy"]}")

        if msg.topic == DEVICE_SHINY_BUTTON:
            payload = json.loads(payload_str)
            action = payload.get("action")
            lamp_topic = "zigbee2mqtt/lamp_livingroom/set"
            if action == "on":
                command = json.dumps({"state": "ON"})
                client.publish(lamp_topic, command)
                print(f"Sent ON command to {lamp_topic} via shiny button")
                ignore_motion = False
            elif action == "off":
                command = json.dumps({"state": "OFF"})
                client.publish(lamp_topic, command)
                print(f"Sent OFF command to {lamp_topic} via shiny button")
                ignore_motion = True

        # If it's device information, pretty print it
        if msg.topic == DEVICE_INFO_TOPIC:
            try:
                devices = json.loads(payload_str)
                print("\n--- Zigbee Device Information ---")
                for device in devices:
                    if device.get('friendly_name'):
                        print(f"  - Friendly Name: {device['friendly_name']}")
                        print(f"    IEEE Address: {device['ieee_address']}")
                        if 'definition' in device and device['definition']:
                            print(f"    Model: {device['definition']['model']}")
                            print(f"    Vendor: {device['definition']['vendor']}")
                print("------------------------------------\n")
            except json.JSONDecodeError:
                print("Could not decode device information JSON.")

    except Exception as e:
        print(f"An error occurred in on_message: {e}")


# --- Main script ---
if __name__ == "__main__":
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Error connecting to MQTT Broker: {e}")
        exit()

    # Start the network loop
    client.loop_forever()
