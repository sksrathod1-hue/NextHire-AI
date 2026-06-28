import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import Config

DB_PATH = os.path.join(os.path.dirname(__file__), 'nexthire.db')

# MySQL cursor and connection wrappers to match SQLite query interface style
class MySQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        
    def fetchone(self):
        return self.cursor.fetchone()
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    @property
    def lastrowid(self):
        return self.cursor.lastrowid

class MySQLConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        
    def execute(self, sql, parameters=None):
        # Convert SQLite '?' parameter placeholder to PyMySQL '%s' placeholder
        if parameters:
            sql = sql.replace('?', '%s')
        cursor = self.conn.cursor()
        cursor.execute(sql, parameters)
        return MySQLCursorWrapper(cursor)
        
    def cursor(self):
        return MySQLCursorWrapper(self.conn.cursor())
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_db_connection():
    if Config.MYSQL_HOST:
        import pymysql
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )
        return MySQLConnectionWrapper(conn)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    
    if Config.MYSQL_HOST:
        # MySQL Schemas
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fullname VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            college VARCHAR(255),
            google_id VARCHAR(255),
            avatar_url VARCHAR(512),
            target_role VARCHAR(100) DEFAULT 'Frontend Engineer',
            experience_lvl VARCHAR(50) DEFAULT 'Mid',
            difficulty VARCHAR(50) DEFAULT 'Medium'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            ats_score INT NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role VARCHAR(100) NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            score INT,
            strengths TEXT,
            corrections TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_subscribers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
    else:
        # SQLite Schemas
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            college TEXT,
            google_id TEXT,
            avatar_url TEXT,
            is_admin INTEGER DEFAULT 0,
            target_role TEXT DEFAULT 'Frontend Engineer',
            experience_lvl TEXT DEFAULT 'Mid',
            difficulty TEXT DEFAULT 'Medium'
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            ats_score INTEGER NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            score INTEGER,
            strengths TEXT,
            corrections TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Unread',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

    # Run manual migration checks for SQLite/MySQL to ensure column parity
    if not Config.MYSQL_HOST:
        try:
            conn.execute("SELECT google_id FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
            conn.commit()
        try:
            conn.execute("SELECT avatar_url FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
            conn.commit()
        try:
            conn.execute("SELECT is_admin FROM users LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            conn.commit()
        try:
            conn.execute("SELECT status FROM contact_messages LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE contact_messages ADD COLUMN status TEXT DEFAULT 'Unread'")
            conn.commit()
        try:
            conn.execute("SELECT created_at FROM contact_messages LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE contact_messages ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
    else:
        try:
            conn.execute("SELECT is_admin FROM users LIMIT 1")
        except Exception:
            try:
                conn.execute("ALTER TABLE users ADD COLUMN is_admin INT DEFAULT 0")
            except Exception:
                pass
        try:
            conn.execute("SELECT status FROM contact_messages LIMIT 1")
        except Exception:
            try:
                conn.execute("ALTER TABLE contact_messages ADD COLUMN status VARCHAR(50) DEFAULT 'Unread'")
            except Exception:
                pass
        try:
            conn.execute("SELECT created_at FROM contact_messages LIMIT 1")
        except Exception:
            try:
                conn.execute("ALTER TABLE contact_messages ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except Exception:
                pass

    # Seed initial test rows if database has no registered users
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users')
    row = cursor.fetchone()
    
    # SQLite returns sqlite3.Row, MySQLCursorWrapper returns Dict
    count = row['count'] if isinstance(row, dict) or hasattr(row, '__getitem__') and not isinstance(row, tuple) else row[0]
    
    if count == 0:
        cursor.execute('''
        INSERT INTO users (fullname, email, password, phone, college, target_role, experience_lvl, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'John Doe',
            'john@domain.com',
            generate_password_hash('password123'),
            '+1 (555) 019-2834',
            'Stanford University',
            'Lead AI Architect',
            'Senior',
            'Hard'
        ))
        
        cursor.execute('''
        INSERT INTO users (fullname, email, password, phone, college, target_role, experience_lvl, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Sarah Connor',
            'sarah@sky.net',
            generate_password_hash('cyberdyne'),
            '+1 (555) 900-1000',
            'University of California',
            'Frontend Architect',
            'Senior',
            'Hard'
        ))
        
        # Seed default resume for User 1
        cursor.execute('''
        INSERT INTO resumes (user_id, filename, ats_score, matched_skills, missing_skills, recommendations)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            1,
            'John_Doe_CV.pdf',
            92,
            'Python, React, SQL, Git, HTML, CSS',
            'Docker, AWS',
            'Increase action verbs frequency. Add Docker and cloud-related deployment tools.'
        ))

        # Seed default interview for User 1
        cursor.execute('''
        INSERT INTO interviews (user_id, role, question, answer, score, strengths, corrections)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,
            'Lead AI Architect',
            'How do you optimize model latency constraints when serving public API inferences?',
            'We can utilize model quantization and model caching at the edge using CDN services.',
            85,
            'Strong structural overview of edge scaling concepts.',
            'Reference network latencies, model replication pipelines, and vector databases.'
        ))

    # Automatically promote default admin user
    try:
        conn.execute("UPDATE users SET is_admin = 1 WHERE email = 'sksrathod1@gmail.com'")
        conn.commit()
    except Exception as e:
        print(f"Failed to auto-promote admin: {e}")

    conn.commit()
    conn.close()

# Run initialization
init_db()
