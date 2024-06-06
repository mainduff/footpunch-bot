import sqlite3

# Initialize database connection
def init_db():
    conn = sqlite3.connect('footpunch_bot.db')
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER,
        referrals INTEGER,
        referral_code TEXT,
        boost_claimed BOOLEAN,
        tasks_subscribe BOOLEAN,
        tasks_invite_1 BOOLEAN,
        tasks_invite_5 BOOLEAN,
        tasks_invite_10 BOOLEAN,
        tasks_invite_50 BOOLEAN,
        tasks_invite_100 BOOLEAN,
        tasks_nickname BOOLEAN
    )
    ''')
    # Create referral codes usage table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS used_referral_codes (
        ref_code TEXT,
        user_id INTEGER,
        PRIMARY KEY (ref_code, user_id)
    )
    ''')
    conn.commit()
    conn.close()

# Save user data to the database
def save_user_data(user_id, user_data):
    conn = sqlite3.connect('footpunch_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO users (user_id, username, balance, referrals, referral_code, boost_claimed, tasks_subscribe, tasks_invite_1, tasks_invite_5, tasks_invite_10, tasks_invite_50, tasks_invite_100, tasks_nickname)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, user_data['username'], user_data['balance'], user_data['referrals'], user_data['referral_code'],
        user_data['boost_claimed'], user_data['tasks']['subscribe'], user_data['tasks']['invite_1'],
        user_data['tasks']['invite_5'], user_data['tasks']['invite_10'], user_data['tasks']['invite_50'],
        user_data['tasks']['invite_100'], user_data['tasks']['nickname']
    ))
    conn.commit()
    conn.close()

# Load user data from the database
def load_user_data(user_id):
    conn = sqlite3.connect('footpunch_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'username': row[1],
            'balance': row[2],
            'referrals': row[3],
            'referral_code': row[4],
            'boost_claimed': row[5],
            'tasks': {
                'subscribe': row[6],
                'invite_1': row[7],
                'invite_5': row[8],
                'invite_10': row[9],
                'invite_50': row[10],
                'invite_100': row[11],
                'nickname': row[12],
            }
        }
    return None

# Save used referral codes to the database
def save_used_referral_code(ref_code, user_id):
    conn = sqlite3.connect('footpunch_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO used_referral_codes (ref_code, user_id)
    VALUES (?, ?)
    ''', (ref_code, user_id))
    conn.commit()
    conn.close()

# Load used referral codes from the database
def load_used_referral_codes():
    conn = sqlite3.connect('footpunch_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM used_referral_codes')
    rows = cursor.fetchall()
    conn.close()
    used_referral_codes = {}
    for row in rows:
        if row[0] not in used_referral_codes:
            used_referral_codes[row[0]] = set()
        used_referral_codes[row[0]].add(row[1])
    return used_referral_codes

# Load all user data from the database
def load_all_user_data():
    conn = sqlite3.connect('footpunch_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    conn.close()
    all_user_data = {}
    for row in rows:
        all_user_data[row[0]] = {
            'username': row[1],
            'balance': row[2],
            'referrals': row[3],
            'referral_code': row[4],
            'boost_claimed': row[5],
            'tasks': {
                'subscribe': row[6],
                'invite_1': row[7],
                'invite_5': row[8],
                'invite_10': row[9],
                'invite_50': row[10],
                'invite_100': row[11],
                'nickname': row[12],
            }
        }
    return all_user_data
