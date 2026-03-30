import mysql.connector
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import requests
import time

def table_exists(cursor):
    cursor.execute("SHOW TABLES LIKE 'earthquake_data'")
    return bool(cursor.fetchone())

def create_earthquake_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS earthquake_data (
        event_id VARCHAR(255) PRIMARY KEY,
        place_name VARCHAR(255),
        origin_time DATETIME,
        latitude FLOAT,
        longitude FLOAT,
        magnitude VARCHAR(10)
    )
    """
    cursor.execute(create_table_query)
    print("Table 'earthquake_data' created successfully!")

def insert_earthquake_data(event_id, place_name, origin_time, latitude, longitude, magnitude):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sumeet",
            database="frequency_data"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM earthquake_data WHERE event_id = %s", (event_id,))
        existing_event = cursor.fetchone()
        if existing_event:
            print("Event with ID", event_id, "already exists. Skipping insertion.")
            return
        insert_query = "INSERT INTO earthquake_data (event_id, place_name, origin_time, latitude, longitude, magnitude) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (event_id, place_name, origin_time, latitude, longitude, magnitude))
        conn.commit()
        print("Data inserted successfully!")
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

while True:
    try:
        source = requests.get('https://riseq.seismo.gov.in/riseq/earthquake').text
        soup = BeautifulSoup(source, 'lxml')
        earthquake_element = soup.find('li', class_='list-view-item event_list')

        if earthquake_element:
            data_json = earthquake_element['data-json']
            earthquake_data = json.loads(data_json)
            event_id = earthquake_data['event_id']
            place_name_full = earthquake_data['event_name']
            origin_time_str = earthquake_data['origin_time']
            origin_time_str = origin_time_str.replace(' IST', '')
            origin_time = datetime.strptime(origin_time_str, '%Y-%m-%d %H:%M:%S')
            origin_time = origin_time - timedelta(hours=5, minutes=30)
            origin_time = origin_time.strftime('%Y-%m-%d %H:%M:%S')
            lat_long = earthquake_data['lat_long']
            latitude, longitude = map(float, lat_long.split(','))
            magnitude_depth = earthquake_data['magnitude_depth']
            magnitude = None
            for item in magnitude_depth.split(','):
                if item.startswith('M:'):
                    magnitude = "{:.1f}".format(float(item.split(': ')[1]))
                    break
            place_name = place_name_full.split(' - ')[-1].strip()
            print("Event ID:", event_id)
            print("Place Name:", place_name)
            print("Origin Time:", origin_time)
            print("Latitude:", latitude)
            print("Longitude:", longitude)
            print("Magnitude:", magnitude)
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="sumeet",
                database="frequency_data"
            )
            cursor = conn.cursor()
            if not table_exists(cursor):
                create_earthquake_table(cursor)
            if magnitude is not None:
                insert_earthquake_data(event_id, place_name, origin_time, latitude, longitude, magnitude)
            else:
                print("Magnitude is None. Skipping insertion.")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    time.sleep(6)  # Sleep for 60 seconds before repeating
