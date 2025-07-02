# loan_application.py

import sys
import random
import time
import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QComboBox, QMessageBox, QProgressBar,
                            QTableWidget, QTableWidgetItem, QGroupBox, QCheckBox,
                            QSpinBox, QDoubleSpinBox, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from database import Database
from credit_scoring import CreditScoring

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Predefined loan application templates
LOAN_TEMPLATES = {
    "Personal Loan - Good Credit": {
        "applicant_name": "John Smith",
        "ssn": "123-45-6789",
        "email": "john.smith@email.com",
        "phone": "+1-555-0123",
        "annual_income": 75000.00,
        "employment_status": "Full-time",
        "employer": "Tech Corp Inc",
        "employment_years": 5,
        "loan_amount": 25000.00,
        "loan_purpose": "Home improvement",
        "loan_term": 60,
        "existing_debt": 15000.00,
        "credit_score": 750
    },
    "Business Loan - Startup": {
        "applicant_name": "Sarah Johnson",
        "ssn": "987-65-4321",
        "email": "sarah.johnson@startup.com",
        "phone": "+1-555-0456",
        "annual_income": 45000.00,
        "employment_status": "Self-employed",
        "employer": "Johnson Consulting LLC",
        "employment_years": 2,
        "loan_amount": 100000.00,
        "loan_purpose": "Business expansion",
        "loan_term": 84,
        "existing_debt": 25000.00,
        "credit_score": 680
    },
    "Auto Loan - Fair Credit": {
        "applicant_name": "Michael Brown",
        "ssn": "456-78-9012",
        "email": "m.brown@email.com",
        "phone": "+1-555-0789",
        "annual_income": 55000.00,
        "employment_status": "Full-time",
        "employer": "Manufacturing Co",
        "employment_years": 3,
        "loan_amount": 35000.00,
        "loan_purpose": "Vehicle purchase",
        "loan_term": 72,
        "existing_debt": 20000.00,
        "credit_score": 620
    },
    "Mortgage - High Risk": {
        "applicant_name": "Lisa Davis",
        "ssn": "789-01-2345",
        "email": "lisa.davis@email.com",
        "phone": "+1-555-0321",
        "annual_income": 40000.00,
        "employment_status": "Part-time",
        "employer": "Retail Store",
        "employment_years": 1,
        "loan_amount": 250000.00,
        "loan_purpose": "Home purchase",
        "loan_term": 360,
        "existing_debt": 35000.00,
        "credit_score": 580
    }
}

class LoanProcessingThread(QThread):
    """Thread for processing loan applications with credit scoring"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    
    def __init__(self, loan_data, use_ai=True):
        super().__init__()
        self.loan_data = loan_data
        self.use_ai = use_ai
        self.credit_scoring = CreditScoring()
        logger.info(f"LoanProcessingThread initialized with use_ai={use_ai}")
    
    def run(self):
        """Process the loan application through multiple stages"""
        logger.info(f"Starting loan processing for reference: {self.loan_data.get('reference', 'N/A')}")
        
        # Simulate processing steps with progress updates
        stages = [
            "Validating application data",
            "Checking credit history",
            "Calculating debt-to-income ratio",
            "Running credit scoring model",
            "Performing risk assessment",
            "Generating final decision"
        ]
        
        for i, stage in enumerate(stages):
            logger.info(f"Processing stage: {stage}")
            for j in range(17):  # Each stage takes ~17% of progress
                self.progress.emit(i * 17 + j)
                time.sleep(0.05)
        
        if self.use_ai:
            logger.info("Using AI-powered credit scoring")
            scoring_result = self.credit_scoring.evaluate_application(self.loan_data)
        else:
            logger.info("Using rule-based scoring")
            scoring_result = self._rule_based_scoring()
        
        self.progress.emit(100)
        self.finished.emit(scoring_result)
    
    def _rule_based_scoring(self):
        """Simple rule-based loan approval logic"""
        try:
            # Extract key metrics
            credit_score = int(self.loan_data.get('credit_score', 0))
            annual_income = float(self.loan_data.get('annual_income', 0))
            loan_amount = float(self.loan_data.get('loan_amount', 0))
            existing_debt = float(self.loan_data.get('existing_debt', 0))
            employment_years = int(self.loan_data.get('employment_years', 0))
            
            # Calculate debt-to-income ratio
            monthly_income = annual_income / 12
            monthly_debt = existing_debt / 12
            loan_payment = loan_amount / int(self.loan_data.get('loan_term', 60))
            total_monthly_debt = monthly_debt + loan_payment
            debt_to_income = (total_monthly_debt / monthly_income) * 100 if monthly_income > 0 else 100
            
            # Scoring logic
            score = 0
            risk_factors = []
            
            # Credit score evaluation
            if credit_score >= 750:
                score += 40
            elif credit_score >= 700:
                score += 30
            elif credit_score >= 650:
                score += 20
            elif credit_score >= 600:
                score += 10
            else:
                risk_factors.append(f"Low credit score: {credit_score}")
            
            # Debt-to-income ratio
            if debt_to_income <= 30:
                score += 30
            elif debt_to_income <= 40:
                score += 20
            elif debt_to_income <= 50:
                score += 10
            else:
                risk_factors.append(f"High debt-to-income ratio: {debt_to_income:.1f}%")
            
            # Employment stability
            if employment_years >= 5:
                score += 20
            elif employment_years >= 2:
                score += 15
            elif employment_years >= 1:
                score += 10
            else:
                risk_factors.append(f"Short employment history: {employment_years} years")
            
            # Income adequacy
            if annual_income >= 75000:
                score += 10
            elif annual_income >= 50000:
                score += 5
            elif annual_income < 30000:
                risk_factors.append(f"Low annual income: ${annual_income:,.2f}")
            
            # Determine approval status
            if score >= 80:
                status = "APPROVED"
                risk_level = "low"
                interest_rate = 3.5 + random.uniform(0, 1.5)
            elif score >= 60:
                status = "CONDITIONAL_APPROVAL"
                risk_level = "medium"
                interest_rate = 5.0 + random.uniform(0, 2.0)
            else:
                status = "REJECTED"
                risk_level = "high"
                interest_rate = None
            
            reason = f"Credit score: {score}/100. "
            if risk_factors:
                reason += f"Risk factors: {'; '.join(risk_factors)}"
            else:
                reason += "All criteria met satisfactorily."
            
            result = {
                'approved': status == "APPROVED",
                'status': status,
                'risk_level': risk_level,
                'credit_score_calculated': score,
                'debt_to_income_ratio': debt_to_income,
                'interest_rate': interest_rate,
                'reason': reason,
                'risk_factors': risk_factors
            }
            
            logger.info(f"Rule-based scoring result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in rule-based scoring: {str(e)}")
            return {
                'approved': False,
                'status': "ERROR",
                'risk_level': "high",
                'reason': f"Error in processing: {str(e)}"
            }

class ApplicantWindow(QMainWindow):
    """Window for loan applicants to submit applications"""
    application_submitted = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loan Application - Applicant Portal")
        self.setMinimumSize(900, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface for loan application"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QLabel { font-size: 12px; color: #333; font-weight: bold; }
            QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                font-size: 11px;
            }
            QPushButton {
                padding: 12px 24px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #BDBDBD; }
            QGroupBox { 
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 1em;
                padding-top: 1em;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Header
        header = QLabel("🏦 Loan Application Portal")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E7D32; margin: 20px;")
        layout.addWidget(header)
        
        # Template selection
        template_group = QGroupBox("📋 Application Templates")
        template_layout = QVBoxLayout()
        
        template_label = QLabel("Choose a predefined application template:")
        self.template_combo = QComboBox()
        self.template_combo.addItem("Custom Application")
        self.template_combo.addItems(LOAN_TEMPLATES.keys())
        self.template_combo.currentTextChanged.connect(self.load_template)
        
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Create tabbed interface for better organization
        tab_widget = QTabWidget()
        
        # Personal Information Tab
        personal_tab = QWidget()
        personal_layout = QVBoxLayout(personal_tab)
        
        personal_group = QGroupBox("👤 Personal Information")
        personal_form = QVBoxLayout()
        
        # Create form fields for personal info
        self.applicant_name = QLineEdit()
        self.ssn = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        
        personal_form.addWidget(QLabel("Full Name:"))
        personal_form.addWidget(self.applicant_name)
        personal_form.addWidget(QLabel("Social Security Number:"))
        personal_form.addWidget(self.ssn)
        personal_form.addWidget(QLabel("Email Address:"))
        personal_form.addWidget(self.email)
        personal_form.addWidget(QLabel("Phone Number:"))
        personal_form.addWidget(self.phone)
        
        personal_group.setLayout(personal_form)
        personal_layout.addWidget(personal_group)
        tab_widget.addTab(personal_tab, "Personal Info")
        
        # Employment Information Tab
        employment_tab = QWidget()
        employment_layout = QVBoxLayout(employment_tab)
        
        employment_group = QGroupBox("💼 Employment Information")
        employment_form = QVBoxLayout()
        
        self.annual_income = QDoubleSpinBox()
        self.annual_income.setRange(0, 10000000)
        self.annual_income.setPrefix("$")
        self.annual_income.setSuffix(".00")
        
        self.employment_status = QComboBox()
        self.employment_status.addItems(["Full-time", "Part-time", "Self-employed", "Unemployed", "Retired"])
        
        self.employer = QLineEdit()
        
        self.employment_years = QSpinBox()
        self.employment_years.setRange(0, 50)
        self.employment_years.setSuffix(" years")
        
        employment_form.addWidget(QLabel("Annual Income:"))
        employment_form.addWidget(self.annual_income)
        employment_form.addWidget(QLabel("Employment Status:"))
        employment_form.addWidget(self.employment_status)
        employment_form.addWidget(QLabel("Employer:"))
        employment_form.addWidget(self.employer)
        employment_form.addWidget(QLabel("Years of Employment:"))
        employment_form.addWidget(self.employment_years)
        
        employment_group.setLayout(employment_form)
        employment_layout.addWidget(employment_group)
        tab_widget.addTab(employment_tab, "Employment")
        
        # Loan Details Tab
        loan_tab = QWidget()
        loan_layout = QVBoxLayout(loan_tab)
        
        loan_group = QGroupBox("💰 Loan Details")
        loan_form = QVBoxLayout()
        
        self.loan_amount = QDoubleSpinBox()
        self.loan_amount.setRange(1000, 10000000)
        self.loan_amount.setPrefix("$")
        self.loan_amount.setSuffix(".00")
        
        self.loan_purpose = QComboBox()
        self.loan_purpose.addItems(["Home purchase", "Home improvement", "Vehicle purchase", 
                                   "Business expansion", "Debt consolidation", "Education", "Other"])
        
        self.loan_term = QSpinBox()
        self.loan_term.setRange(12, 480)
        self.loan_term.setSuffix(" months")
        self.loan_term.setValue(60)
        
        self.existing_debt = QDoubleSpinBox()
        self.existing_debt.setRange(0, 1000000)
        self.existing_debt.setPrefix("$")
        self.existing_debt.setSuffix(".00")
        
        self.credit_score = QSpinBox()
        self.credit_score.setRange(300, 850)
        self.credit_score.setValue(650)
        
        loan_form.addWidget(QLabel("Loan Amount Requested:"))
        loan_form.addWidget(self.loan_amount)
        loan_form.addWidget(QLabel("Loan Purpose:"))
        loan_form.addWidget(self.loan_purpose)
        loan_form.addWidget(QLabel("Loan Term:"))
        loan_form.addWidget(self.loan_term)
        loan_form.addWidget(QLabel("Existing Monthly Debt:"))
        loan_form.addWidget(self.existing_debt)
        loan_form.addWidget(QLabel("Estimated Credit Score:"))
        loan_form.addWidget(self.credit_score)
        
        loan_group.setLayout(loan_form)
        loan_layout.addWidget(loan_group)
        tab_widget.addTab(loan_tab, "Loan Details")
        
        layout.addWidget(tab_widget)
        
        # Submit button
        submit_layout = QHBoxLayout()
        submit_layout.addStretch()
        
        self.submit_button = QPushButton("📤 Submit Loan Application")
        self.submit_button.clicked.connect(self.submit_application)
        submit_layout.addWidget(self.submit_button)
        
        submit_layout.addStretch()
        layout.addLayout(submit_layout)
    
    def load_template(self, template_name):
        """Load predefined template data into form fields"""
        if template_name in LOAN_TEMPLATES:
            template = LOAN_TEMPLATES[template_name]
            
            # Load personal information
            self.applicant_name.setText(template['applicant_name'])
            self.ssn.setText(template['ssn'])
            self.email.setText(template['email'])
            self.phone.setText(template['phone'])
            
            # Load employment information
            self.annual_income.setValue(template['annual_income'])
            self.employment_status.setCurrentText(template['employment_status'])
            self.employer.setText(template['employer'])
            self.employment_years.setValue(template['employment_years'])
            
            # Load loan details
            self.loan_amount.setValue(template['loan_amount'])
            self.loan_purpose.setCurrentText(template['loan_purpose'])
            self.loan_term.setValue(template['loan_term'])
            self.existing_debt.setValue(template['existing_debt'])
            self.credit_score.setValue(template['credit_score'])
    
    def submit_application(self):
        """Validate and submit the loan application"""
        # Validate required fields
        if not all([self.applicant_name.text(), self.ssn.text(), self.email.text()]):
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields.")
            return
        
        # Generate unique reference number
        reference = f"LOAN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Collect application data
        application_data = {
            'reference': reference,
            'applicant_name': self.applicant_name.text(),
            'ssn': self.ssn.text(),
            'email': self.email.text(),
            'phone': self.phone.text(),
            'annual_income': self.annual_income.value(),
            'employment_status': self.employment_status.currentText(),
            'employer': self.employer.text(),
            'employment_years': self.employment_years.value(),
            'loan_amount': self.loan_amount.value(),
            'loan_purpose': self.loan_purpose.currentText(),
            'loan_term': self.loan_term.value(),
            'existing_debt': self.existing_debt.value(),
            'credit_score': self.credit_score.value(),
            'status': 'PENDING',
            'created_at': datetime.now()
        }
        
        # Emit signal with application data
        self.application_submitted.emit(application_data)
        
        # Show confirmation
        QMessageBox.information(self, "Application Submitted", 
                               f"Your loan application has been submitted successfully!\n\nReference Number: {reference}\n\nYou will receive an email notification once the application is processed.")
        
        # Clear form
        self.clear_form()
    
    def clear_form(self):
        """Clear all form fields"""
        self.template_combo.setCurrentIndex(0)
        self.applicant_name.clear()
        self.ssn.clear()
        self.email.clear()
        self.phone.clear()
        self.annual_income.setValue(0)
        self.employment_status.setCurrentIndex(0)
        self.employer.clear()
        self.employment_years.setValue(0)
        self.loan_amount.setValue(1000)
        self.loan_purpose.setCurrentIndex(0)
        self.loan_term.setValue(60)
        self.existing_debt.setValue(0)
        self.credit_score.setValue(650)

class LoanOfficerWindow(QMainWindow):
    """Window for loan officers to review and process applications"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loan Processing - Officer Dashboard")
        self.setMinimumSize(1200, 800)
        self.db = Database()
        self.setup_ui()
        self.refresh_applications()
    
    def setup_ui(self):
        """Set up the loan officer dashboard interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Apply styling
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f4f8; }
            QLabel { font-size: 12px; color: #2d3748; }
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                alternate-background-color: #f7fafc;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#approve { background-color: #48bb78; color: white; }
            QPushButton#reject { background-color: #f56565; color: white; }
            QPushButton#refresh { background-color: #4299e1; color: white; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                margin-top: 1em;
                padding-top: 1em;
                background-color: white;
            }
        """)
        
        # Header
        header = QLabel("🏦 Loan Officer Dashboard")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d3748; margin: 20px;")
        layout.addWidget(header)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.use_ai_checkbox = QCheckBox("🤖 Use AI Credit Scoring")
        self.use_ai_checkbox.setChecked(True)
        controls_layout.addWidget(self.use_ai_checkbox)
        
        controls_layout.addStretch()
        
        refresh_button = QPushButton("🔄 Refresh Applications")
        refresh_button.setObjectName("refresh")
        refresh_button.clicked.connect(self.refresh_applications)
        controls_layout.addWidget(refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Applications table
        self.applications_table = QTableWidget()
        self.applications_table.setColumnCount(8)
        self.applications_table.setHorizontalHeaderLabels([
            "Reference", "Applicant", "Amount", "Purpose", "Status", "Risk Level", "Submitted", "Actions"
        ])
        self.applications_table.setAlternatingRowColors(True)
        layout.addWidget(self.applications_table)
        
        # Processing area
        processing_group = QGroupBox("📊 Application Processing")
        processing_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        processing_layout.addWidget(self.progress_bar)
        
        self.processing_status = QLabel("Ready to process applications")
        processing_layout.addWidget(self.processing_status)
        
        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)
    
    def refresh_applications(self):
        """Refresh the applications table with latest data"""
        applications = self.db.get_all_applications()
        self.applications_table.setRowCount(len(applications))
        
        for row, app in enumerate(applications):
            self.applications_table.setItem(row, 0, QTableWidgetItem(app.reference))
            self.applications_table.setItem(row, 1, QTableWidgetItem(app.applicant_name))
            self.applications_table.setItem(row, 2, QTableWidgetItem(f"${app.loan_amount:,.2f}"))
            self.applications_table.setItem(row, 3, QTableWidgetItem(app.loan_purpose))
            self.applications_table.setItem(row, 4, QTableWidgetItem(app.status))
            self.applications_table.setItem(row, 5, QTableWidgetItem(app.risk_level or "N/A"))
            self.applications_table.setItem(row, 6, QTableWidgetItem(app.created_at.strftime("%Y-%m-%d %H:%M")))
            
            # Action buttons
            if app.status == "PENDING":
                process_button = QPushButton("🔍 Process")
                process_button.clicked.connect(lambda checked, ref=app.reference: self.process_application(ref))
                self.applications_table.setCellWidget(row, 7, process_button)
        
        self.applications_table.resizeColumnsToContents()
    
    def process_application(self, reference):
        """Process a specific loan application"""
        application = self.db.get_application(reference)
        if not application:
            QMessageBox.warning(self, "Error", "Application not found")
            return
        
        # Update status to processing
        self.db.update_application_status(reference, "PROCESSING")
        self.refresh_applications()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.processing_status.setText(f"Processing application {reference}...")
        
        # Prepare application data for processing
        app_data = {
            'reference': application.reference,
            'applicant_name': application.applicant_name,
            'annual_income': application.annual_income,
            'employment_status': application.employment_status,
            'employment_years': application.employment_years,
            'loan_amount': application.loan_amount,
            'loan_purpose': application.loan_purpose,
            'loan_term': application.loan_term,
            'existing_debt': application.existing_debt,
            'credit_score': application.credit_score
        }
        
        # Start processing thread
        self.processing_thread = LoanProcessingThread(app_data, self.use_ai_checkbox.isChecked())
        self.processing_thread.progress.connect(self.progress_bar.setValue)
        self.processing_thread.finished.connect(lambda result: self.on_processing_finished(reference, result))
        self.processing_thread.start()
    
    def on_processing_finished(self, reference, result):
        """Handle completion of loan processing"""
        # Update database with results
        status = "APPROVED" if result.get('approved', False) else "REJECTED"
        self.db.update_application_status(reference, status, datetime.now())
        
        # Update additional fields
        application = self.db.get_application(reference)
        if application:
            application.risk_level = result.get('risk_level', 'unknown')
            application.scoring_result = str(result)
            application.interest_rate = result.get('interest_rate')
            self.db.session.commit()
        
        # Hide progress and update status
        self.progress_bar.setVisible(False)
        self.processing_status.setText(f"Application {reference} processed: {status}")
        
        # Show result dialog
        self.show_processing_result(reference, result)
        
        # Refresh table
        self.refresh_applications()
    
    def show_processing_result(self, reference, result):
        """Show detailed processing results"""
        status = "APPROVED" if result.get('approved', False) else "REJECTED"
        
        msg = QMessageBox()
        msg.setWindowTitle("Processing Complete")
        msg.setText(f"Application {reference} has been {status}")
        
        details = f"""Risk Level: {result.get('risk_level', 'Unknown')}
Reason: {result.get('reason', 'No reason provided')}"""
        
        if result.get('interest_rate'):
            details += f"\nInterest Rate: {result['interest_rate']:.2f}%"
        
        if result.get('debt_to_income_ratio'):
            details += f"\nDebt-to-Income Ratio: {result['debt_to_income_ratio']:.1f}%"
        
        msg.setDetailedText(details)
        msg.setIcon(QMessageBox.Icon.Information if result.get('approved') else QMessageBox.Icon.Warning)
        msg.exec()
    
    def add_application(self, application_data):
        """Add new application to database"""
        self.db.add_application(application_data)
        self.refresh_applications()
        self.processing_status.setText(f"New application received: {application_data['reference']}")

class LoanApplicationSystem(QMainWindow):
    """Main application window that manages both applicant and officer interfaces"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏦 Loan Application Processing System")
        self.setMinimumSize(400, 300)
        
        # Initialize database
        self.db = Database()
        
        # Create windows
        self.applicant_window = ApplicantWindow()
        self.officer_window = LoanOfficerWindow()
        
        # Connect signals
        self.applicant_window.application_submitted.connect(self.officer_window.add_application)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main launcher interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow { background-color: #f8fafc; }
            QLabel { font-size: 14px; color: #2d3748; }
            QPushButton {
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                margin: 10px;
            }
            QPushButton#applicant {
                background-color: #4299e1;
                color: white;
            }
            QPushButton#officer {
                background-color: #48bb78;
                color: white;
            }
            QPushButton:hover { opacity: 0.8; }
        """)
        
        # Header
        header = QLabel("🏦 Loan Application Processing System")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3748; margin: 30px;")
        layout.addWidget(header)
        
        # Description
        description = QLabel("Choose your role to access the appropriate interface:")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("font-size: 16px; color: #4a5568; margin-bottom: 30px;")
        layout.addWidget(description)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        applicant_button = QPushButton("👤 Loan Applicant Portal\nSubmit new loan applications")
        applicant_button.setObjectName("applicant")
        applicant_button.clicked.connect(self.show_applicant_window)
        button_layout.addWidget(applicant_button)
        
        officer_button = QPushButton("👨‍💼 Loan Officer Dashboard\nReview and process applications")
        officer_button.setObjectName("officer")
        officer_button.clicked.connect(self.show_officer_window)
        button_layout.addWidget(officer_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def show_applicant_window(self):
        """Show the applicant window"""
        self.applicant_window.show()
        self.applicant_window.raise_()
        self.applicant_window.activateWindow()
    
    def show_officer_window(self):
        """Show the loan officer window"""
        self.officer_window.show()
        self.officer_window.raise_()
        self.officer_window.activateWindow()

def main():
    """Main function to run the loan application system"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Loan Application Processing System")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    main_window = LoanApplicationSystem()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()