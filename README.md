# Earthquake Alert System (Real-Time)

A Python-based earthquake monitoring project that fetches live seismic data from India’s government API, saves events to a MySQL database, and provides separate audio alert scripts.

---

## Tech Stack

- **Language:** Python
- **Libraries:** Requests, BeautifulSoup4, lxml, gTTS, pygame, mysql-connector-python
- **Database:** MySQL
- **API:** riseq.seismo.gov.in (National Center for Seismology, India)

---

## Features

- Fetches live earthquake event data from the Indian government seismic API
- Parses and extracts event ID, location, magnitude, latitude, and longitude
- Converts IST timestamps to UTC
- Checks for duplicate events before inserting (deduplication using event_id)
- Auto-creates the `earthquake_data` table on first run
- Includes separate audio announcement scripts for spoken alerts
- Runs continuously with periodic polling

---

## Project Structure

```
Earthquake-Alert/
├── check_alerts.py       # Main data collection script
├── announce.py           # Audio announcement script using the latest event
├── raspberrypi.py        # Alternate audio announcement script with nearby parks lookup
├── .env.example          # Example environment file
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.x
- MySQL Server
- A working audio environment if using `announce.py` or `raspberrypi.py`

### 1. Clone the Repository

```bash
git clone https://github.com/Pushti-12/Earthquake-Alert.git
cd Earthquake-Alert
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Copy the example file and update your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set `DB_PASSWORD` and `GOOGLE_MAPS_API_KEY` if needed.

### 4. Setup MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE frequency_data;
```

> The `earthquake_data` table is auto-created by `check_alerts.py` if it does not exist.

### 5. Update Database Credentials

Database connection settings are now loaded from `.env`.

Example `.env` values:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=frequency_data
```

For `raspberrypi.py`, optionally add your Google Maps API key:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

Example connection block inside the scripts is now handled by `get_db_connection()`.

```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="frequency_data"
)
```

### 6. Run the Data Collector

```bash
python check_alerts.py
```

### 7. Run Audio Alerts (Optional)

Run `announce.py` or `raspberrypi.py` separately to generate spoken alerts from the latest stored event:

```bash
python announce.py
```

```bash
python raspberrypi.py
```

> `raspberrypi.py` additionally looks up nearby parks using the Google Maps Places API and requires `YOUR_GOOGLE_MAPS_API_KEY` to be replaced.

---

## Database Schema

```sql
CREATE TABLE earthquake_data (
    event_id    VARCHAR(255) PRIMARY KEY,
    place_name  VARCHAR(255),
    origin_time DATETIME,
    latitude    FLOAT,
    longitude   FLOAT,
    magnitude   VARCHAR(10)
);
```

**Useful Queries:**

```sql
-- View all events
SELECT * FROM earthquake_data;

-- View recent events
SELECT * FROM earthquake_data ORDER BY origin_time DESC LIMIT 10;

-- View high magnitude events
SELECT * FROM earthquake_data WHERE magnitude >= 4.0;
```

---

## Notes

- `check_alerts.py` polls the API every 6 seconds.
- `announce.py` and `raspberrypi.py` are separate audio scripts and are not automatically invoked by `check_alerts.py`.
- `raspberrypi.py` uses Google Maps API lookup and may require a valid API key.
- `audio_message.mp3` and `last_event_id.txt` are generated at runtime by the speaker scripts.

---

## Data Source

- **API:** [RISEQ — National Center for Seismology](https://riseq.seismo.gov.in/riseq/earthquake)
- **Provider:** Ministry of Earth Sciences, Government of India
- **Updates:** Live earthquake events across India

