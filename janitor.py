import psycopg2
from urllib.parse import quote_plus
import os

# --- CONFIGURATION ---

#1. The PIN Secerecy 
DB_URI = os.getenv("DB_PASSWORD")
if not DB_URI:
    raise ValueError(" Error: Database password not found in environment variables.")

# --- JANITOR FUNCTION TO DELETE OLD RECORDS ---

def janitor():
    print(" Running Janitor Script to Clean Database...")
    conn = None
    try:
        #Connecting to the database
        conn = psycopg2.connect(DB_URI, sslmode = "require")
        cur = conn.cursor()

        #Creating the delete query
        delete_query = """
        delete from article
        where created_at < NOW() - interval '30 days';
        """

        #Executing the delete query
        cur.execute(delete_query)
        print(" Old articles deleted successfully.")

        #Committing the changes
        conn.commit()
        print(f" Succsessfully deleted {cur.rowcount} old articles.")

        #Closing the Cursor
        cur.close()

    except Exception as e:
        print(f" Database Error during janitor operation: {e}")
    
    #Closing the connection
    finally:
        if conn:
            conn.close()
            print(" Database connection closed.")

# --- RUNING JANITOR ---

if __name__ == "__main__":
    janitor()