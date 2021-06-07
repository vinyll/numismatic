import sqlite3
import time
from uuid import uuid4


def init():
  con = sqlite3.connect('bsl.db')
  cur = con.cursor()
  return con, cur


def create_tables():
  con, cur = init()
  try:
    cur.execute("""
      CREATE TABLE users (
        id integer primary key autoincrement,
        firstname text,
        lastname text,
        date integer,
        email text,
        password text,
        credit integer
      )
    """)
  except sqlite3.OperationalError:
    pass

  try:
    cur.execute("""
      CREATE TABLE transactions (
        uid text primary key,
        sender integer,
        recipient integer,
        amount text,
        date integer,
        status text
      )
    """)
  except sqlite3.OperationalError:
    pass

  con.commit()


def get_user(id):
  con, cur = init()
  query = f"SELECT * from users WHERE id={id} LIMIT 1"
  cur.execute(query)
  return cur.fetchone()


def create_user(firstname, lastname, email, password):
  con, cur = init()
  q = f"INSERT INTO users VALUES (null, '{firstname}', '{lastname}', {int(time.time())}, '{email}', '{password}', 0)"
  cur.execute(q)
  con.commit()


def get_transaction(id):
  con, cur = init()
  query = f"SELECT * from transactions WHERE uid='{id}' LIMIT 1"
  cur.execute(query)
  return cur.fetchone()


def create_transaction(sender_id, amount):
  con, cur = init()
  uid = str(uuid4())
  q = f"INSERT INTO transactions VALUES ('{uid}', {sender_id}, null, {amount}, {int(time.time())}, 'pending')"
  cur.execute(q)
  con.commit()
  return uid


def complete_transaction(uid, recipient_id):
  con, cur = init()
  q = f"UPDATE transactions SET status='complete', recipient={recipient_id}, date={int(time.time())} WHERE uid='{uid}' AND status='pending'"
  cur.execute(q)
  con.commit()


def update_credit(id, credit):
  con, cur = init()
  user = get_user(id)
  q = f"UPDATE users SET credit={credit} WHERE id={id}"

  cur.execute(q)
  con.commit()


def transfer_credit(sender_id, recipient_id, amount):
    amount = int(amount)
    if not 0 < amount < 1000:
        raise Exception(f"The amount must be between 1 and 1000. {amount} is not valid.")
    
    sender = get_user(sender_id)
    if not sender:
        raise Exception("You must be authenticated to commit a transaction.")

    recipient = get_user(recipient_id)
    if not recipient:
        raise Exception("You must be authenticated to commit a transaction.")
    new_credit = recipient[6] + amount
    import ipdb; ipdb.set_trace()
    update_credit(sender_id, sender[6] - amount)
    update_credit(recipient_id, new_credit)
