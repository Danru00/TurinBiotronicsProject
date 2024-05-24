from machine import Pin, I2C, ADC
import time
import network
from umqtt.simple import MQTTClient
import config

# MQTT Topic definition
MQTT_TOPIC_EMG = 'pico/EMG2'

# MQTT Parameters
MQTT_SERVER = config.mqtt_server
MQTT_PORT = 1883
MQTT_USER = config.mqtt_username
MQTT_PASSWORD = config.mqtt_password
MQTT_CLIENT_ID = b"raspberrypi_picow_2"
MQTT_KEEPALIVE = 7200
MQTT_SSL = False
MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}


# Initialize ADC communication
adc = ADC(26) # Change Pin according to connection

def get_emg_readings():

    value = adc.read_u16()
    EMG_data = [value]
    
    return EMG_data

def initialize_wifi(ssid, password):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Connect to the network
    wlan.connect(ssid, password,channel=2)

    # Wait for Wi-Fi connection
    connection_timeout = 60
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)

    # Check if connection is successful
    if wlan.status() != 3:
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True

def connect_mqtt():
    try:
        client = MQTTClient(client_id=MQTT_CLIENT_ID,
                            server=MQTT_SERVER,
                            port=MQTT_PORT,
                            user=MQTT_USER,
                            password=MQTT_PASSWORD,
                            keepalive=MQTT_KEEPALIVE,
                            ssl=MQTT_SSL,
                            ssl_params=MQTT_SSL_PARAMS)
        client.connect()
        
        return client
    except Exception as e:
        print('Error connecting to MQTT:', e)
        raise  # Re-raise the exception to see the full traceback

def publish_mqtt(topic, value):
    client.publish(topic, value)

try:
    if not initialize_wifi(config.wifi_ssid, config.wifi_password):
        print('Error connecting to the network... exiting program')
    else:
        # Connect to MQTT broker, start MQTT client
        client = connect_mqtt()
        print('Publishing!')
        while (1):
           EMG_data = str(get_emg_readings())           
           publish_mqtt(MQTT_TOPIC_EMG, EMG_data)

except Exception as e:
    print('Error:', e)
