from machine import Pin, I2C
from time import sleep
import network
from umqtt.simple import MQTTClient
import config
from imu import MPU6050

# MQTT Topic definition
MQTT_TOPIC_IMU = 'pico/IMU'

# MQTT Parameters
MQTT_SERVER = config.mqtt_server
MQTT_PORT = 1883
MQTT_USER = config.mqtt_username
MQTT_PASSWORD = config.mqtt_password
MQTT_CLIENT_ID = b"raspberrypi_picow_IMU"
MQTT_KEEPALIVE = 7200
MQTT_SSL = True
MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}

# Initialize I2C communication
i2c = I2C(0, sda=Pin(12), scl=Pin(13), freq=400000) #Change Pin numbers accoding to connections

# Initialize IMU sensor
imu = MPU6050(i2c)

def get_imu_readings():
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)
    gx=round(imu.gyro.x)
    gy=round(imu.gyro.y)
    gz=round(imu.gyro.z)
    IMU_data = [ax,ay,az,gx,gy,gz]
    return IMU_data

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
        sleep(1)

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
    print(value)
    
try:
    if not initialize_wifi(config.wifi_ssid, config.wifi_password):
        print('Error connecting to the network... exiting program')
    else:
        # Connect to MQTT broker, start MQTT client
        client = connect_mqtt()
        while (1):
            # Read sensor data
            IMU_data = get_imu_readings()

            # Publish as MQTT payload
            publish_mqtt(MQTT_TOPIC_IMU, str(IMU_data))
        

except Exception as e:
    print('Error:', e)