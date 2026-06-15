import os
import mysql.connector
from dotenv import load_dotenv
from gtts import gTTS
import pygame
import time

load_dotenv()

# Global variables to store the last spoken earthquake data and the time it was last spoken
last_spoken_earthquake = None
last_spoken_time = None


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "frequency_data")
    )


def fetch_latest_earthquake_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM earthquake_data ORDER BY origin_time DESC LIMIT 1")
        latest_earthquake = cursor.fetchone()
        return latest_earthquake
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_audio_message(earthquake_data):
    if not earthquake_data:
        return "No earthquake data available."

    event_id, place_name, origin_time, latitude, longitude, magnitude = earthquake_data
    audio_message = f"The earthquake occurred at {place_name} on {origin_time} with a magnitude of {magnitude}. Please stay safe."
    return audio_message

def generate_audio(message):
    tts = gTTS(text=message, lang='en')
    tts.save("audio_message.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("audio_message.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def main():
    global last_spoken_earthquake
    global last_spoken_time

    latest_earthquake = fetch_latest_earthquake_data()

    if latest_earthquake != last_spoken_earthquake:
        audio_message = create_audio_message(latest_earthquake)
        print(audio_message)  # Print the message for reference
        generate_audio(audio_message)
        last_spoken_earthquake = latest_earthquake
        last_spoken_time = time.time()  # Record the time when the earthquake data was last spoken
    elif time.time() - last_spoken_time >= 2 * 60:  # Check if 2 minutes have passed since the last spoken earthquake
        # Speak the same earthquake data again after 2 minutes
        audio_message = create_audio_message(last_spoken_earthquake)
        print(audio_message)  # Print the message for reference
        generate_audio(audio_message)
        last_spoken_time = time.time()  # Update the last spoken time

while True:
    main()
    time.sleep(30)  # Sleep for 5 minutes before checking again
