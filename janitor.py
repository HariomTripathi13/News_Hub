import psycopg2
from urllib.parse import quote_plus
import os

# --- CONFIGURATION ---

#1. The PIN Secerecy 
db_pin = os.getenv("DB_PASSWORD")
if not db_pin:
    raise ValueError("❌ Error: Database password not found in environment variables.")

# 2. Password Handling (Password Encoding)
encoded_password = quote_plus(db_pin)

# 3. Connection String (IPv4 Compatible & SSL)
DB_URI = f"postgresql://postgres.furwcwgvvvziblenvhzc:{encoded_password}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"

# --- JANITOR FUNCTION TO DELETE OLD RECORDS ---

def janitor():
    print("🧹 Running Janitor Script to Clean Database...")
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
        print("✅ Old articles deleted successfully.")

        #Committing the changes
        conn.commit()
        print(f" Succsessfully deleted {cur.rowcount} old articles.")

        #Closing the Cursor
        cur.close()

    except Exception as e:
        print(f"   ❌ Database Error during janitor operation: {e}")
    
    #Closing the connection
    finally:
        if conn:
            conn.close()
            print("🔌 Database connection closed.")

# --- RUNING JANITOR ---

if __name__ == "__main__":
    janitor()