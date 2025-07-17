import os

# --- MQTT Configuration ---
MQTT_BROKER = os.environ.get('MQTT_BROKER', '192.168.50.161')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))

# --- Device Topics ---
DEVICE_INFO_TOPIC = "zigbee2mqtt/bridge/devices"
DEVICE_MOTION_SENSOR_LIVING_ROOM = "zigbee2mqtt/0x8c65a3fffe868d86"
DEVICE_MOTION_SENSOR_TEST = "zigbee2mqtt/motion_sensor_test"
DEVICE_SHINY_BUTTON = "zigbee2mqtt/shiny_4_button"
LAMP_LIVINGROOM_TOPIC = "zigbee2mqtt/lamp_livingroom/set"

# --- Logging Configuration ---
LOG_TOPIC = "zigbee2mqtt/#"
LOG_FILE = "zigbee_activity.log"
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# --- Application State ---
ignore_motion = False
