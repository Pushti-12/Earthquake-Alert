import os
import mysql.connector
import requests
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

def load_last_event_id():
    try:
        with open("last_event_id.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def save_last_event_id(event_id):
    with open("last_event_id.txt", "w") as file:
        file.write(event_id)

def create_audio_message(earthquake_data, nearby_parks):
    if not earthquake_data:
        return "No earthquake data available."

    event_id, place_name, origin_time, latitude, longitude, magnitude = earthquake_data
    park_info = ""
    for park in nearby_parks:
        if park['vicinity'] != "Unnamed Road":
            park_info += f"{park['name']} located at {park['vicinity']}, "
        else:
            park_info += f"{park['name']}, "

    audio_message = f"The earthquake occurred at {place_name} on {origin_time} with a magnitude of {magnitude}.Don't get panic.please follow the safety measures:go to open fields or if you get stuck in any area,find a object and keep holding it with one hand.use a sturdy object like a desk to protect your head and neck.Move out from any vehicle if you are present there. Nearby parks include: {park_info}..Disaster helpline number for certain country for india its 112 or 100 for australia its 000 or 112 for canada and US its 911"
    return audio_message

def generate_audio(message):
    tts = gTTS(text=message, lang='en-in')  # Indian English language code
    tts.save("audio_message.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("audio_message.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def find_parks_near_location(latitude, longitude, radius=20000):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        print("Google Maps API key is not configured. Skipping nearby park lookup.")
        return []

    try:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&type=park&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX and 5XX status codes
        data = response.json()

        if 'results' in data:
            return data['results'][:3]  # Return only the top three nearest parks
        else:
            print("No parks found near the specified location")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def main():
    global last_spoken_earthquake
    global last_spoken_time

    if last_spoken_time is None:
        last_spoken_time = time.time()  # Initialize last_spoken_time

    latest_earthquake = fetch_latest_earthquake_data()

    if latest_earthquake != last_spoken_earthquake:
        nearby_parks = find_parks_near_location(latest_earthquake[3], latest_earthquake[4])  # Latitude at index 3, longitude at index 4
        audio_message = create_audio_message(latest_earthquake, nearby_parks)
        print(audio_message)  # Print the message for reference

        event_id = latest_earthquake[0]  # Event ID is the first element
        last_event_id = load_last_event_id()

        if event_id != last_event_id:
            for _ in range(3):
                generate_audio(audio_message)
                time.sleep(2)  # Wait for 2 seconds between announcements
            save_last_event_id(event_id)
            last_spoken_earthquake = latest_earthquake
            last_spoken_time = time.time()  # Record the time when the earthquake data was last spoken
    elif time.time() - last_spoken_time >= 60:  # Check if 1 minute has passed since the last spoken earthquake
        nearby_parks = find_parks_near_location(last_spoken_earthquake[3], last_spoken_earthquake[4])  # Latitude at index 3, longitude at index 4
        audio_message = create_audio_message(last_spoken_earthquake, nearby_parks)
        print(audio_message)  # Print the message for reference

        event_id = last_spoken_earthquake[0]  # Event ID is the first element
        last_event_id = load_last_event_id()

        if event_id != last_event_id:
            for _ in range(3):
                generate_audio(audio_message)
              #  time.sleep(2)  # Wait for 2 seconds between announcements
            save_last_event_id(event_id)
            last_spoken_time = time.time()  # Update the last spoken time

while True:
    main()
    time.sleep(30)  # Sleep for 30 seconds before checking again
