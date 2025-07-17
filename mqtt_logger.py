import paho.mqtt.client as mqtt
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
import config
import sys
import argparse

# --- Set up logging ---
def setup_logging(log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # File handler
    file_handler = RotatingFileHandler(config.LOG_FILE, maxBytes=config.LOG_MAX_BYTES, backupCount=config.LOG_BACKUP_COUNT)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)


# --- Message Handlers ---
def handle_motion_sensor(client, payload_str):
    """Handles messages from the living room motion sensor."""
    payload = json.loads(payload_str)
    logging.info(f"Motion sensor update: {payload}")
    if not config.ignore_motion:
        state = "ON" if payload.get("occupancy") else "OFF"
        command = json.dumps({"state": state})
        client.publish(config.LAMP_LIVINGROOM_TOPIC, command)
        logging.info(f"Sent {state} command to {config.LAMP_LIVINGROOM_TOPIC}")

def handle_shiny_button(client, payload_str):
    """Handles messages from the shiny button."""
    payload = json.loads(payload_str)
    action = payload.get("action")
    logging.info(f"Shiny button action: {action}")
    if action in ["on", "off"]:
        state = "ON" if action == "on" else "OFF"
        command = json.dumps({"state": state})
        client.publish(config.LAMP_LIVINGROOM_TOPIC, command)
        logging.info(f"Sent {state} command to {config.LAMP_LIVINGROOM_TOPIC} via shiny button")
        config.ignore_motion = (action == "on")

def handle_device_info(payload_str):
    """Handles device information messages."""
    try:
        devices = json.loads(payload_str)
        logging.info("\n--- Zigbee Device Information ---")
        for device in devices:
            if device.get('friendly_name'):
                logging.info(f"  - Friendly Name: {device['friendly_name']}")
                logging.info(f"    IEEE Address: {device['ieee_address']}")
                if 'definition' in device and device['definition']:
                    logging.info(f"    Model: {device['definition']['model']}")
                    logging.info(f"    Vendor: {device['definition']['vendor']}")
        logging.info("------------------------------------\n")
    except json.JSONDecodeError:
        logging.error("Could not decode device information JSON.")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
        client.subscribe([(config.DEVICE_INFO_TOPIC, 0), (config.LOG_TOPIC, 0)])
        logging.info(f"Subscribed to {config.DEVICE_INFO_TOPIC} and {config.LOG_TOPIC}")
    else:
        logging.error(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    try:
        payload_str = msg.payload.decode("utf-8")
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": msg.topic,
            "payload": payload_str
        }
        logging.info(json.dumps(log_entry))

        if msg.topic == config.DEVICE_MOTION_SENSOR_LIVING_ROOM:
            handle_motion_sensor(client, payload_str)
        elif msg.topic == config.DEVICE_SHINY_BUTTON:
            handle_shiny_button(client, payload_str)
        elif msg.topic == config.DEVICE_INFO_TOPIC:
            handle_device_info(payload_str)
        elif msg.topic == config.DEVICE_MOTION_SENSOR_TEST:
            payload = json.loads(payload_str)
            logging.info(f"Test motion sensor update: {payload}")

    except Exception as e:
        logging.error(f"An error occurred in on_message: {e}")


# --- Main script ---
def main():
    parser = argparse.ArgumentParser(description="MQTT Logger for Zigbee devices.")
    parser.add_argument("--broker", default=config.MQTT_BROKER, help="MQTT broker address.")
    parser.add_argument("--port", type=int, default=config.MQTT_PORT, help="MQTT broker port.")
    parser.add_argument("--log-level", default=config.LOG_LEVEL, help="Logging level (e.g., INFO, DEBUG).")
    args = parser.parse_args()

    setup_logging(args.log_level)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.broker, args.port, 60)
    except Exception as e:
        logging.error(f"Error connecting to MQTT Broker: {e}")
        exit()

    client.loop_forever()

if __name__ == "__main__":
    main()
