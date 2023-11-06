import threading, random
from . import SESSION, BASE
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    UnicodeText,
    UniqueConstraint,
    func,
)
from sqlalchemy.sql.sqltypes import BigInteger

class sess(BASE):
    __tablename__ = "sessions"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer)

    def __init__(self, id, user_id, type):
        self.id = id
        self.user_id = user_id

    def __repr__(self):
        return "<msg: {}, user {}>".format(self.id, self.user_id)

sess.__table__.create(checkfirst=True)
ILOCK = threading.RLock()

def save(id, user_id): 
   SESSION.add(sess(id, user_id))
   SESSION.commit()

def remove(id):
    with ILOCK:
        fuk = SESSION.query(sess).get(id)
        if fuk:
            SESSION.delete(fuk)
            SESSION.commit()
        else:
            SESSION.close()

def check(id):
    try:
        return SESSION.query(sess).filter(sess.id == str(id)).one()
    except BaseException:
        return None
    finally:
        SESSION.close()

def get_data():
    try:
        return SESSION.query(sess).all()
    finally:
        SESSION.close()

def get_list():
    try:
       return SESSION.query(sess.id).all()
       #return list(result) #.scalar() 
       #return [item[0] for item in result]  
    finally:
       SESSION.close()
 
def count():
    try:
        return SESSION.query(sess).count()
    finally:
        SESSION.close()
