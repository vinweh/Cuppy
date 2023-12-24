import sqlite3

class CuppyDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            print("Connected to database successfully")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from database")

    def execute_query(self, query, data=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            print("Query executed successfully")
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    def fetch_data(self, query, data=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return []
        
    def fetch_one(self, query, data=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            row = cursor.fetchone()
            return row
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return None

if __name__ == "__main__":
    
# Example usage
    db = CuppyDatabase("cuppy-dev.db")
    db.connect()

    create_runs_table_query = """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME,
        url_count INTEGER,
        success_count INTEGER
    """

    create_urls_table_query = """CREATE TABLE urls 
       (id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        status_code INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        title TEXT,
        canonical_url_header TEXT,
        canonical_url_html TEXT,
        og_url TEXT )
    """
    db.execute_query(create_urls_table_query)

    insert_data_query = """
    INSERT INTO urls (url, status_code, timestamp, canonical_url_header, canonical_url_html)
     VALUES ("https://www.google.com", 200, CURRENT_TIMESTAMP, "https://www.google.com", "https://www.google.com")
      ON CONFLICT(url) DO UPDATE 
     SET status_code=?, timestamp=CURRENT_TIMESTAMP, canonical_url_header=?, canonical_url_html=?;"""
    data = (200, "https://www.google.com", "https://www.google.com")
    db.execute_query(insert_data_query, data=data)

    select_data_query = """
    SELECT * FROM urls;
    """
    data = db.fetch_data(select_data_query)
    print(data)

    select_data_query = """
    SELECT * FROM runs;
    """
    data = db.fetch_data(select_data_query)
    print(data)

    

    db.disconnect()