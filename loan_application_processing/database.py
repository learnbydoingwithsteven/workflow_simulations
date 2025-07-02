# database.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create base class for declarative models
Base = declarative_base()

class LoanApplication(Base):
    """Database model for loan applications"""
    __tablename__ = 'loan_applications'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Application identification
    reference = Column(String(50), unique=True, nullable=False, index=True)
    
    # Personal information
    applicant_name = Column(String(100), nullable=False)
    ssn = Column(String(11), nullable=False)  # Format: XXX-XX-XXXX
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Employment information
    annual_income = Column(Float, nullable=False)
    employment_status = Column(String(20), nullable=False)  # Full-time, Part-time, Self-employed, etc.
    employer = Column(String(100), nullable=True)
    employment_years = Column(Integer, nullable=False)
    
    # Loan details
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String(100), nullable=False)
    loan_term = Column(Integer, nullable=False)  # in months
    existing_debt = Column(Float, nullable=False, default=0.0)
    credit_score = Column(Integer, nullable=False)
    
    # Processing information
    status = Column(String(20), nullable=False, default='PENDING')  # PENDING, PROCESSING, APPROVED, REJECTED, CONDITIONAL_APPROVAL
    risk_level = Column(String(10), nullable=True)  # low, medium, high
    scoring_result = Column(Text, nullable=True)  # JSON string of detailed scoring results
    interest_rate = Column(Float, nullable=True)  # Approved interest rate
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Additional flags
    is_high_risk = Column(Boolean, default=False)
    requires_manual_review = Column(Boolean, default=False)
    
    def __repr__(self):
        """String representation of the loan application"""
        return f"<LoanApplication(reference='{self.reference}', applicant='{self.applicant_name}', amount={self.loan_amount}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert the loan application to a dictionary"""
        return {
            'id': self.id,
            'reference': self.reference,
            'applicant_name': self.applicant_name,
            'ssn': self.ssn,
            'email': self.email,
            'phone': self.phone,
            'annual_income': self.annual_income,
            'employment_status': self.employment_status,
            'employer': self.employer,
            'employment_years': self.employment_years,
            'loan_amount': self.loan_amount,
            'loan_purpose': self.loan_purpose,
            'loan_term': self.loan_term,
            'existing_debt': self.existing_debt,
            'credit_score': self.credit_score,
            'status': self.status,
            'risk_level': self.risk_level,
            'scoring_result': self.scoring_result,
            'interest_rate': self.interest_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_high_risk': self.is_high_risk,
            'requires_manual_review': self.requires_manual_review
        }

class Database:
    """Database manager for loan application processing system"""
    
    def __init__(self, db_path='loan_applications.db'):
        """Initialize database connection and create tables"""
        try:
            # Create SQLite database engine
            self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            logger.info(f"Database initialized successfully: {db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_application(self, application_data):
        """Add a new loan application to the database"""
        try:
            # Create new loan application instance
            application = LoanApplication(
                reference=application_data['reference'],
                applicant_name=application_data['applicant_name'],
                ssn=application_data['ssn'],
                email=application_data['email'],
                phone=application_data.get('phone', ''),
                annual_income=application_data['annual_income'],
                employment_status=application_data['employment_status'],
                employer=application_data.get('employer', ''),
                employment_years=application_data['employment_years'],
                loan_amount=application_data['loan_amount'],
                loan_purpose=application_data['loan_purpose'],
                loan_term=application_data['loan_term'],
                existing_debt=application_data.get('existing_debt', 0.0),
                credit_score=application_data['credit_score'],
                status=application_data.get('status', 'PENDING'),
                created_at=application_data.get('created_at', datetime.now())
            )
            
            # Add to session and commit
            self.session.add(application)
            self.session.commit()
            
            logger.info(f"Added new loan application: {application.reference}")
            return application
            
        except Exception as e:
            logger.error(f"Error adding loan application: {str(e)}")
            self.session.rollback()
            raise
    
    def update_application_status(self, reference, status, processed_at=None):
        """Update the status of a loan application"""
        try:
            # Find the application by reference
            application = self.session.query(LoanApplication).filter_by(reference=reference).first()
            
            if application:
                # Update status
                application.status = status
                application.updated_at = datetime.now()
                
                # Set processed timestamp if provided
                if processed_at:
                    application.processed_at = processed_at
                
                # Commit changes
                self.session.commit()
                
                logger.info(f"Updated application {reference} status to {status}")
                return True
            else:
                logger.warning(f"Application not found: {reference}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating application status: {str(e)}")
            self.session.rollback()
            return False
    
    def get_application(self, reference):
        """Retrieve a loan application by reference number"""
        try:
            application = self.session.query(LoanApplication).filter_by(reference=reference).first()
            
            if application:
                logger.debug(f"Retrieved application: {reference}")
            else:
                logger.warning(f"Application not found: {reference}")
            
            return application
            
        except Exception as e:
            logger.error(f"Error retrieving application: {str(e)}")
            return None
    
    def get_all_applications(self, status=None, limit=None):
        """Retrieve all loan applications, optionally filtered by status"""
        try:
            query = self.session.query(LoanApplication)
            
            # Filter by status if provided
            if status:
                query = query.filter_by(status=status)
            
            # Order by creation date (newest first)
            query = query.order_by(LoanApplication.created_at.desc())
            
            # Apply limit if provided
            if limit:
                query = query.limit(limit)
            
            applications = query.all()
            
            logger.debug(f"Retrieved {len(applications)} applications")
            return applications
            
        except Exception as e:
            logger.error(f"Error retrieving applications: {str(e)}")
            return []
    
    def get_applications_by_status(self, status):
        """Get all applications with a specific status"""
        return self.get_all_applications(status=status)
    
    def get_pending_applications(self):
        """Get all pending applications"""
        return self.get_applications_by_status('PENDING')
    
    def get_approved_applications(self):
        """Get all approved applications"""
        return self.get_applications_by_status('APPROVED')
    
    def get_rejected_applications(self):
        """Get all rejected applications"""
        return self.get_applications_by_status('REJECTED')
    
    def update_scoring_result(self, reference, scoring_result, risk_level=None, interest_rate=None):
        """Update the scoring result for an application"""
        try:
            application = self.session.query(LoanApplication).filter_by(reference=reference).first()
            
            if application:
                # Update scoring information
                application.scoring_result = str(scoring_result)
                application.updated_at = datetime.now()
                
                if risk_level:
                    application.risk_level = risk_level
                    application.is_high_risk = (risk_level == 'high')
                
                if interest_rate is not None:
                    application.interest_rate = interest_rate
                
                # Commit changes
                self.session.commit()
                
                logger.info(f"Updated scoring result for application {reference}")
                return True
            else:
                logger.warning(f"Application not found: {reference}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating scoring result: {str(e)}")
            self.session.rollback()
            return False
    
    def get_statistics(self):
        """Get application statistics"""
        try:
            stats = {
                'total_applications': self.session.query(LoanApplication).count(),
                'pending_applications': self.session.query(LoanApplication).filter_by(status='PENDING').count(),
                'approved_applications': self.session.query(LoanApplication).filter_by(status='APPROVED').count(),
                'rejected_applications': self.session.query(LoanApplication).filter_by(status='REJECTED').count(),
                'high_risk_applications': self.session.query(LoanApplication).filter_by(is_high_risk=True).count(),
                'total_loan_amount_requested': self.session.query(LoanApplication.loan_amount).filter_by(status='PENDING').scalar() or 0,
                'total_loan_amount_approved': self.session.query(LoanApplication.loan_amount).filter_by(status='APPROVED').scalar() or 0
            }
            
            logger.debug(f"Generated statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating statistics: {str(e)}")
            return {}
    
    def search_applications(self, search_term):
        """Search applications by applicant name, reference, or email"""
        try:
            search_pattern = f"%{search_term}%"
            
            applications = self.session.query(LoanApplication).filter(
                (LoanApplication.applicant_name.like(search_pattern)) |
                (LoanApplication.reference.like(search_pattern)) |
                (LoanApplication.email.like(search_pattern))
            ).order_by(LoanApplication.created_at.desc()).all()
            
            logger.debug(f"Search for '{search_term}' returned {len(applications)} results")
            return applications
            
        except Exception as e:
            logger.error(f"Error searching applications: {str(e)}")
            return []
    
    def delete_application(self, reference):
        """Delete a loan application (use with caution)"""
        try:
            application = self.session.query(LoanApplication).filter_by(reference=reference).first()
            
            if application:
                self.session.delete(application)
                self.session.commit()
                
                logger.info(f"Deleted application: {reference}")
                return True
            else:
                logger.warning(f"Application not found for deletion: {reference}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting application: {str(e)}")
            self.session.rollback()
            return False
    
    def close(self):
        """Close the database session"""
        try:
            self.session.close()
            logger.info("Database session closed")
        except Exception as e:
            logger.error(f"Error closing database session: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Example usage and testing
if __name__ == "__main__":
    # Test the database functionality
    import random
    from datetime import datetime, timedelta
    
    # Initialize database
    db = Database('test_loan_applications.db')
    
    # Test data
    test_application = {
        'reference': f"LOAN-TEST-{random.randint(1000, 9999)}",
        'applicant_name': "Test Applicant",
        'ssn': "123-45-6789",
        'email': "test@example.com",
        'phone': "+1-555-0123",
        'annual_income': 75000.0,
        'employment_status': "Full-time",
        'employer': "Test Company",
        'employment_years': 5,
        'loan_amount': 25000.0,
        'loan_purpose': "Home improvement",
        'loan_term': 60,
        'existing_debt': 15000.0,
        'credit_score': 750
    }
    
    try:
        # Add test application
        app = db.add_application(test_application)
        print(f"Added application: {app.reference}")
        
        # Retrieve application
        retrieved_app = db.get_application(app.reference)
        print(f"Retrieved application: {retrieved_app}")
        
        # Update status
        db.update_application_status(app.reference, "APPROVED", datetime.now())
        
        # Get statistics
        stats = db.get_statistics()
        print(f"Statistics: {stats}")
        
        # Get all applications
        all_apps = db.get_all_applications()
        print(f"Total applications: {len(all_apps)}")
        
    except Exception as e:
        print(f"Test error: {e}")
    
    finally:
        db.close()
        print("Database test completed")