import threading
from . import BASE, SESSION
from sqlalchemy import Boolean, Column, Integer, UnicodeText, BigInteger

class SELLERS(BASE):
    __tablename__ = "sellers"

    user_id = Column(BigInteger, primary_key=True)
    amount = Column(Integer, default=0)
    ids = Column(Integer, default=0)
    sold = Column(Integer, default=0)

    def __init__(self, user_id, amount=0, ids=0, sold=0):
        self.user_id = user_id
        self.amount = amount
        self.ids = ids
        self.sold = sold

    def __repr__(self):
        return "User > {}".format(self.user_id)

    def to_dict(self):
        return {'user_id': self.user_id, 'amount': self.amount, 'ids': self.ids, 'sold': self.sold}

SELLERS.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

def add(user_id):
   Check = SESSION.query(SELLERS).get(int(user_id))
   if not Check:
      SESSION.add(SELLERS(user_id, 0, 0, 0))
      SESSION.commit()
   else:
      SESSION.close()

def remove(user_id):
    with INSERTION_LOCK:
        user = SESSION.query(SELLERS).get(user_id)
        if user:
            SESSION.delete(user)
            SESSION.commit()
        else:
            SESSION.close()

def sell(user_id):
   check = SESSION.query(SELLERS).get(int(user_id))
   old_amount = check.amount
   old_ids = check.ids
   old_sold = check.sold
   new_amount = int(int(old_amount) + 13)
   new_ids = int(int(old_ids) - 1)
   new_sold = int(int(old_sold) + 1)
   check.amount = new_amount
   check.ids = new_ids
   check.sold = new_sold
   SESSION.merge(check)
   SESSION.commit()
   return new_amount

def new(user_id):
   check = SESSION.query(SELLERS).get(int(user_id))
   old_ids = check.ids
   new_ids = int(int(old_ids) + 1)
   check.ids = new_ids
   SESSION.merge(check)
   SESSION.commit()

def withdraw(user_id, rs):
   check = SESSION.query(SELLERS).get(int(user_id))
   old = check.amount
   remain = int(int(old) - int(rs))
   check.amount = remain
   SESSION.merge(check)
   SESSION.commit()
   return remain

def less_id(user_id):
   check = SESSION.query(SELLERS).get(int(user_id))
   old_ids = check.ids
   new_ids = int(int(old_ids) - 1)
   check.ids = new_ids
   SESSION.merge(check)
   SESSION.commit()

def count():
    try:
        return SESSION.query(SELLERS).count()
    finally:
        SESSION.close()

def get_all_SELLERS():
    try:
        return SESSION.query(SELLERS).all()
    finally:
        SESSION.close()

def check(user_id):
    try:
        return SESSION.query(SELLERS).filter(SELLERS.user_id == str(user_id)).one()
    except BaseException:
        return None
    finally:
        SESSION.close()