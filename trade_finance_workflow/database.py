# database.py

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

class TradeFinanceApplication(Base):
    """Trade Finance Application model"""
    __tablename__ = 'trade_finance_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(50), unique=True, nullable=False)
    
    # Company Information
    company_name = Column(String(200), nullable=False)
    company_address = Column(Text)
    company_registration = Column(String(100))
    contact_person = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(50))
    
    # Trade Information
    trade_type = Column(String(100), nullable=False)
    finance_amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    payment_terms = Column(String(100))
    trade_description = Column(Text)
    
    # Counterparty Information
    counterparty_name = Column(String(200))
    counterparty_country = Column(String(100))
    counterparty_address = Column(Text)
    counterparty_bank = Column(String(200))
    
    # Processing Information
    status = Column(String(50), default='submitted')
    priority = Column(String(20), default='normal')
    assigned_officer = Column(String(100))
    
    # AI Screening Results
    ai_screening_result = Column(Text)  # JSON string
    ai_screening_score = Column(Float)
    ai_screening_timestamp = Column(DateTime)
    
    # Document Verification Results
    document_verification_result = Column(Text)  # JSON string
    document_verification_score = Column(Float)
    document_verification_timestamp = Column(DateTime)
    
    # Credit Assessment Results
    credit_assessment_result = Column(Text)  # JSON string
    credit_assessment_score = Column(Float)
    credit_assessment_timestamp = Column(DateTime)
    
    # Compliance Check Results
    compliance_check_result = Column(Text)  # JSON string
    compliance_check_score = Column(Float)
    compliance_check_timestamp = Column(DateTime)
    
    # Risk Analysis Results
    risk_analysis_result = Column(Text)  # JSON string
    risk_analysis_score = Column(Float)
    risk_analysis_timestamp = Column(DateTime)
    
    # Final Decision
    final_decision = Column(String(50))
    final_decision_reason = Column(Text)
    final_decision_timestamp = Column(DateTime)
    decision_maker = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    processed_at = Column(DateTime)
    
    # Additional Fields
    notes = Column(Text)
    risk_level = Column(String(20))
    approval_conditions = Column(Text)
    rejection_reason = Column(Text)
    
class ProcessingStep(Base):
    """Processing step tracking model"""
    __tablename__ = 'processing_steps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(50), nullable=False)
    step_name = Column(String(100), nullable=False)
    step_status = Column(String(50), nullable=False)  # pending, in_progress, completed, failed
    step_result = Column(Text)  # JSON string
    step_score = Column(Float)
    processing_time = Column(Float)  # seconds
    processor = Column(String(100))  # ai, rule_based, manual
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)

class RiskAssessment(Base):
    """Risk assessment model"""
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(50), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # country, counterparty, transaction, overall
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    risk_score = Column(Float, nullable=False)
    risk_factors = Column(Text)  # JSON string
    mitigation_measures = Column(Text)  # JSON string
    assessment_method = Column(String(50))  # ai, rule_based, manual
    assessed_by = Column(String(100))
    assessed_at = Column(DateTime, default=datetime.now)
    valid_until = Column(DateTime)
    notes = Column(Text)

class AuditLog(Base):
    """Audit log model"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    action_details = Column(Text)
    performed_by = Column(String(100), nullable=False)
    performed_at = Column(DateTime, default=datetime.now)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    result = Column(String(50))  # success, failure, warning
    error_message = Column(Text)

class Database:
    """Database management class"""
    
    def __init__(self, db_path: str = "trade_finance.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"Database initialized: {db_path}")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def add_application(self, application_data: Dict[str, Any]) -> bool:
        """Add new trade finance application"""
        try:
            session = self.get_session()
            
            application = TradeFinanceApplication(
                application_id=application_data.get('application_id'),
                company_name=application_data.get('company_name'),
                company_address=application_data.get('company_address'),
                company_registration=application_data.get('company_registration'),
                contact_person=application_data.get('contact_person'),
                contact_email=application_data.get('contact_email'),
                contact_phone=application_data.get('contact_phone'),
                trade_type=application_data.get('trade_type'),
                finance_amount=application_data.get('finance_amount'),
                currency=application_data.get('currency', 'USD'),
                payment_terms=application_data.get('payment_terms'),
                trade_description=application_data.get('trade_description'),
                counterparty_name=application_data.get('counterparty_name'),
                counterparty_country=application_data.get('counterparty_country'),
                counterparty_address=application_data.get('counterparty_address'),
                counterparty_bank=application_data.get('counterparty_bank'),
                status='submitted',
                priority=application_data.get('priority', 'normal'),
                notes=application_data.get('notes')
            )
            
            session.add(application)
            session.commit()
            
            # Add audit log
            self.add_audit_log(
                application_data.get('application_id'),
                'application_submitted',
                f"New trade finance application submitted for {application_data.get('company_name')}",
                'system'
            )
            
            session.close()
            logger.info(f"Application added: {application_data.get('application_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding application: {str(e)}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def update_application(self, application_id: str, updates: Dict[str, Any]) -> bool:
        """Update trade finance application"""
        try:
            session = self.get_session()
            
            application = session.query(TradeFinanceApplication).filter(
                TradeFinanceApplication.application_id == application_id
            ).first()
            
            if not application:
                logger.warning(f"Application not found: {application_id}")
                session.close()
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(application, key):
                    setattr(application, key, value)
            
            application.updated_at = datetime.now()
            session.commit()
            
            # Add audit log
            self.add_audit_log(
                application_id,
                'application_updated',
                f"Application updated: {', '.join(updates.keys())}",
                'system'
            )
            
            session.close()
            logger.info(f"Application updated: {application_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating application: {str(e)}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get trade finance application by ID"""
        try:
            session = self.get_session()
            
            application = session.query(TradeFinanceApplication).filter(
                TradeFinanceApplication.application_id == application_id
            ).first()
            
            if not application:
                session.close()
                return None
            
            # Convert to dictionary
            result = {
                'id': application.id,
                'application_id': application.application_id,
                'company_name': application.company_name,
                'company_address': application.company_address,
                'company_registration': application.company_registration,
                'contact_person': application.contact_person,
                'contact_email': application.contact_email,
                'contact_phone': application.contact_phone,
                'trade_type': application.trade_type,
                'finance_amount': application.finance_amount,
                'currency': application.currency,
                'payment_terms': application.payment_terms,
                'trade_description': application.trade_description,
                'counterparty_name': application.counterparty_name,
                'counterparty_country': application.counterparty_country,
                'counterparty_address': application.counterparty_address,
                'counterparty_bank': application.counterparty_bank,
                'status': application.status,
                'priority': application.priority,
                'assigned_officer': application.assigned_officer,
                'ai_screening_result': self._parse_json_field(application.ai_screening_result),
                'ai_screening_score': application.ai_screening_score,
                'ai_screening_timestamp': application.ai_screening_timestamp,
                'document_verification_result': self._parse_json_field(application.document_verification_result),
                'document_verification_score': application.document_verification_score,
                'document_verification_timestamp': application.document_verification_timestamp,
                'credit_assessment_result': self._parse_json_field(application.credit_assessment_result),
                'credit_assessment_score': application.credit_assessment_score,
                'credit_assessment_timestamp': application.credit_assessment_timestamp,
                'compliance_check_result': self._parse_json_field(application.compliance_check_result),
                'compliance_check_score': application.compliance_check_score,
                'compliance_check_timestamp': application.compliance_check_timestamp,
                'risk_analysis_result': self._parse_json_field(application.risk_analysis_result),
                'risk_analysis_score': application.risk_analysis_score,
                'risk_analysis_timestamp': application.risk_analysis_timestamp,
                'final_decision': application.final_decision,
                'final_decision_reason': application.final_decision_reason,
                'final_decision_timestamp': application.final_decision_timestamp,
                'decision_maker': application.decision_maker,
                'created_at': application.created_at,
                'updated_at': application.updated_at,
                'processed_at': application.processed_at,
                'notes': application.notes,
                'risk_level': application.risk_level,
                'approval_conditions': application.approval_conditions,
                'rejection_reason': application.rejection_reason
            }
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting application: {str(e)}")
            if 'session' in locals():
                session.close()
            return None
    
    def get_applications_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get applications by status"""
        try:
            session = self.get_session()
            
            applications = session.query(TradeFinanceApplication).filter(
                TradeFinanceApplication.status == status
            ).order_by(TradeFinanceApplication.created_at.desc()).limit(limit).all()
            
            results = []
            for app in applications:
                results.append({
                    'application_id': app.application_id,
                    'company_name': app.company_name,
                    'trade_type': app.trade_type,
                    'finance_amount': app.finance_amount,
                    'currency': app.currency,
                    'counterparty_name': app.counterparty_name,
                    'counterparty_country': app.counterparty_country,
                    'status': app.status,
                    'priority': app.priority,
                    'assigned_officer': app.assigned_officer,
                    'created_at': app.created_at,
                    'updated_at': app.updated_at,
                    'risk_level': app.risk_level
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting applications by status: {str(e)}")
            if 'session' in locals():
                session.close()
            return []
    
    def search_applications(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Search applications based on criteria"""
        try:
            session = self.get_session()
            
            query = session.query(TradeFinanceApplication)
            
            # Apply search filters
            if 'company_name' in search_criteria:
                query = query.filter(TradeFinanceApplication.company_name.ilike(f"%{search_criteria['company_name']}%"))
            
            if 'trade_type' in search_criteria:
                query = query.filter(TradeFinanceApplication.trade_type == search_criteria['trade_type'])
            
            if 'status' in search_criteria:
                query = query.filter(TradeFinanceApplication.status == search_criteria['status'])
            
            if 'counterparty_country' in search_criteria:
                query = query.filter(TradeFinanceApplication.counterparty_country == search_criteria['counterparty_country'])
            
            if 'min_amount' in search_criteria:
                query = query.filter(TradeFinanceApplication.finance_amount >= search_criteria['min_amount'])
            
            if 'max_amount' in search_criteria:
                query = query.filter(TradeFinanceApplication.finance_amount <= search_criteria['max_amount'])
            
            if 'date_from' in search_criteria:
                query = query.filter(TradeFinanceApplication.created_at >= search_criteria['date_from'])
            
            if 'date_to' in search_criteria:
                query = query.filter(TradeFinanceApplication.created_at <= search_criteria['date_to'])
            
            applications = query.order_by(TradeFinanceApplication.created_at.desc()).limit(limit).all()
            
            results = []
            for app in applications:
                results.append({
                    'application_id': app.application_id,
                    'company_name': app.company_name,
                    'trade_type': app.trade_type,
                    'finance_amount': app.finance_amount,
                    'currency': app.currency,
                    'counterparty_name': app.counterparty_name,
                    'counterparty_country': app.counterparty_country,
                    'status': app.status,
                    'priority': app.priority,
                    'created_at': app.created_at,
                    'risk_level': app.risk_level
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching applications: {str(e)}")
            if 'session' in locals():
                session.close()
            return []
    
    def add_processing_step(self, step_data: Dict[str, Any]) -> bool:
        """Add processing step record"""
        try:
            session = self.get_session()
            
            step = ProcessingStep(
                application_id=step_data.get('application_id'),
                step_name=step_data.get('step_name'),
                step_status=step_data.get('step_status'),
                step_result=json.dumps(step_data.get('step_result', {})),
                step_score=step_data.get('step_score'),
                processing_time=step_data.get('processing_time'),
                processor=step_data.get('processor'),
                started_at=step_data.get('started_at'),
                completed_at=step_data.get('completed_at'),
                notes=step_data.get('notes')
            )
            
            session.add(step)
            session.commit()
            session.close()
            
            logger.info(f"Processing step added: {step_data.get('application_id')} - {step_data.get('step_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding processing step: {str(e)}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def add_risk_assessment(self, assessment_data: Dict[str, Any]) -> bool:
        """Add risk assessment record"""
        try:
            session = self.get_session()
            
            assessment = RiskAssessment(
                application_id=assessment_data.get('application_id'),
                assessment_type=assessment_data.get('assessment_type'),
                risk_level=assessment_data.get('risk_level'),
                risk_score=assessment_data.get('risk_score'),
                risk_factors=json.dumps(assessment_data.get('risk_factors', [])),
                mitigation_measures=json.dumps(assessment_data.get('mitigation_measures', [])),
                assessment_method=assessment_data.get('assessment_method'),
                assessed_by=assessment_data.get('assessed_by'),
                assessed_at=assessment_data.get('assessed_at', datetime.now()),
                valid_until=assessment_data.get('valid_until'),
                notes=assessment_data.get('notes')
            )
            
            session.add(assessment)
            session.commit()
            session.close()
            
            logger.info(f"Risk assessment added: {assessment_data.get('application_id')} - {assessment_data.get('assessment_type')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding risk assessment: {str(e)}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def add_audit_log(self, application_id: str, action: str, details: str, performed_by: str, result: str = 'success') -> bool:
        """Add audit log entry"""
        try:
            session = self.get_session()
            
            log_entry = AuditLog(
                application_id=application_id,
                action=action,
                action_details=details,
                performed_by=performed_by,
                result=result
            )
            
            session.add(log_entry)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding audit log: {str(e)}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get trade finance statistics"""
        try:
            session = self.get_session()
            
            # Basic counts
            total_applications = session.query(TradeFinanceApplication).count()
            
            # Status distribution
            status_counts = session.query(
                TradeFinanceApplication.status,
                func.count(TradeFinanceApplication.id)
            ).group_by(TradeFinanceApplication.status).all()
            
            status_distribution = {status: count for status, count in status_counts}
            
            # Trade type distribution
            trade_type_counts = session.query(
                TradeFinanceApplication.trade_type,
                func.count(TradeFinanceApplication.id)
            ).group_by(TradeFinanceApplication.trade_type).all()
            
            trade_type_distribution = {trade_type: count for trade_type, count in trade_type_counts}
            
            # Risk level distribution
            risk_level_counts = session.query(
                TradeFinanceApplication.risk_level,
                func.count(TradeFinanceApplication.id)
            ).group_by(TradeFinanceApplication.risk_level).all()
            
            risk_level_distribution = {risk_level or 'Unknown': count for risk_level, count in risk_level_counts}
            
            # Amount statistics
            amount_stats = session.query(
                func.sum(TradeFinanceApplication.finance_amount),
                func.avg(TradeFinanceApplication.finance_amount),
                func.min(TradeFinanceApplication.finance_amount),
                func.max(TradeFinanceApplication.finance_amount)
            ).first()
            
            total_amount, avg_amount, min_amount, max_amount = amount_stats
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_applications = session.query(TradeFinanceApplication).filter(
                TradeFinanceApplication.created_at >= thirty_days_ago
            ).count()
            
            # Processing time statistics
            completed_apps = session.query(TradeFinanceApplication).filter(
                TradeFinanceApplication.status.in_(['approved', 'rejected']),
                TradeFinanceApplication.processed_at.isnot(None)
            ).all()
            
            processing_times = []
            for app in completed_apps:
                if app.processed_at and app.created_at:
                    processing_time = (app.processed_at - app.created_at).total_seconds() / 3600  # hours
                    processing_times.append(processing_time)
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            session.close()
            
            return {
                'total_applications': total_applications,
                'status_distribution': status_distribution,
                'trade_type_distribution': trade_type_distribution,
                'risk_level_distribution': risk_level_distribution,
                'amount_statistics': {
                    'total_amount': total_amount or 0,
                    'average_amount': avg_amount or 0,
                    'minimum_amount': min_amount or 0,
                    'maximum_amount': max_amount or 0
                },
                'recent_activity': {
                    'applications_last_30_days': recent_applications
                },
                'processing_statistics': {
                    'average_processing_time_hours': round(avg_processing_time, 2),
                    'completed_applications': len(completed_apps)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            if 'session' in locals():
                session.close()
            return {
                'total_applications': 0,
                'status_distribution': {},
                'trade_type_distribution': {},
                'risk_level_distribution': {},
                'amount_statistics': {
                    'total_amount': 0,
                    'average_amount': 0,
                    'minimum_amount': 0,
                    'maximum_amount': 0
                },
                'recent_activity': {
                    'applications_last_30_days': 0
                },
                'processing_statistics': {
                    'average_processing_time_hours': 0,
                    'completed_applications': 0
                }
            }
    
    def get_processing_steps(self, application_id: str) -> List[Dict[str, Any]]:
        """Get processing steps for an application"""
        try:
            session = self.get_session()
            
            steps = session.query(ProcessingStep).filter(
                ProcessingStep.application_id == application_id
            ).order_by(ProcessingStep.created_at.asc()).all()
            
            results = []
            for step in steps:
                results.append({
                    'step_name': step.step_name,
                    'step_status': step.step_status,
                    'step_result': self._parse_json_field(step.step_result),
                    'step_score': step.step_score,
                    'processing_time': step.processing_time,
                    'processor': step.processor,
                    'started_at': step.started_at,
                    'completed_at': step.completed_at,
                    'notes': step.notes
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting processing steps: {str(e)}")
            if 'session' in locals():
                session.close()
            return []
    
    def get_risk_assessments(self, application_id: str) -> List[Dict[str, Any]]:
        """Get risk assessments for an application"""
        try:
            session = self.get_session()
            
            assessments = session.query(RiskAssessment).filter(
                RiskAssessment.application_id == application_id
            ).order_by(RiskAssessment.assessed_at.desc()).all()
            
            results = []
            for assessment in assessments:
                results.append({
                    'assessment_type': assessment.assessment_type,
                    'risk_level': assessment.risk_level,
                    'risk_score': assessment.risk_score,
                    'risk_factors': self._parse_json_field(assessment.risk_factors),
                    'mitigation_measures': self._parse_json_field(assessment.mitigation_measures),
                    'assessment_method': assessment.assessment_method,
                    'assessed_by': assessment.assessed_by,
                    'assessed_at': assessment.assessed_at,
                    'valid_until': assessment.valid_until,
                    'notes': assessment.notes
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting risk assessments: {str(e)}")
            if 'session' in locals():
                session.close()
            return []
    
    def get_audit_logs(self, application_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit logs for an application"""
        try:
            session = self.get_session()
            
            logs = session.query(AuditLog).filter(
                AuditLog.application_id == application_id
            ).order_by(AuditLog.performed_at.desc()).limit(limit).all()
            
            results = []
            for log in logs:
                results.append({
                    'action': log.action,
                    'action_details': log.action_details,
                    'performed_by': log.performed_by,
                    'performed_at': log.performed_at,
                    'result': log.result,
                    'error_message': log.error_message
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            if 'session' in locals():
                session.close()
            return []
    
    def cleanup_old_data(self, days_old: int = 365) -> bool:
        """Clean up old data (older than specified days)"""
        try:
            session = self.get_session()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Delete old audit logs
            old_logs = session.query(AuditLog).filter(
                AuditLog.performed_at < cutoff_date
            ).delete()
            
            # Delete old processing steps for completed applications
            old_steps = session.query(ProcessingStep).filter(
                ProcessingStep.created_at < cutoff_date,
                ProcessingStep.step_status == 'completed'
            ).delete()
            
            session.commit()
            session.close()
            
            logger.info(f"Cleaned up {old_logs} audit logs and {old_steps} processing steps")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def _parse_json_field(self, json_str: str) -> Any:
        """Parse JSON field safely"""
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return json_str
    
    def close(self):
        """Close database connection"""
        try:
            self.engine.dispose()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Test the database
    db = Database("test_trade_finance.db")
    
    try:
        # Test application data
        test_application = {
            'application_id': 'TF20240101001',
            'company_name': 'Global Trade Corp',
            'company_address': '123 Business St, Trade City, TC 12345',
            'company_registration': 'REG123456789',
            'contact_person': 'John Smith',
            'contact_email': 'john.smith@globaltrade.com',
            'contact_phone': '+1-555-0123',
            'trade_type': 'Letter of Credit',
            'finance_amount': 500000.0,
            'currency': 'USD',
            'payment_terms': '90 days',
            'trade_description': 'Import of electronic components',
            'counterparty_name': 'International Electronics Ltd',
            'counterparty_country': 'Germany',
            'counterparty_address': '456 Export Ave, Hamburg, Germany',
            'counterparty_bank': 'Deutsche Bank AG',
            'priority': 'high',
            'notes': 'Established customer with good payment history'
        }
        
        # Test adding application
        print("Testing application creation...")
        success = db.add_application(test_application)
        print(f"Application created: {success}")
        
        # Test getting application
        print("\nTesting application retrieval...")
        retrieved_app = db.get_application('TF20240101001')
        print(f"Application retrieved: {retrieved_app is not None}")
        
        # Test updating application
        print("\nTesting application update...")
        update_success = db.update_application('TF20240101001', {
            'status': 'under_review',
            'assigned_officer': 'Jane Doe'
        })
        print(f"Application updated: {update_success}")
        
        # Test statistics
        print("\nTesting statistics...")
        stats = db.get_statistics()
        print(f"Total applications: {stats.get('total_applications', 0)}")
        
        # Test processing step
        print("\nTesting processing step...")
        step_data = {
            'application_id': 'TF20240101001',
            'step_name': 'document_verification',
            'step_status': 'completed',
            'step_result': {'score': 85, 'issues': []},
            'step_score': 85.0,
            'processing_time': 120.5,
            'processor': 'ai_powered',
            'started_at': datetime.now(),
            'completed_at': datetime.now(),
            'notes': 'All documents verified successfully'
        }
        step_success = db.add_processing_step(step_data)
        print(f"Processing step added: {step_success}")
        
        print("\nDatabase test completed successfully")
        
    except Exception as e:
        print(f"Database test error: {e}")
    
    finally:
        db.close()