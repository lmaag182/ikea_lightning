import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add the parent directory to the Python path to allow importing the main script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mqtt_logger
import config

class TestMqttLogger(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        self.client = MagicMock()
        config.ignore_motion = False

    @patch('mqtt_logger.logging')
    def test_handle_motion_sensor_on(self, mock_logging):
        """Test motion sensor turning the lamp on."""
        payload = {"occupancy": True}
        mqtt_logger.handle_motion_sensor(self.client, json.dumps(payload))
        self.client.publish.assert_called_with(config.LAMP_LIVINGROOM_TOPIC, '{"state": "ON"}')

    @patch('mqtt_logger.logging')
    def test_handle_motion_sensor_off(self, mock_logging):
        """Test motion sensor turning the lamp off."""
        payload = {"occupancy": False}
        mqtt_logger.handle_motion_sensor(self.client, json.dumps(payload))
        self.client.publish.assert_called_with(config.LAMP_LIVINGROOM_TOPIC, '{"state": "OFF"}')

    @patch('mqtt_logger.logging')
    def test_handle_motion_sensor_ignored(self, mock_logging):
        """Test that motion is ignored when the flag is set."""
        config.ignore_motion = True
        payload = {"occupancy": True}
        mqtt_logger.handle_motion_sensor(self.client, json.dumps(payload))
        self.client.publish.assert_not_called()

    @patch('mqtt_logger.logging')
    def test_handle_shiny_button_on(self, mock_logging):
        """Test the shiny button turning the lamp on and ignoring motion."""
        payload = {"action": "on"}
        mqtt_logger.handle_shiny_button(self.client, json.dumps(payload))
        self.client.publish.assert_called_with(config.LAMP_LIVINGROOM_TOPIC, '{"state": "ON"}')
        self.assertTrue(config.ignore_motion)

    @patch('mqtt_logger.logging')
    def test_handle_shiny_button_off(self, mock_logging):
        """Test the shiny button turning the lamp off and enabling motion."""
        config.ignore_motion = True
        payload = {"action": "off"}
        mqtt_logger.handle_shiny_button(self.client, json.dumps(payload))
        self.client.publish.assert_called_with(config.LAMP_LIVINGROOM_TOPIC, '{"state": "OFF"}')
        self.assertFalse(config.ignore_motion)

    @patch('mqtt_logger.logging')
    def test_handle_device_info(self, mock_logging):
        """Test the device info handler."""
        devices = [
            {
                "friendly_name": "Test Device",
                "ieee_address": "0x123",
                "definition": {
                    "model": "Test Model",
                    "vendor": "Test Vendor"
                }
            }
        ]
        mqtt_logger.handle_device_info(json.dumps(devices))
        # Check that the logger was called with the device info
        self.assertTrue(any("Test Device" in call[0][0] for call in mock_logging.info.call_args_list))

if __name__ == '__main__':
    unittest.main()
