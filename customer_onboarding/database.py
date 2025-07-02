# database.py

import sqlite3
import json
from datetime import datetime, timedelta
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

class CustomerApplication(Base):
    """SQLAlchemy model for customer onboarding applications"""
    __tablename__ = 'customer_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_name = Column(String(200), nullable=False)
    date_of_birth = Column(String(20))
    national_id = Column(String(50))
    phone = Column(String(30))
    email = Column(String(100), index=True)
    
    # Address Information
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Employment Information
    occupation = Column(String(100))
    employer = Column(String(200))
    employment_status = Column(String(50))
    annual_income = Column(Float, default=0.0)
    
    # Account Information
    account_type = Column(String(50))
    initial_deposit = Column(Float, default=0.0)
    purpose = Column(Text)
    
    # Processing Information
    status = Column(String(30), default='submitted', index=True)  # submitted, processing, approved, rejected, manual_review
    risk_level = Column(String(20))  # low, medium, high, very_high
    
    # KYC/AML Results
    kyc_results = Column(Text)  # JSON string of KYC check results
    aml_results = Column(Text)  # JSON string of AML screening results
    final_decision = Column(Text)  # JSON string of final decision details
    
    # Additional Information
    notes = Column(Text)
    assigned_officer = Column(String(100))
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CustomerApplication(id={self.application_id}, name={self.customer_name}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert application to dictionary"""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'customer_name': self.customer_name,
            'date_of_birth': self.date_of_birth,
            'national_id': self.national_id,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'postal_code': self.postal_code,
            'occupation': self.occupation,
            'employer': self.employer,
            'employment_status': self.employment_status,
            'annual_income': self.annual_income,
            'account_type': self.account_type,
            'initial_deposit': self.initial_deposit,
            'purpose': self.purpose,
            'status': self.status,
            'risk_level': self.risk_level,
            'kyc_results': self.kyc_results,
            'aml_results': self.aml_results,
            'final_decision': self.final_decision,
            'notes': self.notes,
            'assigned_officer': self.assigned_officer,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ComplianceCheck(Base):
    """SQLAlchemy model for individual compliance checks"""
    __tablename__ = 'compliance_checks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(String(50), unique=True, nullable=False)
    application_id = Column(String(50), nullable=False, index=True)
    
    # Check Information
    check_type = Column(String(50), nullable=False)  # document_verification, identity_verification, address_verification, aml_screening, risk_assessment
    status = Column(String(20), default='pending')  # pending, passed, failed, review_required
    score = Column(Float, default=0.0)
    
    # Results
    results = Column(Text)  # JSON string of detailed results
    issues = Column(Text)  # JSON string of issues found
    recommendations = Column(Text)  # JSON string of recommendations
    
    # Processing Information
    processed_by = Column(String(20), default='system')  # system, ai, manual
    confidence_score = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ComplianceCheck(id={self.check_id}, type={self.check_type}, status={self.status})>"

class RiskAssessment(Base):
    """SQLAlchemy model for risk assessments"""
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String(50), unique=True, nullable=False)
    application_id = Column(String(50), nullable=False, index=True)
    
    # Risk Information
    overall_risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default='medium')  # very_low, low, medium, high, very_high
    risk_category = Column(String(50))  # customer, geographic, product, regulatory
    
    # Risk Factors
    risk_factors = Column(Text)  # JSON string of identified risk factors
    mitigation_measures = Column(Text)  # JSON string of recommended mitigation measures
    monitoring_requirements = Column(Text)  # JSON string of ongoing monitoring requirements
    
    # Assessment Details
    assessment_method = Column(String(30), default='hybrid')  # rule_based, ai_powered, hybrid, manual
    assessor = Column(String(100))  # Who performed the assessment
    
    # Timestamps
    assessed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<RiskAssessment(id={self.assessment_id}, level={self.risk_level}, score={self.overall_risk_score})>"

class AuditLog(Base):
    """SQLAlchemy model for audit logging"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(String(50), unique=True, nullable=False)
    application_id = Column(String(50), index=True)
    
    # Action Information
    action = Column(String(100), nullable=False)  # status_change, check_completed, manual_review, etc.
    actor = Column(String(100))  # Who performed the action
    actor_type = Column(String(20), default='system')  # system, user, ai
    
    # Details
    description = Column(Text)
    old_value = Column(Text)
    new_value = Column(Text)
    metadata = Column(Text)  # JSON string of additional metadata
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.log_id}, action={self.action}, actor={self.actor})>"

class Database:
    """Database manager for customer onboarding system"""
    
    def __init__(self, db_path: str = "customer_onboarding.db"):
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
    
    def add_application(self, application_data: Dict[str, Any]) -> bool:
        """Add a new customer application to the database"""
        session = self.get_session()
        try:
            # Parse dates
            submitted_at = datetime.now()
            if 'submission_timestamp' in application_data:
                try:
                    submitted_at = datetime.fromisoformat(application_data['submission_timestamp'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Create application object
            application = CustomerApplication(
                application_id=application_data.get('application_id'),
                customer_name=application_data.get('full_name'),
                date_of_birth=application_data.get('date_of_birth'),
                national_id=application_data.get('national_id'),
                phone=application_data.get('phone'),
                email=application_data.get('email'),
                address=application_data.get('address'),
                city=application_data.get('city'),
                country=application_data.get('country'),
                postal_code=application_data.get('postal_code'),
                occupation=application_data.get('occupation'),
                employer=application_data.get('employer'),
                employment_status=application_data.get('employment_status'),
                annual_income=float(application_data.get('annual_income', 0)),
                account_type=application_data.get('account_type'),
                initial_deposit=float(application_data.get('initial_deposit', 0)),
                purpose=application_data.get('purpose'),
                status=application_data.get('status', 'submitted'),
                submitted_at=submitted_at
            )
            
            session.add(application)
            session.commit()
            
            # Log the action
            self.add_audit_log(
                application_id=application_data.get('application_id'),
                action='application_submitted',
                actor='customer',
                actor_type='user',
                description=f"New application submitted by {application_data.get('full_name')}"
            )
            
            logger.info(f"Application {application_data.get('application_id')} added to database")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding application: {str(e)}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding application: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_application_by_id(self, application_id: str) -> Optional[CustomerApplication]:
        """Get an application by its ID"""
        session = self.get_session()
        try:
            application = session.query(CustomerApplication).filter(
                CustomerApplication.application_id == application_id
            ).first()
            return application
        except Exception as e:
            logger.error(f"Error getting application {application_id}: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_applications(self, limit: int = 100, offset: int = 0, status: str = None) -> List[CustomerApplication]:
        """Get applications with optional filtering"""
        session = self.get_session()
        try:
            query = session.query(CustomerApplication)
            
            if status:
                query = query.filter(CustomerApplication.status == status)
            
            applications = query.order_by(
                CustomerApplication.submitted_at.desc()
            ).offset(offset).limit(limit).all()
            
            return applications
        except Exception as e:
            logger.error(f"Error getting applications: {str(e)}")
            return []
        finally:
            session.close()
    
    def update_application_status(self, application_id: str, new_status: str, notes: str = None) -> bool:
        """Update application status"""
        session = self.get_session()
        try:
            application = session.query(CustomerApplication).filter(
                CustomerApplication.application_id == application_id
            ).first()
            
            if application:
                old_status = application.status
                application.status = new_status
                application.updated_at = datetime.utcnow()
                
                if notes:
                    application.notes = notes
                
                # Set processed/approved timestamps
                if new_status in ['approved', 'rejected', 'manual_review'] and not application.processed_at:
                    application.processed_at = datetime.utcnow()
                
                if new_status == 'approved' and not application.approved_at:
                    application.approved_at = datetime.utcnow()
                
                session.commit()
                
                # Log the action
                self.add_audit_log(
                    application_id=application_id,
                    action='status_changed',
                    actor='system',
                    actor_type='system',
                    description=f"Status changed from {old_status} to {new_status}",
                    old_value=old_status,
                    new_value=new_status
                )
                
                logger.info(f"Application {application_id} status updated to {new_status}")
                return True
            else:
                logger.warning(f"Application {application_id} not found for status update")
                return False
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating application status: {str(e)}")
            return False
        finally:
            session.close()
    
    def update_application_results(self, application_id: str, kyc_results: str = None, 
                                 aml_results: str = None, final_decision: str = None, 
                                 risk_level: str = None) -> bool:
        """Update application processing results"""
        session = self.get_session()
        try:
            application = session.query(CustomerApplication).filter(
                CustomerApplication.application_id == application_id
            ).first()
            
            if application:
                if kyc_results:
                    application.kyc_results = kyc_results
                if aml_results:
                    application.aml_results = aml_results
                if final_decision:
                    application.final_decision = final_decision
                if risk_level:
                    application.risk_level = risk_level
                
                application.updated_at = datetime.utcnow()
                session.commit()
                
                # Log the action
                self.add_audit_log(
                    application_id=application_id,
                    action='results_updated',
                    actor='system',
                    actor_type='system',
                    description="Processing results updated"
                )
                
                logger.info(f"Application {application_id} results updated")
                return True
            else:
                logger.warning(f"Application {application_id} not found for results update")
                return False
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating application results: {str(e)}")
            return False
        finally:
            session.close()
    
    def add_compliance_check(self, check_data: Dict[str, Any]) -> bool:
        """Add a compliance check record"""
        session = self.get_session()
        try:
            check = ComplianceCheck(
                check_id=check_data.get('check_id'),
                application_id=check_data.get('application_id'),
                check_type=check_data.get('check_type'),
                status=check_data.get('status', 'pending'),
                score=float(check_data.get('score', 0)),
                results=check_data.get('results'),
                issues=check_data.get('issues'),
                recommendations=check_data.get('recommendations'),
                processed_by=check_data.get('processed_by', 'system'),
                confidence_score=float(check_data.get('confidence_score', 0)),
                completed_at=datetime.utcnow() if check_data.get('status') != 'pending' else None
            )
            
            session.add(check)
            session.commit()
            
            logger.info(f"Compliance check {check_data.get('check_id')} added")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding compliance check: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_compliance_checks(self, application_id: str) -> List[ComplianceCheck]:
        """Get compliance checks for an application"""
        session = self.get_session()
        try:
            checks = session.query(ComplianceCheck).filter(
                ComplianceCheck.application_id == application_id
            ).order_by(ComplianceCheck.started_at.asc()).all()
            return checks
        except Exception as e:
            logger.error(f"Error getting compliance checks: {str(e)}")
            return []
        finally:
            session.close()
    
    def add_risk_assessment(self, assessment_data: Dict[str, Any]) -> bool:
        """Add a risk assessment record"""
        session = self.get_session()
        try:
            assessment = RiskAssessment(
                assessment_id=assessment_data.get('assessment_id'),
                application_id=assessment_data.get('application_id'),
                overall_risk_score=float(assessment_data.get('overall_risk_score', 0)),
                risk_level=assessment_data.get('risk_level', 'medium'),
                risk_category=assessment_data.get('risk_category'),
                risk_factors=assessment_data.get('risk_factors'),
                mitigation_measures=assessment_data.get('mitigation_measures'),
                monitoring_requirements=assessment_data.get('monitoring_requirements'),
                assessment_method=assessment_data.get('assessment_method', 'hybrid'),
                assessor=assessment_data.get('assessor', 'system')
            )
            
            session.add(assessment)
            session.commit()
            
            logger.info(f"Risk assessment {assessment_data.get('assessment_id')} added")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding risk assessment: {str(e)}")
            return False
        finally:
            session.close()
    
    def add_audit_log(self, application_id: str = None, action: str = None, actor: str = None, 
                     actor_type: str = 'system', description: str = None, old_value: str = None, 
                     new_value: str = None, metadata: str = None) -> bool:
        """Add an audit log entry"""
        session = self.get_session()
        try:
            import uuid
            log_entry = AuditLog(
                log_id=str(uuid.uuid4()),
                application_id=application_id,
                action=action,
                actor=actor,
                actor_type=actor_type,
                description=description,
                old_value=old_value,
                new_value=new_value,
                metadata=metadata
            )
            
            session.add(log_entry)
            session.commit()
            
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding audit log: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_audit_logs(self, application_id: str = None, limit: int = 100) -> List[AuditLog]:
        """Get audit logs"""
        session = self.get_session()
        try:
            query = session.query(AuditLog)
            
            if application_id:
                query = query.filter(AuditLog.application_id == application_id)
            
            logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            return logs
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_onboarding_statistics(self) -> Dict[str, Any]:
        """Get comprehensive onboarding statistics"""
        session = self.get_session()
        try:
            # Total applications
            total_applications = session.query(CustomerApplication).count()
            
            # Applications by status
            status_counts = {}
            for status in ['submitted', 'processing', 'approved', 'rejected', 'manual_review']:
                count = session.query(CustomerApplication).filter(
                    CustomerApplication.status == status
                ).count()
                status_counts[f'{status}_applications'] = count
            
            # Calculate rates
            processed_total = status_counts.get('approved_applications', 0) + \
                            status_counts.get('rejected_applications', 0) + \
                            status_counts.get('manual_review_applications', 0)
            
            approval_rate = (status_counts.get('approved_applications', 0) / processed_total * 100) if processed_total > 0 else 0
            rejection_rate = (status_counts.get('rejected_applications', 0) / processed_total * 100) if processed_total > 0 else 0
            manual_review_rate = (status_counts.get('manual_review_applications', 0) / processed_total * 100) if processed_total > 0 else 0
            
            # Risk distribution
            risk_distribution = {}
            for risk_level in ['low', 'medium', 'high', 'very_high']:
                count = session.query(CustomerApplication).filter(
                    CustomerApplication.risk_level == risk_level
                ).count()
                risk_distribution[risk_level] = count
            
            # Account type distribution
            account_types = {}
            account_type_results = session.query(
                CustomerApplication.account_type,
                session.query(CustomerApplication).filter(
                    CustomerApplication.account_type == CustomerApplication.account_type
                ).count().label('count')
            ).group_by(CustomerApplication.account_type).all()
            
            for account_type, count in account_type_results:
                if account_type:
                    account_types[account_type] = count
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            
            recent_applications = session.query(CustomerApplication).filter(
                CustomerApplication.submitted_at >= yesterday
            ).count()
            
            recent_processed = session.query(CustomerApplication).filter(
                CustomerApplication.processed_at >= yesterday
            ).count()
            
            recent_approved = session.query(CustomerApplication).filter(
                CustomerApplication.approved_at >= yesterday
            ).count()
            
            statistics = {
                'total_applications': total_applications,
                **status_counts,
                'approval_rate': round(approval_rate, 1),
                'rejection_rate': round(rejection_rate, 1),
                'manual_review_rate': round(manual_review_rate, 1),
                'risk_distribution': risk_distribution,
                'account_types': account_types,
                'recent_activity': {
                    'applications_24h': recent_applications,
                    'processed_24h': recent_processed,
                    'approved_24h': recent_approved
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting onboarding statistics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def search_applications(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[CustomerApplication]:
        """Search applications based on criteria"""
        session = self.get_session()
        try:
            query = session.query(CustomerApplication)
            
            # Apply search filters
            if 'customer_name' in search_criteria:
                query = query.filter(CustomerApplication.customer_name.ilike(f"%{search_criteria['customer_name']}%"))
            
            if 'email' in search_criteria:
                query = query.filter(CustomerApplication.email.ilike(f"%{search_criteria['email']}%"))
            
            if 'status' in search_criteria:
                query = query.filter(CustomerApplication.status == search_criteria['status'])
            
            if 'risk_level' in search_criteria:
                query = query.filter(CustomerApplication.risk_level == search_criteria['risk_level'])
            
            if 'account_type' in search_criteria:
                query = query.filter(CustomerApplication.account_type == search_criteria['account_type'])
            
            if 'country' in search_criteria:
                query = query.filter(CustomerApplication.country == search_criteria['country'])
            
            if 'date_from' in search_criteria:
                query = query.filter(CustomerApplication.submitted_at >= search_criteria['date_from'])
            
            if 'date_to' in search_criteria:
                query = query.filter(CustomerApplication.submitted_at <= search_criteria['date_to'])
            
            applications = query.order_by(CustomerApplication.submitted_at.desc()).limit(limit).all()
            return applications
            
        except Exception as e:
            logger.error(f"Error searching applications: {str(e)}")
            return []
        finally:
            session.close()
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """Clean up old application data"""
        session = self.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old applications (keep approved and rejected ones for longer)
            deleted_count = session.query(CustomerApplication).filter(
                CustomerApplication.submitted_at < cutoff_date,
                CustomerApplication.status.in_(['submitted', 'processing'])
            ).delete()
            
            # Clean up old audit logs
            audit_cutoff = datetime.now() - timedelta(days=days_to_keep // 2)  # Keep audit logs for half the time
            audit_deleted = session.query(AuditLog).filter(
                AuditLog.timestamp < audit_cutoff
            ).delete()
            
            session.commit()
            logger.info(f"Cleaned up {deleted_count} old applications and {audit_deleted} audit logs")
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
    db = Database("test_customer_onboarding.db")
    
    # Test application data
    test_application = {
        'application_id': 'APP123456',
        'full_name': 'John Doe',
        'date_of_birth': '1990-01-01',
        'national_id': '123456789',
        'phone': '+1-555-0123',
        'email': 'john.doe@email.com',
        'address': '123 Main Street',
        'city': 'New York',
        'country': 'United States',
        'postal_code': '10001',
        'occupation': 'Software Engineer',
        'employer': 'Tech Corp',
        'employment_status': 'Employed',
        'annual_income': '75000',
        'account_type': 'Personal Checking',
        'initial_deposit': '1000',
        'purpose': 'Personal banking',
        'submission_timestamp': datetime.now().isoformat(),
        'status': 'submitted'
    }
    
    try:
        # Add application
        success = db.add_application(test_application)
        print(f"Add application: {'Success' if success else 'Failed'}")
        
        # Get application
        retrieved = db.get_application_by_id('APP123456')
        print(f"Retrieved application: {retrieved.customer_name if retrieved else 'Not found'}")
        
        # Update status
        update_success = db.update_application_status('APP123456', 'approved')
        print(f"Update status: {'Success' if update_success else 'Failed'}")
        
        # Get statistics
        stats = db.get_onboarding_statistics()
        print(f"Statistics: {stats}")
        
        print("Database test completed")
        
    except Exception as e:
        print(f"Database test error: {e}")