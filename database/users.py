import threading
from . import BASE, SESSION
from sqlalchemy import Boolean, Column, Integer, UnicodeText, BigInteger


class USERS(BASE):
    __tablename__ = "ACE-users"

    user_id = Column(BigInteger, primary_key=True)
    deposit = Column(Integer, default=0)
    orders = Column(Integer, default=0)

    def __init__(self, user_id, deposit=0, orders=0):
        self.user_id = user_id
        self.deposit = deposit
        self.orders = orders

    def __repr__(self):
        return "User > {}".format(self.user_id)

    def to_dict(self):
        return {'user_id': self.user_id, 'deposit': self.deposit, 'orders': self.orders}

USERS.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

def adduser(user_id):
   Check = SESSION.query(USERS).get(int(user_id))
   if not Check:
      SESSION.add(USERS(user_id, 0, 0))
      SESSION.commit()
   else:
      SESSION.close()

def update_deposit(user_id, amount):
   check = SESSION.query(USERS).get(int(user_id))
   if not check:
      SESSION.add(USERS(user_id, amount, 0))
      SESSION.commit()
   else:
      old_amount = check.deposit
      new_amount = int(int(old_amount) + int(amount))
      check.deposit = new_amount
      SESSION.merge(check)
      SESSION.commit()
      return new_amount

def take_deposit(user_id, amount):
   check = SESSION.query(USERS).get(int(user_id))
   old_amount = check.deposit
   new_amount = int(int(old_amount) - int(amount))
   check.deposit = new_amount
   SESSION.merge(check)
   SESSION.commit()
   return new_amount

def add_order(user_id):
   check = SESSION.query(USERS).get(int(user_id))
   if not check:
      SESSION.add(USERS(user_id, 0, 0, 1))
      SESSION.commit()
   else:
      old = check.orders
      new = int(int(old) + 1)
      check.orders = new
      SESSION.merge(check)
      SESSION.commit()
      return new

def charge_price(user_id):
   check = SESSION.query(USERS).get(int(user_id))
   old_amount = check.deposit
   new_amount = int(int(old_amount) - 16)
   check.deposit = new_amount
   new = int(int(check.orders) + 1)
   check.orders = new
   SESSION.merge(check)
   SESSION.commit()
   return new_amount

def count():
    try:
        return SESSION.query(USERS).count()
    finally:
        SESSION.close()

def get_all_users():
    try:
        return SESSION.query(USERS).all()
    finally:
        SESSION.close()

def check(user_id):
    try:
        return SESSION.query(USERS).filter(USERS.user_id == str(user_id)).one()
    except BaseException:
        return None
    finally:
        SESSION.close()
