from app import db
from config.db import Base

class Call(db.Model):
    __tablename__ = 'calls'

    id = db.Column(db.Integer, primary_key=True)
    from_phone = db.Column(db.String, default='unavailable', nullable=True)
    session_id = db.Column(db.String)
    question = db.Column(db.String)
    answer = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)


    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.updated_at = db.func.now()
        db.session.commit()
    
    def delete(self):
        self.is_deleted = True
        self.updated_at = db.func.now()
        db.session.commit()

    @classmethod
    def get_by_session_id(cls, session_id):
        return cls.query.filter_by(session_id=session_id).order_by(cls.id.desc()).all()
    
    @classmethod
    def create(cls, session_id, question, answer, from_phone=None):
        call = cls(from_phone=from_phone, session_id=session_id, question=question, answer=answer)
        call.save()
        return call
