# onboarding.py

import sys
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QGroupBox, QFormLayout, QCheckBox, QDateEdit,
    QMessageBox, QSplitter, QFrame, QScrollArea
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QDate, Qt
from PyQt6.QtGui import QFont, QColor, QPalette
import requests
from database import Database, CustomerApplication

class KYCAMLProcessor(QThread):
    """Thread for processing KYC and AML checks"""
    
    progress_updated = pyqtSignal(str, int)  # stage, progress
    check_completed = pyqtSignal(str, dict)  # check_type, result
    processing_finished = pyqtSignal(str, dict)  # application_id, final_result
    
    def __init__(self, application_data: Dict[str, Any]):
        super().__init__()
        self.application_data = application_data
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.2"
        
    def run(self):
        """Run KYC and AML processing"""
        try:
            application_id = self.application_data.get('application_id')
            
            # Stage 1: Document Verification
            self.progress_updated.emit("Document Verification", 10)
            doc_result = self.verify_documents()
            self.check_completed.emit("document_verification", doc_result)
            time.sleep(1)
            
            # Stage 2: Identity Verification
            self.progress_updated.emit("Identity Verification", 30)
            identity_result = self.verify_identity()
            self.check_completed.emit("identity_verification", identity_result)
            time.sleep(1)
            
            # Stage 3: Address Verification
            self.progress_updated.emit("Address Verification", 50)
            address_result = self.verify_address()
            self.check_completed.emit("address_verification", address_result)
            time.sleep(1)
            
            # Stage 4: AML Screening
            self.progress_updated.emit("AML Screening", 70)
            aml_result = self.perform_aml_screening()
            self.check_completed.emit("aml_screening", aml_result)
            time.sleep(1)
            
            # Stage 5: Risk Assessment
            self.progress_updated.emit("Risk Assessment", 90)
            risk_result = self.assess_risk()
            self.check_completed.emit("risk_assessment", risk_result)
            time.sleep(1)
            
            # Final Decision
            self.progress_updated.emit("Final Decision", 100)
            final_result = self.make_final_decision(doc_result, identity_result, address_result, aml_result, risk_result)
            
            self.processing_finished.emit(application_id, final_result)
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'message': f'Processing error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            self.processing_finished.emit(application_id, error_result)
    
    def verify_documents(self) -> Dict[str, Any]:
        """Simulate document verification"""
        # Simulate document analysis
        documents = self.application_data.get('documents', {})
        
        # Rule-based checks
        issues = []
        score = 100
        
        # Check document completeness
        required_docs = ['passport', 'proof_of_address', 'income_proof']
        for doc in required_docs:
            if not documents.get(doc):
                issues.append(f"Missing {doc.replace('_', ' ')}")
                score -= 20
        
        # Simulate document quality checks
        if random.random() < 0.1:  # 10% chance of document quality issues
            issues.append("Document quality concerns detected")
            score -= 15
        
        # AI-powered document analysis (if available)
        ai_analysis = self.get_ai_document_analysis(documents)
        if ai_analysis.get('confidence', 0) < 0.7:
            score -= 10
            issues.append("AI analysis shows low confidence")
        
        status = 'passed' if score >= 70 else 'failed' if score < 50 else 'review_required'
        
        return {
            'status': status,
            'score': score,
            'issues': issues,
            'ai_analysis': ai_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_identity(self) -> Dict[str, Any]:
        """Simulate identity verification"""
        customer_data = self.application_data
        
        issues = []
        score = 100
        
        # Basic validation
        if not customer_data.get('date_of_birth'):
            issues.append("Date of birth missing")
            score -= 20
        
        if not customer_data.get('national_id'):
            issues.append("National ID missing")
            score -= 20
        
        # Simulate identity database checks
        if random.random() < 0.05:  # 5% chance of identity mismatch
            issues.append("Identity verification mismatch detected")
            score -= 30
        
        # Age verification
        try:
            dob = datetime.strptime(customer_data.get('date_of_birth', ''), '%Y-%m-%d')
            age = (datetime.now() - dob).days // 365
            if age < 18:
                issues.append("Customer is under 18 years old")
                score -= 50
            elif age > 100:
                issues.append("Suspicious age detected")
                score -= 20
        except:
            issues.append("Invalid date of birth format")
            score -= 15
        
        # AI-powered identity verification
        ai_verification = self.get_ai_identity_verification(customer_data)
        if ai_verification.get('confidence', 0) < 0.8:
            score -= 10
            issues.append("AI identity verification shows concerns")
        
        status = 'passed' if score >= 80 else 'failed' if score < 60 else 'review_required'
        
        return {
            'status': status,
            'score': score,
            'issues': issues,
            'ai_verification': ai_verification,
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_address(self) -> Dict[str, Any]:
        """Simulate address verification"""
        address = self.application_data.get('address', '')
        country = self.application_data.get('country', '')
        
        issues = []
        score = 100
        
        # Basic validation
        if len(address) < 10:
            issues.append("Address too short or incomplete")
            score -= 20
        
        # Simulate address database verification
        if random.random() < 0.1:  # 10% chance of address verification failure
            issues.append("Address not found in postal database")
            score -= 25
        
        # High-risk country check
        high_risk_countries = ['Country A', 'Country B', 'Country C']
        if country in high_risk_countries:
            issues.append(f"High-risk jurisdiction: {country}")
            score -= 15
        
        # Simulate utility bill verification
        if random.random() < 0.05:  # 5% chance of utility bill issues
            issues.append("Utility bill verification failed")
            score -= 20
        
        status = 'passed' if score >= 75 else 'failed' if score < 50 else 'review_required'
        
        return {
            'status': status,
            'score': score,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def perform_aml_screening(self) -> Dict[str, Any]:
        """Perform Anti-Money Laundering screening"""
        customer_data = self.application_data
        
        issues = []
        score = 100
        risk_factors = []
        
        # PEP (Politically Exposed Person) check
        if random.random() < 0.02:  # 2% chance of PEP match
            issues.append("Potential PEP (Politically Exposed Person) match")
            risk_factors.append("PEP")
            score -= 40
        
        # Sanctions list check
        if random.random() < 0.01:  # 1% chance of sanctions match
            issues.append("Potential sanctions list match")
            risk_factors.append("Sanctions")
            score -= 50
        
        # Adverse media check
        if random.random() < 0.05:  # 5% chance of adverse media
            issues.append("Adverse media mentions found")
            risk_factors.append("Adverse Media")
            score -= 20
        
        # High-risk occupation check
        occupation = customer_data.get('occupation', '').lower()
        high_risk_occupations = ['politician', 'arms dealer', 'casino owner']
        if any(risk_occ in occupation for risk_occ in high_risk_occupations):
            issues.append(f"High-risk occupation: {occupation}")
            risk_factors.append("High-risk Occupation")
            score -= 25
        
        # Income vs. expected wealth check
        try:
            annual_income = float(customer_data.get('annual_income', 0))
            if annual_income > 1000000:  # High income threshold
                issues.append("High income requires enhanced due diligence")
                risk_factors.append("High Income")
                score -= 10
        except:
            pass
        
        # AI-powered AML screening
        ai_screening = self.get_ai_aml_screening(customer_data)
        if ai_screening.get('risk_score', 0) > 0.7:
            issues.append("AI AML screening indicates high risk")
            risk_factors.append("AI High Risk")
            score -= 15
        
        status = 'passed' if score >= 80 else 'failed' if score < 60 else 'review_required'
        
        return {
            'status': status,
            'score': score,
            'issues': issues,
            'risk_factors': risk_factors,
            'ai_screening': ai_screening,
            'timestamp': datetime.now().isoformat()
        }
    
    def assess_risk(self) -> Dict[str, Any]:
        """Perform overall risk assessment"""
        customer_data = self.application_data
        
        risk_score = 0
        risk_factors = []
        
        # Age-based risk
        try:
            dob = datetime.strptime(customer_data.get('date_of_birth', ''), '%Y-%m-%d')
            age = (datetime.now() - dob).days // 365
            if age < 25:
                risk_score += 10
                risk_factors.append("Young age")
            elif age > 65:
                risk_score += 5
                risk_factors.append("Senior age")
        except:
            pass
        
        # Income-based risk
        try:
            annual_income = float(customer_data.get('annual_income', 0))
            if annual_income < 20000:
                risk_score += 15
                risk_factors.append("Low income")
            elif annual_income > 500000:
                risk_score += 10
                risk_factors.append("Very high income")
        except:
            pass
        
        # Employment status risk
        employment_status = customer_data.get('employment_status', '').lower()
        if employment_status in ['unemployed', 'self-employed']:
            risk_score += 10
            risk_factors.append(f"Employment status: {employment_status}")
        
        # Country risk
        country = customer_data.get('country', '')
        high_risk_countries = ['Country A', 'Country B']
        if country in high_risk_countries:
            risk_score += 20
            risk_factors.append(f"High-risk country: {country}")
        
        # Account type risk
        account_type = customer_data.get('account_type', '')
        if account_type in ['business', 'corporate']:
            risk_score += 5
            risk_factors.append("Business account")
        
        # AI-powered risk assessment
        ai_risk = self.get_ai_risk_assessment(customer_data)
        ai_risk_score = ai_risk.get('risk_score', 0) * 100
        risk_score += ai_risk_score * 0.3  # Weight AI score
        
        # Determine risk level
        if risk_score < 20:
            risk_level = 'low'
        elif risk_score < 40:
            risk_level = 'medium'
        elif risk_score < 60:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'risk_factors': risk_factors,
            'ai_assessment': ai_risk,
            'timestamp': datetime.now().isoformat()
        }
    
    def make_final_decision(self, doc_result: Dict, identity_result: Dict, 
                          address_result: Dict, aml_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Make final onboarding decision"""
        
        # Check if any critical checks failed
        critical_failures = []
        if doc_result['status'] == 'failed':
            critical_failures.append('Document verification failed')
        if identity_result['status'] == 'failed':
            critical_failures.append('Identity verification failed')
        if aml_result['status'] == 'failed':
            critical_failures.append('AML screening failed')
        
        # Calculate overall score
        total_score = (
            doc_result['score'] * 0.25 +
            identity_result['score'] * 0.25 +
            address_result['score'] * 0.2 +
            aml_result['score'] * 0.2 +
            (100 - risk_result['risk_score']) * 0.1
        )
        
        # Determine final decision
        if critical_failures:
            decision = 'rejected'
            reason = f"Critical failures: {', '.join(critical_failures)}"
        elif total_score >= 80 and risk_result['risk_level'] in ['low', 'medium']:
            decision = 'approved'
            reason = "All checks passed successfully"
        elif total_score >= 60:
            decision = 'manual_review'
            reason = "Requires manual review due to moderate risk factors"
        else:
            decision = 'rejected'
            reason = "Overall score too low for approval"
        
        # Determine account restrictions if approved
        restrictions = []
        if risk_result['risk_level'] == 'high':
            restrictions.extend(['Enhanced monitoring', 'Transaction limits'])
        if aml_result['status'] == 'review_required':
            restrictions.append('Periodic AML reviews')
        
        return {
            'decision': decision,
            'reason': reason,
            'overall_score': round(total_score, 2),
            'risk_level': risk_result['risk_level'],
            'restrictions': restrictions,
            'checks_summary': {
                'document_verification': doc_result['status'],
                'identity_verification': identity_result['status'],
                'address_verification': address_result['status'],
                'aml_screening': aml_result['status'],
                'risk_assessment': risk_result['risk_level']
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_ai_document_analysis(self, documents: Dict) -> Dict[str, Any]:
        """Get AI analysis of documents"""
        try:
            prompt = f"""
Analyze the following customer documents for onboarding:

Documents provided: {', '.join(documents.keys())}
Document details: {json.dumps(documents, indent=2)}

Please analyze and provide:
1. Document authenticity assessment
2. Completeness check
3. Quality assessment
4. Any red flags or concerns
5. Overall confidence score (0-1)

Respond in JSON format:
{{
    "authenticity": "high/medium/low",
    "completeness": "complete/partial/incomplete",
    "quality": "excellent/good/fair/poor",
    "concerns": ["list of concerns"],
    "confidence": 0.85,
    "recommendation": "approve/review/reject"
}}
"""
            
            response = self.call_ollama_api(prompt)
            if response:
                return response
            
        except Exception as e:
            print(f"AI document analysis error: {e}")
        
        # Fallback response
        return {
            "authenticity": "medium",
            "completeness": "complete",
            "quality": "good",
            "concerns": [],
            "confidence": 0.75,
            "recommendation": "approve"
        }
    
    def get_ai_identity_verification(self, customer_data: Dict) -> Dict[str, Any]:
        """Get AI identity verification"""
        try:
            prompt = f"""
Perform identity verification for customer onboarding:

Customer Information:
- Name: {customer_data.get('full_name', 'N/A')}
- Date of Birth: {customer_data.get('date_of_birth', 'N/A')}
- National ID: {customer_data.get('national_id', 'N/A')}
- Address: {customer_data.get('address', 'N/A')}
- Phone: {customer_data.get('phone', 'N/A')}
- Email: {customer_data.get('email', 'N/A')}

Analyze for:
1. Data consistency
2. Potential fraud indicators
3. Identity verification confidence
4. Any red flags

Respond in JSON format:
{{
    "consistency": "high/medium/low",
    "fraud_indicators": ["list of indicators"],
    "confidence": 0.9,
    "red_flags": ["list of red flags"],
    "recommendation": "approve/review/reject"
}}
"""
            
            response = self.call_ollama_api(prompt)
            if response:
                return response
            
        except Exception as e:
            print(f"AI identity verification error: {e}")
        
        # Fallback response
        return {
            "consistency": "high",
            "fraud_indicators": [],
            "confidence": 0.8,
            "red_flags": [],
            "recommendation": "approve"
        }
    
    def get_ai_aml_screening(self, customer_data: Dict) -> Dict[str, Any]:
        """Get AI AML screening"""
        try:
            prompt = f"""
Perform AML (Anti-Money Laundering) screening for customer:

Customer Profile:
- Name: {customer_data.get('full_name', 'N/A')}
- Occupation: {customer_data.get('occupation', 'N/A')}
- Annual Income: {customer_data.get('annual_income', 'N/A')}
- Country: {customer_data.get('country', 'N/A')}
- Account Type: {customer_data.get('account_type', 'N/A')}

Analyze for:
1. PEP (Politically Exposed Person) risk
2. Sanctions list risk
3. High-risk jurisdiction
4. Suspicious activity patterns
5. Overall AML risk

Respond in JSON format:
{{
    "pep_risk": "high/medium/low",
    "sanctions_risk": "high/medium/low",
    "jurisdiction_risk": "high/medium/low",
    "risk_score": 0.3,
    "risk_factors": ["list of risk factors"],
    "recommendation": "approve/review/reject"
}}
"""
            
            response = self.call_ollama_api(prompt)
            if response:
                return response
            
        except Exception as e:
            print(f"AI AML screening error: {e}")
        
        # Fallback response
        return {
            "pep_risk": "low",
            "sanctions_risk": "low",
            "jurisdiction_risk": "low",
            "risk_score": 0.2,
            "risk_factors": [],
            "recommendation": "approve"
        }
    
    def get_ai_risk_assessment(self, customer_data: Dict) -> Dict[str, Any]:
        """Get AI risk assessment"""
        try:
            prompt = f"""
Perform comprehensive risk assessment for customer onboarding:

Customer Profile:
{json.dumps(customer_data, indent=2)}

Analyze overall risk considering:
1. Customer demographics
2. Financial profile
3. Geographic risk
4. Account type and intended use
5. Regulatory compliance requirements

Provide risk assessment in JSON format:
{{
    "risk_score": 0.25,
    "risk_category": "low/medium/high/very_high",
    "key_risk_factors": ["list of main risk factors"],
    "mitigation_measures": ["suggested measures"],
    "monitoring_requirements": ["ongoing monitoring needs"],
    "recommendation": "approve/conditional_approve/review/reject"
}}
"""
            
            response = self.call_ollama_api(prompt)
            if response:
                return response
            
        except Exception as e:
            print(f"AI risk assessment error: {e}")
        
        # Fallback response
        return {
            "risk_score": 0.3,
            "risk_category": "medium",
            "key_risk_factors": [],
            "mitigation_measures": [],
            "monitoring_requirements": [],
            "recommendation": "approve"
        }
    
    def call_ollama_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Ollama API for AI analysis"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '{}')
                
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"Ollama API error: {e}")
        
        return None

class CustomerApplicationWindow(QWidget):
    """Window for customer to submit onboarding application"""
    
    application_submitted = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Customer Onboarding Application")
        self.setGeometry(100, 100, 800, 700)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Bank Account Opening Application")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Personal Information
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout()
        
        self.full_name_edit = QLineEdit()
        self.date_of_birth_edit = QDateEdit()
        self.date_of_birth_edit.setDate(QDate.currentDate().addYears(-25))
        self.national_id_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        
        personal_layout.addRow("Full Name:", self.full_name_edit)
        personal_layout.addRow("Date of Birth:", self.date_of_birth_edit)
        personal_layout.addRow("National ID:", self.national_id_edit)
        personal_layout.addRow("Phone Number:", self.phone_edit)
        personal_layout.addRow("Email Address:", self.email_edit)
        
        personal_group.setLayout(personal_layout)
        scroll_layout.addWidget(personal_group)
        
        # Address Information
        address_group = QGroupBox("Address Information")
        address_layout = QFormLayout()
        
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        self.city_edit = QLineEdit()
        self.country_combo = QComboBox()
        self.country_combo.addItems([
            "United States", "United Kingdom", "Canada", "Australia",
            "Germany", "France", "Japan", "Singapore", "Other"
        ])
        self.postal_code_edit = QLineEdit()
        
        address_layout.addRow("Street Address:", self.address_edit)
        address_layout.addRow("City:", self.city_edit)
        address_layout.addRow("Country:", self.country_combo)
        address_layout.addRow("Postal Code:", self.postal_code_edit)
        
        address_group.setLayout(address_layout)
        scroll_layout.addWidget(address_group)
        
        # Employment Information
        employment_group = QGroupBox("Employment Information")
        employment_layout = QFormLayout()
        
        self.occupation_edit = QLineEdit()
        self.employer_edit = QLineEdit()
        self.employment_status_combo = QComboBox()
        self.employment_status_combo.addItems([
            "Employed", "Self-employed", "Unemployed", "Retired", "Student"
        ])
        self.annual_income_edit = QLineEdit()
        
        employment_layout.addRow("Occupation:", self.occupation_edit)
        employment_layout.addRow("Employer:", self.employer_edit)
        employment_layout.addRow("Employment Status:", self.employment_status_combo)
        employment_layout.addRow("Annual Income ($):", self.annual_income_edit)
        
        employment_group.setLayout(employment_layout)
        scroll_layout.addWidget(employment_group)
        
        # Account Information
        account_group = QGroupBox("Account Information")
        account_layout = QFormLayout()
        
        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems([
            "Personal Checking", "Personal Savings", "Business Checking",
            "Business Savings", "Investment Account"
        ])
        self.initial_deposit_edit = QLineEdit()
        self.purpose_edit = QTextEdit()
        self.purpose_edit.setMaximumHeight(60)
        
        account_layout.addRow("Account Type:", self.account_type_combo)
        account_layout.addRow("Initial Deposit ($):", self.initial_deposit_edit)
        account_layout.addRow("Account Purpose:", self.purpose_edit)
        
        account_group.setLayout(account_layout)
        scroll_layout.addWidget(account_group)
        
        # Documents
        documents_group = QGroupBox("Required Documents")
        documents_layout = QVBoxLayout()
        
        self.passport_check = QCheckBox("Passport/Government ID")
        self.address_proof_check = QCheckBox("Proof of Address (Utility Bill)")
        self.income_proof_check = QCheckBox("Proof of Income")
        self.bank_statement_check = QCheckBox("Bank Statement (if applicable)")
        
        documents_layout.addWidget(self.passport_check)
        documents_layout.addWidget(self.address_proof_check)
        documents_layout.addWidget(self.income_proof_check)
        documents_layout.addWidget(self.bank_statement_check)
        
        documents_group.setLayout(documents_layout)
        scroll_layout.addWidget(documents_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear Form")
        self.submit_button = QPushButton("Submit Application")
        
        self.clear_button.clicked.connect(self.clear_form)
        self.submit_button.clicked.connect(self.submit_application)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.submit_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load sample data
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        samples = [
            {
                "full_name": "John Smith",
                "national_id": "123456789",
                "phone": "+1-555-0123",
                "email": "john.smith@email.com",
                "address": "123 Main Street, Apt 4B",
                "city": "New York",
                "country": "United States",
                "postal_code": "10001",
                "occupation": "Software Engineer",
                "employer": "Tech Corp",
                "employment_status": "Employed",
                "annual_income": "75000",
                "account_type": "Personal Checking",
                "initial_deposit": "1000",
                "purpose": "Personal banking and savings"
            },
            {
                "full_name": "Maria Garcia",
                "national_id": "987654321",
                "phone": "+1-555-0456",
                "email": "maria.garcia@email.com",
                "address": "456 Oak Avenue",
                "city": "Los Angeles",
                "country": "United States",
                "postal_code": "90210",
                "occupation": "Business Owner",
                "employer": "Self-employed",
                "employment_status": "Self-employed",
                "annual_income": "120000",
                "account_type": "Business Checking",
                "initial_deposit": "5000",
                "purpose": "Business operations and payroll"
            }
        ]
        
        # Randomly select a sample
        sample = random.choice(samples)
        
        self.full_name_edit.setText(sample["full_name"])
        self.national_id_edit.setText(sample["national_id"])
        self.phone_edit.setText(sample["phone"])
        self.email_edit.setText(sample["email"])
        self.address_edit.setPlainText(sample["address"])
        self.city_edit.setText(sample["city"])
        self.country_combo.setCurrentText(sample["country"])
        self.postal_code_edit.setText(sample["postal_code"])
        self.occupation_edit.setText(sample["occupation"])
        self.employer_edit.setText(sample["employer"])
        self.employment_status_combo.setCurrentText(sample["employment_status"])
        self.annual_income_edit.setText(sample["annual_income"])
        self.account_type_combo.setCurrentText(sample["account_type"])
        self.initial_deposit_edit.setText(sample["initial_deposit"])
        self.purpose_edit.setPlainText(sample["purpose"])
        
        # Check some documents
        self.passport_check.setChecked(True)
        self.address_proof_check.setChecked(True)
        self.income_proof_check.setChecked(random.choice([True, False]))
    
    def clear_form(self):
        """Clear all form fields"""
        self.full_name_edit.clear()
        self.date_of_birth_edit.setDate(QDate.currentDate().addYears(-25))
        self.national_id_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.address_edit.clear()
        self.city_edit.clear()
        self.country_combo.setCurrentIndex(0)
        self.postal_code_edit.clear()
        self.occupation_edit.clear()
        self.employer_edit.clear()
        self.employment_status_combo.setCurrentIndex(0)
        self.annual_income_edit.clear()
        self.account_type_combo.setCurrentIndex(0)
        self.initial_deposit_edit.clear()
        self.purpose_edit.clear()
        
        self.passport_check.setChecked(False)
        self.address_proof_check.setChecked(False)
        self.income_proof_check.setChecked(False)
        self.bank_statement_check.setChecked(False)
    
    def submit_application(self):
        """Submit the application"""
        # Validate required fields
        if not self.full_name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return
        
        if not self.national_id_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "National ID is required.")
            return
        
        if not self.email_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Email address is required.")
            return
        
        # Collect application data
        application_data = {
            'application_id': f"APP{random.randint(100000, 999999)}",
            'full_name': self.full_name_edit.text().strip(),
            'date_of_birth': self.date_of_birth_edit.date().toString('yyyy-MM-dd'),
            'national_id': self.national_id_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'address': self.address_edit.toPlainText().strip(),
            'city': self.city_edit.text().strip(),
            'country': self.country_combo.currentText(),
            'postal_code': self.postal_code_edit.text().strip(),
            'occupation': self.occupation_edit.text().strip(),
            'employer': self.employer_edit.text().strip(),
            'employment_status': self.employment_status_combo.currentText(),
            'annual_income': self.annual_income_edit.text().strip(),
            'account_type': self.account_type_combo.currentText(),
            'initial_deposit': self.initial_deposit_edit.text().strip(),
            'purpose': self.purpose_edit.toPlainText().strip(),
            'documents': {
                'passport': self.passport_check.isChecked(),
                'proof_of_address': self.address_proof_check.isChecked(),
                'income_proof': self.income_proof_check.isChecked(),
                'bank_statement': self.bank_statement_check.isChecked()
            },
            'submission_timestamp': datetime.now().isoformat(),
            'status': 'submitted'
        }
        
        self.application_submitted.emit(application_data)
        
        QMessageBox.information(
            self, 
            "Application Submitted", 
            f"Your application {application_data['application_id']} has been submitted successfully!\n\n"
            "You will receive updates on the processing status."
        )
        
        # Clear form after submission
        self.clear_form()
        self.load_sample_data()

class ComplianceOfficerWindow(QWidget):
    """Window for compliance officers to review applications"""
    
    def __init__(self, database: Database):
        super().__init__()
        self.database = database
        self.current_applications = []
        self.init_ui()
        self.load_applications()
    
    def init_ui(self):
        self.setWindowTitle("Compliance Officer Dashboard")
        self.setGeometry(200, 200, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Customer Onboarding - Compliance Review")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Applications list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "submitted", "processing", "approved", "rejected", "manual_review"])
        self.status_filter.currentTextChanged.connect(self.filter_applications)
        filter_layout.addWidget(self.status_filter)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_applications)
        filter_layout.addWidget(self.refresh_button)
        
        left_layout.addLayout(filter_layout)
        
        # Applications table
        self.applications_table = QTableWidget()
        self.applications_table.setColumnCount(6)
        self.applications_table.setHorizontalHeaderLabels([
            "Application ID", "Customer Name", "Account Type", "Status", "Risk Level", "Submitted"
        ])
        self.applications_table.horizontalHeader().setStretchLastSection(True)
        self.applications_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.applications_table.itemSelectionChanged.connect(self.on_application_selected)
        
        left_layout.addWidget(self.applications_table)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Application details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Application details
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Start Processing")
        self.approve_button = QPushButton("Approve")
        self.reject_button = QPushButton("Reject")
        self.review_button = QPushButton("Mark for Review")
        
        self.process_button.clicked.connect(self.start_processing)
        self.approve_button.clicked.connect(self.approve_application)
        self.reject_button.clicked.connect(self.reject_application)
        self.review_button.clicked.connect(self.mark_for_review)
        
        action_layout.addWidget(self.process_button)
        action_layout.addWidget(self.approve_button)
        action_layout.addWidget(self.reject_button)
        action_layout.addWidget(self.review_button)
        
        right_layout.addLayout(action_layout)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
    
    def load_applications(self):
        """Load applications from database"""
        try:
            applications = self.database.get_applications(limit=100)
            self.current_applications = applications
            self.update_applications_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load applications: {str(e)}")
    
    def update_applications_table(self):
        """Update the applications table"""
        filtered_apps = self.get_filtered_applications()
        
        self.applications_table.setRowCount(len(filtered_apps))
        
        for row, app in enumerate(filtered_apps):
            self.applications_table.setItem(row, 0, QTableWidgetItem(app.application_id))
            self.applications_table.setItem(row, 1, QTableWidgetItem(app.customer_name))
            self.applications_table.setItem(row, 2, QTableWidgetItem(app.account_type))
            self.applications_table.setItem(row, 3, QTableWidgetItem(app.status))
            self.applications_table.setItem(row, 4, QTableWidgetItem(app.risk_level or 'N/A'))
            
            submitted_date = app.submitted_at.strftime('%Y-%m-%d %H:%M') if app.submitted_at else 'N/A'
            self.applications_table.setItem(row, 5, QTableWidgetItem(submitted_date))
            
            # Color code by status
            if app.status == 'approved':
                for col in range(6):
                    self.applications_table.item(row, col).setBackground(QColor(200, 255, 200))
            elif app.status == 'rejected':
                for col in range(6):
                    self.applications_table.item(row, col).setBackground(QColor(255, 200, 200))
            elif app.status == 'processing':
                for col in range(6):
                    self.applications_table.item(row, col).setBackground(QColor(255, 255, 200))
    
    def get_filtered_applications(self):
        """Get filtered applications based on current filter"""
        status_filter = self.status_filter.currentText()
        
        if status_filter == "All":
            return self.current_applications
        else:
            return [app for app in self.current_applications if app.status == status_filter]
    
    def filter_applications(self):
        """Filter applications based on selected criteria"""
        self.update_applications_table()
    
    def on_application_selected(self):
        """Handle application selection"""
        current_row = self.applications_table.currentRow()
        if current_row >= 0:
            filtered_apps = self.get_filtered_applications()
            if current_row < len(filtered_apps):
                app = filtered_apps[current_row]
                self.show_application_details(app)
    
    def show_application_details(self, application: CustomerApplication):
        """Show detailed information about the selected application"""
        details = f"""
<h2>Application Details</h2>
<b>Application ID:</b> {application.application_id}<br>
<b>Status:</b> {application.status}<br>
<b>Risk Level:</b> {application.risk_level or 'Not assessed'}<br>
<b>Submitted:</b> {application.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if application.submitted_at else 'N/A'}<br>

<h3>Customer Information</h3>
<b>Name:</b> {application.customer_name}<br>
<b>Date of Birth:</b> {application.date_of_birth}<br>
<b>National ID:</b> {application.national_id}<br>
<b>Phone:</b> {application.phone}<br>
<b>Email:</b> {application.email}<br>

<h3>Address</h3>
<b>Address:</b> {application.address}<br>
<b>City:</b> {application.city}<br>
<b>Country:</b> {application.country}<br>
<b>Postal Code:</b> {application.postal_code}<br>

<h3>Employment</h3>
<b>Occupation:</b> {application.occupation}<br>
<b>Employer:</b> {application.employer}<br>
<b>Employment Status:</b> {application.employment_status}<br>
<b>Annual Income:</b> ${application.annual_income:,.2f}<br>

<h3>Account Information</h3>
<b>Account Type:</b> {application.account_type}<br>
<b>Initial Deposit:</b> ${application.initial_deposit:,.2f}<br>
<b>Purpose:</b> {application.purpose}<br>

<h3>Processing Results</h3>
"""
        
        if application.kyc_results:
            details += f"<b>KYC Results:</b><br><pre>{application.kyc_results}</pre><br>"
        
        if application.aml_results:
            details += f"<b>AML Results:</b><br><pre>{application.aml_results}</pre><br>"
        
        if application.final_decision:
            details += f"<b>Final Decision:</b><br><pre>{application.final_decision}</pre><br>"
        
        if application.notes:
            details += f"<b>Notes:</b><br>{application.notes}<br>"
        
        self.details_text.setHtml(details)
    
    def start_processing(self):
        """Start processing the selected application"""
        current_row = self.applications_table.currentRow()
        if current_row >= 0:
            filtered_apps = self.get_filtered_applications()
            if current_row < len(filtered_apps):
                app = filtered_apps[current_row]
                
                if app.status != 'submitted':
                    QMessageBox.warning(self, "Warning", "Only submitted applications can be processed.")
                    return
                
                # Update status to processing
                self.database.update_application_status(app.application_id, 'processing')
                
                # Start KYC/AML processing
                self.start_kyc_aml_processing(app)
                
                # Refresh the table
                self.load_applications()
    
    def start_kyc_aml_processing(self, application: CustomerApplication):
        """Start KYC/AML processing for an application"""
        try:
            # Convert application to dictionary for processing
            app_data = {
                'application_id': application.application_id,
                'full_name': application.customer_name,
                'date_of_birth': application.date_of_birth,
                'national_id': application.national_id,
                'phone': application.phone,
                'email': application.email,
                'address': application.address,
                'city': application.city,
                'country': application.country,
                'postal_code': application.postal_code,
                'occupation': application.occupation,
                'employer': application.employer,
                'employment_status': application.employment_status,
                'annual_income': str(application.annual_income),
                'account_type': application.account_type,
                'initial_deposit': str(application.initial_deposit),
                'purpose': application.purpose,
                'documents': {
                    'passport': True,  # Assume documents are provided
                    'proof_of_address': True,
                    'income_proof': True
                }
            }
            
            # Create and start processing thread
            self.processing_thread = KYCAMLProcessor(app_data)
            self.processing_thread.processing_finished.connect(
                lambda app_id, result: self.on_processing_finished(app_id, result)
            )
            self.processing_thread.start()
            
            QMessageBox.information(
                self, 
                "Processing Started", 
                f"KYC/AML processing started for application {application.application_id}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start processing: {str(e)}")
    
    def on_processing_finished(self, application_id: str, result: Dict[str, Any]):
        """Handle processing completion"""
        try:
            # Update application with results
            decision = result.get('decision', 'manual_review')
            risk_level = result.get('risk_level', 'medium')
            
            self.database.update_application_status(application_id, decision)
            self.database.update_application_results(
                application_id,
                kyc_results=json.dumps(result.get('checks_summary', {}), indent=2),
                aml_results=json.dumps(result.get('risk_level', 'medium'), indent=2),
                final_decision=json.dumps(result, indent=2),
                risk_level=risk_level
            )
            
            # Refresh the applications
            self.load_applications()
            
            QMessageBox.information(
                self,
                "Processing Complete",
                f"Application {application_id} processing completed.\n"
                f"Decision: {decision.replace('_', ' ').title()}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update application results: {str(e)}")
    
    def approve_application(self):
        """Manually approve the selected application"""
        self.update_application_status('approved')
    
    def reject_application(self):
        """Manually reject the selected application"""
        self.update_application_status('rejected')
    
    def mark_for_review(self):
        """Mark application for manual review"""
        self.update_application_status('manual_review')
    
    def update_application_status(self, new_status: str):
        """Update the status of the selected application"""
        current_row = self.applications_table.currentRow()
        if current_row >= 0:
            filtered_apps = self.get_filtered_applications()
            if current_row < len(filtered_apps):
                app = filtered_apps[current_row]
                
                try:
                    self.database.update_application_status(app.application_id, new_status)
                    self.load_applications()
                    
                    QMessageBox.information(
                        self,
                        "Status Updated",
                        f"Application {app.application_id} status updated to {new_status.replace('_', ' ').title()}"
                    )
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")

class CustomerOnboardingSystem(QMainWindow):
    """Main application window for customer onboarding system"""
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Customer Onboarding System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with tabs
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)
        
        # Customer Application Tab
        self.customer_window = CustomerApplicationWindow()
        self.customer_window.application_submitted.connect(self.on_application_submitted)
        central_widget.addTab(self.customer_window, "Customer Application")
        
        # Compliance Officer Tab
        self.compliance_window = ComplianceOfficerWindow(self.database)
        central_widget.addTab(self.compliance_window, "Compliance Review")
        
        # Statistics Tab
        self.stats_widget = self.create_statistics_widget()
        central_widget.addTab(self.stats_widget, "Statistics")
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def create_statistics_widget(self) -> QWidget:
        """Create statistics widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Onboarding Statistics")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        # Refresh button
        refresh_stats_button = QPushButton("Refresh Statistics")
        refresh_stats_button.clicked.connect(self.update_statistics)
        layout.addWidget(refresh_stats_button)
        
        # Load initial statistics
        self.update_statistics()
        
        return widget
    
    def on_application_submitted(self, application_data: Dict[str, Any]):
        """Handle new application submission"""
        try:
            success = self.database.add_application(application_data)
            if success:
                # Refresh compliance window
                self.compliance_window.load_applications()
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Error", "Failed to save application to database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving application: {str(e)}")
    
    def update_statistics(self):
        """Update statistics display"""
        try:
            stats = self.database.get_onboarding_statistics()
            
            stats_html = f"""
<h2>Customer Onboarding Statistics</h2>

<h3>Application Summary</h3>
<table border="1" cellpadding="5">
<tr><td><b>Total Applications:</b></td><td>{stats.get('total_applications', 0)}</td></tr>
<tr><td><b>Submitted:</b></td><td>{stats.get('submitted_applications', 0)}</td></tr>
<tr><td><b>Processing:</b></td><td>{stats.get('processing_applications', 0)}</td></tr>
<tr><td><b>Approved:</b></td><td>{stats.get('approved_applications', 0)}</td></tr>
<tr><td><b>Rejected:</b></td><td>{stats.get('rejected_applications', 0)}</td></tr>
<tr><td><b>Manual Review:</b></td><td>{stats.get('manual_review_applications', 0)}</td></tr>
</table>

<h3>Approval Metrics</h3>
<table border="1" cellpadding="5">
<tr><td><b>Approval Rate:</b></td><td>{stats.get('approval_rate', 0):.1f}%</td></tr>
<tr><td><b>Rejection Rate:</b></td><td>{stats.get('rejection_rate', 0):.1f}%</td></tr>
<tr><td><b>Manual Review Rate:</b></td><td>{stats.get('manual_review_rate', 0):.1f}%</td></tr>
</table>

<h3>Risk Distribution</h3>
<table border="1" cellpadding="5">
<tr><td><b>Low Risk:</b></td><td>{stats.get('risk_distribution', {}).get('low', 0)}</td></tr>
<tr><td><b>Medium Risk:</b></td><td>{stats.get('risk_distribution', {}).get('medium', 0)}</td></tr>
<tr><td><b>High Risk:</b></td><td>{stats.get('risk_distribution', {}).get('high', 0)}</td></tr>
<tr><td><b>Very High Risk:</b></td><td>{stats.get('risk_distribution', {}).get('very_high', 0)}</td></tr>
</table>

<h3>Recent Activity (Last 24 Hours)</h3>
<table border="1" cellpadding="5">
<tr><td><b>New Applications:</b></td><td>{stats.get('recent_activity', {}).get('applications_24h', 0)}</td></tr>
<tr><td><b>Processed:</b></td><td>{stats.get('recent_activity', {}).get('processed_24h', 0)}</td></tr>
<tr><td><b>Approved:</b></td><td>{stats.get('recent_activity', {}).get('approved_24h', 0)}</td></tr>
</table>

<h3>Account Types</h3>
<table border="1" cellpadding="5">
<tr><td><b>Personal Checking:</b></td><td>{stats.get('account_types', {}).get('Personal Checking', 0)}</td></tr>
<tr><td><b>Personal Savings:</b></td><td>{stats.get('account_types', {}).get('Personal Savings', 0)}</td></tr>
<tr><td><b>Business Checking:</b></td><td>{stats.get('account_types', {}).get('Business Checking', 0)}</td></tr>
<tr><td><b>Business Savings:</b></td><td>{stats.get('account_types', {}).get('Business Savings', 0)}</td></tr>
<tr><td><b>Investment Account:</b></td><td>{stats.get('account_types', {}).get('Investment Account', 0)}</td></tr>
</table>

<p><i>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i></p>
"""
            
            self.stats_text.setHtml(stats_html)
            
        except Exception as e:
            self.stats_text.setPlainText(f"Error loading statistics: {str(e)}")
    
    def refresh_data(self):
        """Refresh all data periodically"""
        try:
            self.compliance_window.load_applications()
            self.update_statistics()
        except Exception as e:
            print(f"Error refreshing data: {e}")

def main():
    """Main function to run the customer onboarding system"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = CustomerOnboardingSystem()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()