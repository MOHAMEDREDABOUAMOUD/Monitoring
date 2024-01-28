import base64
import paho.mqtt.client as mqtt
import time
import random
from dao import Dao
from datetime import datetime

broker_address = "test.mosquitto.org"
topic = "iot/temp_reda"
MAC = "00:1B:44:11:3A:B7"

daoo = Dao()

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the topic when connected
    client.subscribe(topic)

# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    # Decode the bytes to a string
    string_value = msg.payload.decode('utf-8')

    # Extract the numeric part
    numeric_part = string_value  # Skip the 'b' prefix

    # Convert the numeric part to a float
    numeric_value = float(numeric_part.split(";")[1])
    daoo.addIOT({'id': daoo.getIOTByMac(numeric_part.split(";")[0])["id"], 'MAC': numeric_part.split(";")[0], 'date': datetime.now(), 'temperature': numeric_value})
    print(f"Received message: {numeric_value}")

# Create MQTT client
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, 1883, 60)

# Start the loop to handle communication with the broker
client.loop_start()

try:
    while True:
        # Generate a random number
        random_number = round(random.uniform(-10, 50), 2)
        
        message = MAC+";"+str(random_number)
        
        # Publish the random number to the topic
        client.publish(topic, message)
        
        print(f"Published: {message}")
        
        # Wait for a short interval before publishing the next number
        time.sleep(6)

except KeyboardInterrupt:
    # Disconnect from the broker when the script is interrupted
    client.disconnect()
    print("Disconnected from the broker.")
