# database.py

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

class Transaction(Base):
    """SQLAlchemy model for fraud detection transactions"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(100))
    amount = Column(Float, nullable=False)
    merchant = Column(String(200))
    merchant_category = Column(String(50))
    transaction_type = Column(String(20))
    location = Column(String(200))
    timestamp = Column(DateTime, nullable=False, index=True)
    account_type = Column(String(20))
    customer_risk_profile = Column(String(20))
    template_risk_level = Column(String(20))
    is_suspicious_template = Column(Boolean, default=False)
    manual_entry = Column(Boolean, default=False)
    
    # Fraud analysis results
    fraud_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default='low')
    status = Column(String(20), default='pending')  # pending, approved, flagged, blocked
    fraud_indicators = Column(Text)  # JSON string of indicators
    analysis_method = Column(String(30), default='rule_based')
    ai_confidence = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount={self.amount}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'amount': self.amount,
            'merchant': self.merchant,
            'merchant_category': self.merchant_category,
            'transaction_type': self.transaction_type,
            'location': self.location,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'account_type': self.account_type,
            'customer_risk_profile': self.customer_risk_profile,
            'template_risk_level': self.template_risk_level,
            'is_suspicious_template': self.is_suspicious_template,
            'manual_entry': self.manual_entry,
            'fraud_score': self.fraud_score,
            'risk_level': self.risk_level,
            'status': self.status,
            'fraud_indicators': self.fraud_indicators,
            'analysis_method': self.analysis_method,
            'ai_confidence': self.ai_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FraudAlert(Base):
    """SQLAlchemy model for fraud alerts"""
    __tablename__ = 'fraud_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(50), unique=True, nullable=False)
    transaction_id = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # high_risk, pattern_match, velocity, etc.
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    description = Column(Text)
    status = Column(String(20), default='open')  # open, investigating, resolved, false_positive
    assigned_to = Column(String(100))  # Analyst assigned to investigate
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    def __repr__(self):
        return f"<FraudAlert(id={self.alert_id}, type={self.alert_type}, severity={self.severity})>"

class CustomerProfile(Base):
    """SQLAlchemy model for customer profiles and behavior patterns"""
    __tablename__ = 'customer_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(20), unique=True, nullable=False, index=True)
    customer_name = Column(String(100))
    account_type = Column(String(20))
    risk_profile = Column(String(20), default='medium')
    
    # Behavioral patterns
    avg_monthly_spending = Column(Float, default=0.0)
    typical_locations = Column(Text)  # JSON string of typical locations
    typical_merchants = Column(Text)  # JSON string of typical merchant categories
    typical_transaction_times = Column(Text)  # JSON string of typical hours
    
    # Account information
    account_opened = Column(DateTime)
    last_activity = Column(DateTime)
    total_transactions = Column(Integer, default=0)
    
    # Risk indicators
    fraud_history = Column(Boolean, default=False)
    high_risk_flags = Column(Text)  # JSON string of risk flags
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CustomerProfile(id={self.customer_id}, name={self.customer_name}, risk={self.risk_profile})>"

class Database:
    """Database manager for fraud detection system"""
    
    def __init__(self, db_path: str = "fraud_detection.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self._create_tables()
        
        logger.info(f"Database initialized: {db_path}")
    
    def _create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Add a new transaction to the database"""
        session = self.get_session()
        try:
            # Parse timestamp
            timestamp_str = transaction_data.get('timestamp')
            if isinstance(timestamp_str, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            # Convert fraud indicators to JSON string
            fraud_indicators = transaction_data.get('fraud_indicators', [])
            if isinstance(fraud_indicators, list):
                fraud_indicators_str = ','.join(fraud_indicators)
            else:
                fraud_indicators_str = str(fraud_indicators) if fraud_indicators else ''
            
            # Create transaction object
            transaction = Transaction(
                transaction_id=transaction_data.get('transaction_id'),
                customer_id=transaction_data.get('customer_id'),
                customer_name=transaction_data.get('customer_name'),
                amount=float(transaction_data.get('amount', 0)),
                merchant=transaction_data.get('merchant'),
                merchant_category=transaction_data.get('merchant_category'),
                transaction_type=transaction_data.get('transaction_type'),
                location=transaction_data.get('location'),
                timestamp=timestamp,
                account_type=transaction_data.get('account_type'),
                customer_risk_profile=transaction_data.get('customer_risk_profile'),
                template_risk_level=transaction_data.get('template_risk_level'),
                is_suspicious_template=transaction_data.get('is_suspicious_template', False),
                manual_entry=transaction_data.get('manual_entry', False),
                fraud_score=float(transaction_data.get('fraud_score', 0)),
                risk_level=transaction_data.get('risk_level', 'low'),
                status=transaction_data.get('status', 'pending'),
                fraud_indicators=fraud_indicators_str,
                analysis_method=transaction_data.get('analysis_method', 'rule_based'),
                ai_confidence=float(transaction_data.get('ai_confidence', 0))
            )
            
            session.add(transaction)
            session.commit()
            
            logger.debug(f"Transaction {transaction_data.get('transaction_id')} added to database")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding transaction: {str(e)}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding transaction: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by its ID"""
        session = self.get_session()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.transaction_id == transaction_id
            ).first()
            return transaction
        except Exception as e:
            logger.error(f"Error getting transaction {transaction_id}: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_transactions(self, limit: int = 100, offset: int = 0) -> List[Transaction]:
        """Get all transactions with pagination"""
        session = self.get_session()
        try:
            transactions = session.query(Transaction).order_by(
                Transaction.timestamp.desc()
            ).offset(offset).limit(limit).all()
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_flagged_transactions(self, limit: int = 100) -> List[Transaction]:
        """Get transactions flagged for fraud"""
        session = self.get_session()
        try:
            transactions = session.query(Transaction).filter(
                Transaction.status == 'flagged'
            ).order_by(Transaction.timestamp.desc()).limit(limit).all()
            return transactions
        except Exception as e:
            logger.error(f"Error getting flagged transactions: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_high_risk_transactions(self, limit: int = 100) -> List[Transaction]:
        """Get high-risk transactions"""
        session = self.get_session()
        try:
            transactions = session.query(Transaction).filter(
                Transaction.risk_level.in_(['high', 'critical'])
            ).order_by(Transaction.fraud_score.desc()).limit(limit).all()
            return transactions
        except Exception as e:
            logger.error(f"Error getting high-risk transactions: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_customer_transactions(self, customer_id: str, limit: int = 50) -> List[Transaction]:
        """Get transactions for a specific customer"""
        session = self.get_session()
        try:
            transactions = session.query(Transaction).filter(
                Transaction.customer_id == customer_id
            ).order_by(Transaction.timestamp.desc()).limit(limit).all()
            return transactions
        except Exception as e:
            logger.error(f"Error getting customer transactions: {str(e)}")
            return []
        finally:
            session.close()
    
    def update_transaction_status(self, transaction_id: str, status: str, notes: str = None) -> bool:
        """Update transaction status"""
        session = self.get_session()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.transaction_id == transaction_id
            ).first()
            
            if transaction:
                transaction.status = status
                transaction.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Transaction {transaction_id} status updated to {status}")
                return True
            else:
                logger.warning(f"Transaction {transaction_id} not found for status update")
                return False
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating transaction status: {str(e)}")
            return False
        finally:
            session.close()
    
    def add_fraud_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Add a fraud alert"""
        session = self.get_session()
        try:
            alert = FraudAlert(
                alert_id=alert_data.get('alert_id'),
                transaction_id=alert_data.get('transaction_id'),
                alert_type=alert_data.get('alert_type'),
                severity=alert_data.get('severity', 'medium'),
                description=alert_data.get('description'),
                status=alert_data.get('status', 'open'),
                assigned_to=alert_data.get('assigned_to')
            )
            
            session.add(alert)
            session.commit()
            
            logger.info(f"Fraud alert {alert_data.get('alert_id')} added")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding fraud alert: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_fraud_alerts(self, status: str = None, limit: int = 100) -> List[FraudAlert]:
        """Get fraud alerts"""
        session = self.get_session()
        try:
            query = session.query(FraudAlert)
            
            if status:
                query = query.filter(FraudAlert.status == status)
            
            alerts = query.order_by(FraudAlert.created_at.desc()).limit(limit).all()
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting fraud alerts: {str(e)}")
            return []
        finally:
            session.close()
    
    def add_customer_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Add or update customer profile"""
        session = self.get_session()
        try:
            # Check if profile exists
            existing_profile = session.query(CustomerProfile).filter(
                CustomerProfile.customer_id == profile_data.get('customer_id')
            ).first()
            
            if existing_profile:
                # Update existing profile
                for key, value in profile_data.items():
                    if hasattr(existing_profile, key):
                        setattr(existing_profile, key, value)
                existing_profile.updated_at = datetime.utcnow()
            else:
                # Create new profile
                profile = CustomerProfile(**profile_data)
                session.add(profile)
            
            session.commit()
            logger.info(f"Customer profile {profile_data.get('customer_id')} updated")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding customer profile: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get customer profile"""
        session = self.get_session()
        try:
            profile = session.query(CustomerProfile).filter(
                CustomerProfile.customer_id == customer_id
            ).first()
            return profile
        except Exception as e:
            logger.error(f"Error getting customer profile: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud detection statistics"""
        session = self.get_session()
        try:
            # Total transactions
            total_transactions = session.query(Transaction).count()
            
            # Flagged transactions
            flagged_transactions = session.query(Transaction).filter(
                Transaction.status == 'flagged'
            ).count()
            
            # High-risk transactions
            high_risk_transactions = session.query(Transaction).filter(
                Transaction.risk_level.in_(['high', 'critical'])
            ).count()
            
            # Average fraud score
            avg_fraud_score = session.query(Transaction).with_entities(
                Transaction.fraud_score
            ).all()
            
            if avg_fraud_score:
                avg_score = sum(score[0] for score in avg_fraud_score) / len(avg_fraud_score)
            else:
                avg_score = 0
            
            # Transactions by risk level
            risk_level_counts = {}
            for risk_level in ['very_low', 'low', 'medium', 'high', 'critical']:
                count = session.query(Transaction).filter(
                    Transaction.risk_level == risk_level
                ).count()
                risk_level_counts[risk_level] = count
            
            # Recent activity (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.now() - timedelta(days=1)
            recent_transactions = session.query(Transaction).filter(
                Transaction.timestamp >= yesterday
            ).count()
            
            recent_flagged = session.query(Transaction).filter(
                Transaction.timestamp >= yesterday,
                Transaction.status == 'flagged'
            ).count()
            
            statistics = {
                'total_transactions': total_transactions,
                'flagged_transactions': flagged_transactions,
                'high_risk_transactions': high_risk_transactions,
                'average_fraud_score': round(avg_score, 2),
                'fraud_rate': round((flagged_transactions / total_transactions * 100), 2) if total_transactions > 0 else 0,
                'risk_level_distribution': risk_level_counts,
                'recent_activity': {
                    'transactions_24h': recent_transactions,
                    'flagged_24h': recent_flagged
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting fraud statistics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def search_transactions(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[Transaction]:
        """Search transactions based on criteria"""
        session = self.get_session()
        try:
            query = session.query(Transaction)
            
            # Apply search filters
            if 'customer_id' in search_criteria:
                query = query.filter(Transaction.customer_id == search_criteria['customer_id'])
            
            if 'amount_min' in search_criteria:
                query = query.filter(Transaction.amount >= search_criteria['amount_min'])
            
            if 'amount_max' in search_criteria:
                query = query.filter(Transaction.amount <= search_criteria['amount_max'])
            
            if 'risk_level' in search_criteria:
                query = query.filter(Transaction.risk_level == search_criteria['risk_level'])
            
            if 'status' in search_criteria:
                query = query.filter(Transaction.status == search_criteria['status'])
            
            if 'merchant_category' in search_criteria:
                query = query.filter(Transaction.merchant_category == search_criteria['merchant_category'])
            
            if 'date_from' in search_criteria:
                query = query.filter(Transaction.timestamp >= search_criteria['date_from'])
            
            if 'date_to' in search_criteria:
                query = query.filter(Transaction.timestamp <= search_criteria['date_to'])
            
            transactions = query.order_by(Transaction.timestamp.desc()).limit(limit).all()
            return transactions
            
        except Exception as e:
            logger.error(f"Error searching transactions: {str(e)}")
            return []
        finally:
            session.close()
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> bool:
        """Clean up old transaction data"""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old transactions (keep flagged ones)
            deleted_count = session.query(Transaction).filter(
                Transaction.timestamp < cutoff_date,
                Transaction.status != 'flagged'
            ).delete()
            
            session.commit()
            logger.info(f"Cleaned up {deleted_count} old transactions")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error cleaning up old data: {str(e)}")
            return False
        finally:
            session.close()

# Example usage and testing
if __name__ == "__main__":
    # Test the database
    db = Database("test_fraud_detection.db")
    
    # Test transaction data
    test_transaction = {
        'transaction_id': 'TEST001',
        'customer_id': 'CUST001',
        'customer_name': 'Test Customer',
        'amount': 100.50,
        'merchant': 'Test Merchant',
        'merchant_category': 'grocery',
        'transaction_type': 'purchase',
        'location': 'Test City',
        'timestamp': datetime.now().isoformat(),
        'account_type': 'standard',
        'fraud_score': 25.5,
        'risk_level': 'low',
        'status': 'approved',
        'fraud_indicators': ['test_indicator'],
        'analysis_method': 'rule_based'
    }
    
    try:
        # Add transaction
        success = db.add_transaction(test_transaction)
        print(f"Add transaction: {'Success' if success else 'Failed'}")
        
        # Get transaction
        retrieved = db.get_transaction_by_id('TEST001')
        print(f"Retrieved transaction: {retrieved.transaction_id if retrieved else 'Not found'}")
        
        # Get statistics
        stats = db.get_fraud_statistics()
        print(f"Statistics: {stats}")
        
        print("Database test completed")
        
    except Exception as e:
        print(f"Database test error: {e}")