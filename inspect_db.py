import sqlite3
import os

# Connect relative to script location
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'nexthire.db')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # Return cursor rows as dictionaries for clean key lookups
    conn.row_factory = sqlite3.Row
    return conn

def view_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print("\n--- DATABASE TABLES ---")
    for t in tables:
        print(f"• {t['name']}")
    conn.close()

def view_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, fullname, email, is_admin FROM users;")
    rows = c.fetchall()
    print("\n--- REGISTERED USERS ---")
    print(f"{'ID':<5} {'Name':<15} {'Email':<25} {'Is Admin':<10}")
    print("-" * 60)
    for r in rows:
        print(f"{r['id']:<5} {r['fullname']:<15} {r['email']:<25} {r['is_admin']:<10}")
    conn.close()

def view_resumes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, user_id, score, matched_skills FROM resume_analysis LIMIT 10;")
    rows = c.fetchall()
    print("\n--- RESUME ANALYSIS SCORES (Last 10) ---")
    print(f"{'ID':<5} {'User ID':<10} {'Score':<8} {'Matched Skills (Partial)':<40}")
    print("-" * 75)
    for r in rows:
        skills = r['matched_skills'][:40] + "..." if len(r['matched_skills']) > 40 else r['matched_skills']
        print(f"{r['id']:<5} {r['user_id']:<10} {r['score']:<8} {skills:<40}")
    conn.close()

def custom_query():
    print("\nEnter custom SQL query (e.g. SELECT * FROM contact_messages;):")
    query = input("sql> ").strip()
    if not query:
        return
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        if not rows:
            print("No records returned.")
            conn.close()
            return
            
        headers = rows[0].keys()
        print("\n--- QUERY RESULTS ---")
        print(" | ".join(headers))
        print("-" * 60)
        for r in rows:
            print(" | ".join(str(r[key]) for key in headers))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def main():
    clear_screen()
    while True:
        print("=========================================")
        print("   NextHire AI Database Inspector Tool   ")
        print("=========================================")
        print("1. View list of tables")
        print("2. View registered candidates (Users)")
        print("3. View resume analysis scores")
        print("4. Run a custom SQL query")
        print("5. Exit")
        print("=========================================")
        
        choice = input("Enter choice (1-5): ").strip()
        if choice == "1":
            view_tables()
        elif choice == "2":
            view_users()
        elif choice == "3":
            view_resumes()
        elif choice == "4":
            custom_query()
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid selection.")
        
        input("\nPress Enter to return to menu...")
        clear_screen()

if __name__ == "__main__":
    main()
