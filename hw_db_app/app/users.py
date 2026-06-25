import sqlite3
from datetime import datetime
from schemas.users import User

def add_user(db, username, password):
    cur = db.cursor()
    query = """INSERT INTO "users" (username, password, score, created_at) 
    VALUES (?, ?, ?, ?)
    RETURNING id
    """

    try:
        cur.execute(query,
                    (username, password, 0, datetime.now()))
        user_id = cur.fetchone()

        db.commit()
    except sqlite3.IntegrityError as e:
        print(e)
        return False

    if user_id:
        return user_id[0]
    else:
        return False


def login_user(db, username, password):
    cur = db.cursor()
    query = """SELECT id, username, score FROM "users"
    WHERE username = ?
    AND password = ?
    """
    cur.execute(query, (username, password))
    user = cur.fetchone()
    if user:
        return User(id=user[0], username=user[1], score=user[2])
    else:
        return None

def edit_user_score(db, user_id, score):
    cur = db.cursor()
    query = """
    UPDATE users SET
    score = score + ?
    WHERE id = ?
    """
    cur.execute(query, (score, user_id))
    db.commit()

def get_users_top(db):
    cur = db.cursor()
    query = """SELECT id, username, score FROM 'users' 
                ORDER BY score DESC"""
    cur.execute(query)
    users = cur.fetchall()

    users = [User(id=user[0], username=user[1], score=user[2]) for user in users]
    return users
