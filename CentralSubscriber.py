# python 3.12

import random
import numpy as np
import time
from paho.mqtt import client as mqtt_client
import csv
import os

broker = "172.20.10.5"
port = 1883
topic_IMU = "pico/IMU"
topic_EMG1 = "pico/EMG1"
topic_EMG2 = "pico/EMG2"

client_id = f'subscribe-{"CentralSubscriber"}'
username = None
password = None

IMU_array = []
EMG_array1 = []
EMG_array2 = []
start_time = time.time() #Initialize time counter to calculate acquisition frequency at the end


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc,properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(broker, port)

    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        message = msg.payload.decode()
        if msg.topic == topic_IMU:
            IMU_msg = msg.payload.decode()
            IMU_array.append(np.array(np.matrix(IMU_msg)).ravel())
            if len(IMU_array) % 100 == 0:
               print('Receiving IMU:' , IMU_msg)

        elif msg.topic == topic_EMG1:
            EMG_msg =  msg.payload.decode()
            EMG_array = np.array(np.matrix(EMG_msg)).ravel()
            EMG_array1.append(EMG_array[0])
            if len(EMG_array1) % 500 == 0:
               print('Receiving EMG1:' , EMG_array[0])
               

        elif msg.topic == topic_EMG2:
           EMG_msg =  msg.payload.decode()
           EMG_array = np.array(np.matrix(EMG_msg)).ravel()
           EMG_array2.append(EMG_array[0])
           if len(EMG_array2) % 500 == 0:
               print('Receiving EMG2:',EMG_array[0])
              
                    
    client.subscribe([(topic_IMU,0),(topic_EMG1,0),(topic_EMG2,0)])
    client.on_message = on_message

def save_data():
   elapsed_time = time.time() - start_time
   frequency_IMU = [len(IMU_array)/elapsed_time]
   frequency_EMG1 = [len(EMG_array1)/elapsed_time]
   frequency_EMG2 = [len(EMG_array2)/elapsed_time]
   frequency = [frequency_IMU,frequency_EMG1,frequency_EMG2] 
   np.savetxt("IMU.csv", IMU_array, delimiter=",")
   np.savetxt("EMG1.csv", EMG_array1, delimiter=",")
   np.savetxt("EMG2.csv", EMG_array2, delimiter=",")
   np.savetxt("Sampling_frequency.txt", frequency, delimiter=",")
   

def run():
    client = connect_mqtt()
    subscribe(client)
    try:
        client.loop_forever()
    
    except KeyboardInterrupt:
        pass
    finally:
        print('Saving the Data!')
        save_data()


if __name__ == '__main__':
    run()
