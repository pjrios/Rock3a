# -*- coding: utf-8 -*-
"""Prueba rock3a.ipynb

Generado automáticamente por Colaboratory.

El archivo original se encuentra en
    https://colab.research.google.com/drive/1bhNH1VOfSymhlNqq-jPplcXRo26LzRtG
"""

# Instala las bibliotecas paho-mqtt y openai si aún no están instaladas
!pip install paho-mqtt openai

# Importa las bibliotecas necesarias
import paho.mqtt.client as mqtt
import openai
import time
import random
from datetime import datetime

# Configuración de Callbacks MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK recibido con código %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("cliente: " + str(client) + "userdata: " + str(userdata) + "mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Suscrito: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

# Configuración de variables MQTT
USER = "pjriosc"
PASSWORD = "arduino-conections-101"
ADDR = "4f2f4dcf13da4bd89f97a93716d25684.s2.eu.hivemq.cloud"

# Inicializa el cliente MQTT
client = mqtt.Client(client_id="", userdata=None, protocol=mqtt.MQTTv5)
client.on_connect = on_connect

# Configura la capa de seguridad TLS para MQTT
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(USER, PASSWORD)
client.connect(ADDR, 8883)

client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

# Suscribe al cliente MQTT al tema "Arduino/MQTT" con calidad de servicio (QoS) 1
client.subscribe("Arduino/MQTT", qos=1)
client.loop_start()

# Configuración (puedes cargar estos valores desde variables de entorno o un archivo de configuración)
mqtt_broker_address = "mqtt.example.com"
mqtt_port = 1883
mqtt_topic = "sensor/data"
openai_api_key = "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"
temperature_threshold = 2.0  # Umbral ajustable para el cambio de temperatura

# Inicializa los valores anteriores para la detección de cambios
previous_temperature = 25.0
previous_humidity = 50.0

# Inicializa datos simulados del sensor
simulated_temperature = 25.0
simulated_humidity = 50.0

# Configura tu clave de API de OpenAI
openai.api_key = openai_api_key

# Inicializa una lista para almacenar lecturas del sensor con (temperatura, humedad, marca de tiempo)
sensor_readings = []

# Define una función para leer datos del sensor y agregarlos a la lista
def publish_sensor_data():
    global previous_temperature, previous_humidity, simulated_temperature, simulated_humidity, sensor_readings

    # Simula datos del sensor aquí
    simulated_temperature += 1  # Aumenta la temperatura cada 1 segundo
    simulated_humidity -= 1  # Disminuye la humedad cada 2 segundos
    if simulated_humidity < 0.0:
        simulated_humidity = 0.0

    # Obtiene la marca de tiempo actual
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Agrega los datos simulados a la lista con marca de tiempo
    sensor_readings.append((simulated_temperature, simulated_humidity, current_time))

    # Publica los datos simulados en MQTT
    client.publish(mqtt_topic, f"Temperatura: {simulated_temperature:.2f}°C, Humedad: {simulated_humidity:.2f}%")

    # Comprueba cambios significativos y solicita una explicación
    check_for_changes(simulated_temperature, simulated_humidity)

# Define una función para comprobar cambios significativos y solicitar una explicación a ChatGPT
def check_for_changes(new_temperature, new_humidity):
    global previous_temperature, previous_humidity

    # Ejemplo: Si la temperatura aumentó más que el umbral
    if abs(new_temperature - previous_temperature) > temperature_threshold:
        explanation = chat_with_gpt(f"Mi sistema detectó un cambio significativo de temperatura. "
                                    f"Temperatura actual: {new_temperature:.2f}°C, "
                                    f"Temperatura anterior: {previous_temperature:.2f}°C, "
                                    f"Humedad actual: {new_humidity:.2f}%, "
                                    f"Humedad anterior: {previous_humidity:.2f}%. "
                                    f"¿Por qué cambió significativamente la temperatura?")
        print("Explicación:", explanation)

    # Actualiza los valores anteriores para la próxima comprobación
    previous_temperature = new_temperature
    previous_humidity = new_humidity

# Define una función para interactuar con ChatGPT
def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50  # Ajusta según sea necesario
    )
    return response.choices[0].text

# Conéctate al broker MQTT y comienza el bucle de monitoreo
client.connect("4f2f4dcf13da4bd89f97a93716d25684.s2.eu.hivemq.cloud", 8883)
client.loop_start()
seconds = 0

# Bucle principal para publicar datos del sensor
try:
    while True:
        # Recopila datos del sensor y envíalos a ChatGPT cada 1 minuto
        seconds += 1
        if seconds == 10:
            print("¡Aquí!")
            latest_reading = sensor_readings[-1]  # Obtiene la lectura más reciente de la lista
            current_temperature, current_humidity, current_time = latest_reading
            explanation = chat_with_gpt(f"Tengo un conjunto de datos a lo largo del tiempo en forma de (temperatura en °C, humedad, tiempo): {sensor_readings}, "
                                        f"¿Qué puedes inferir de estos datos?")
            print("Explicación:", explanation)
            seconds = 0

        # Publica datos del sensor cada 1 segundo
        publish_sensor_data()
        time.sleep(10)  # Espera 10 segundos

except KeyboardInterrupt:
    print("Monitoreo detenido por el usuario.")
    client.disconnect()

print(sensor_readings)
