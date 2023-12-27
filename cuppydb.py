import sqlite3

class CuppyDatabase:
    """Class to connect to the database and execute queries"""
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


    create_urls_table_query = """CREATE TABLE urls 
       (id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        etag TEXT,
        status_code INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        title TEXT,
        canonical_url_header TEXT,
        canonical_url_html TEXT,
        og_url TEXT,
        og_title TEXT,
        description TEXT, clean_text TEXT)
    """
    db.execute_query(create_urls_table_query)

    insert_data_query = """
    INSERT INTO urls (
         url
        ,etag 
        ,status_code
        ,timestamp
        ,title
        ,canonical_url_header
        ,canonical_url_html
        ,og_url
        ,og_title
        ,description
        ,clean_text)
        )
     VALUES ("https://www.google.com", NULL, 200, CURRENT_TIMESTAMP, "Google", 
     NULL, "https://www.google.com", NULL, NULL, NULL)
      ON CONFLICT(url) DO UPDATE 
     SET etag=?, status_code=?, timestamp=CURRENT_TIMESTAMP, title=?, canonical_url_header=?, canonical_url_html=?;"""
    
    data = ("33a64df551425fcc55e4d42a148795d9f25f89d4", 200, "Google", "https://www.google.com", "https://www.google.com")
    
    db.execute_query(insert_data_query, data=data)

    select_data_query = """
    SELECT * FROM urls;
    """
    data = db.fetch_data(select_data_query)
    print(data)

    data = db.fetch_data(select_data_query)
    print(data)

    

    db.disconnect()