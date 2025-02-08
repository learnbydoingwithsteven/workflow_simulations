from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    reference = Column(String(50), unique=True)
    sender_name = Column(String(100))
    sender_account = Column(String(50))
    receiver_name = Column(String(100))
    receiver_account = Column(String(50))
    amount = Column(Float)
    currency = Column(String(3))
    purpose = Column(String(500))
    status = Column(String(20))
    llm_screening_result = Column(String(1000))
    created_at = Column(DateTime, default=datetime.now)
    processed_at = Column(DateTime, nullable=True)
    is_high_risk = Column(Boolean, default=False)

class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///payments.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_payment(self, payment_data):
        payment = Payment(**payment_data)
        self.session.add(payment)
        self.session.commit()
        return payment
    
    def update_payment_status(self, reference, status, processed_at=None):
        payment = self.session.query(Payment).filter_by(reference=reference).first()
        if payment:
            payment.status = status
            if processed_at:
                payment.processed_at = processed_at
            self.session.commit()
            return True
        return False
    
    def get_payment(self, reference):
        return self.session.query(Payment).filter_by(reference=reference).first()
    
    def get_all_payments(self):
        return self.session.query(Payment).all() 