# trade_finance.py

import sys
import json
import uuid
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox, QFormLayout,
    QProgressBar, QMessageBox, QHeaderView, QSplitter, QFrame,
    QScrollArea, QGridLayout, QDoubleSpinBox, QDateEdit, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QDate
from PyQt6.QtGui import QFont, QPalette, QColor
from database import Database
from document_processor import DocumentProcessor
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradeFinanceProcessingThread(QThread):
    """Thread for processing trade finance applications"""
    
    progress_updated = pyqtSignal(str, str, int)  # application_id, status, progress
    processing_completed = pyqtSignal(str, dict)  # application_id, results
    
    def __init__(self, application_data: Dict[str, Any], db: Database, doc_processor: DocumentProcessor):
        super().__init__()
        self.application_data = application_data
        self.db = db
        self.doc_processor = doc_processor
        self.application_id = application_data.get('application_id')
    
    def run(self):
        """Process trade finance application"""
        try:
            logger.info(f"Starting processing for application {self.application_id}")
            
            # Step 1: Document Verification (20%)
            self.progress_updated.emit(self.application_id, "Document Verification", 20)
            time.sleep(2)
            doc_results = self.verify_documents()
            
            # Step 2: Credit Assessment (40%)
            self.progress_updated.emit(self.application_id, "Credit Assessment", 40)
            time.sleep(2)
            credit_results = self.assess_credit()
            
            # Step 3: Compliance Check (60%)
            self.progress_updated.emit(self.application_id, "Compliance Check", 60)
            time.sleep(2)
            compliance_results = self.check_compliance()
            
            # Step 4: Risk Analysis (80%)
            self.progress_updated.emit(self.application_id, "Risk Analysis", 80)
            time.sleep(2)
            risk_results = self.analyze_risk()
            
            # Step 5: Final Decision (100%)
            self.progress_updated.emit(self.application_id, "Final Decision", 100)
            time.sleep(1)
            final_decision = self.make_final_decision(doc_results, credit_results, compliance_results, risk_results)
            
            # Combine all results
            complete_results = {
                'document_verification': doc_results,
                'credit_assessment': credit_results,
                'compliance_check': compliance_results,
                'risk_analysis': risk_results,
                'final_decision': final_decision,
                'processing_completed_at': datetime.now().isoformat()
            }
            
            # Update database
            new_status = final_decision.get('decision', 'pending')
            self.db.update_application_status(self.application_id, new_status)
            self.db.update_application_results(
                self.application_id,
                processing_results=json.dumps(complete_results),
                risk_level=risk_results.get('risk_level', 'medium')
            )
            
            self.processing_completed.emit(self.application_id, complete_results)
            logger.info(f"Processing completed for application {self.application_id}")
            
        except Exception as e:
            logger.error(f"Error processing application {self.application_id}: {str(e)}")
            error_results = {
                'error': str(e),
                'status': 'processing_error',
                'timestamp': datetime.now().isoformat()
            }
            self.processing_completed.emit(self.application_id, error_results)
    
    def verify_documents(self) -> Dict[str, Any]:
        """Verify trade finance documents"""
        try:
            # Use AI-powered document verification if available
            ai_results = self.doc_processor.verify_documents_ai(self.application_data)
            
            if ai_results.get('success'):
                return ai_results
            else:
                # Fallback to rule-based verification
                return self.doc_processor.verify_documents_rules(self.application_data)
                
        except Exception as e:
            logger.error(f"Document verification error: {str(e)}")
            return {
                'success': False,
                'score': 0.0,
                'issues': [f"Verification error: {str(e)}"],
                'method': 'error_fallback'
            }
    
    def assess_credit(self) -> Dict[str, Any]:
        """Assess creditworthiness"""
        try:
            # Try AI-powered credit assessment
            ai_assessment = self.get_ai_credit_assessment()
            
            if ai_assessment.get('success'):
                # Combine AI assessment with rule-based metrics
                rule_assessment = self.get_rule_based_credit_assessment()
                
                # Weighted combination (70% AI, 30% rules)
                combined_score = (ai_assessment.get('credit_score', 0) * 0.7 + 
                                rule_assessment.get('credit_score', 0) * 0.3)
                
                return {
                    'success': True,
                    'credit_score': round(combined_score, 2),
                    'rating': self.get_credit_rating(combined_score),
                    'ai_assessment': ai_assessment,
                    'rule_assessment': rule_assessment,
                    'method': 'hybrid'
                }
            else:
                # Fallback to rule-based assessment
                return self.get_rule_based_credit_assessment()
                
        except Exception as e:
            logger.error(f"Credit assessment error: {str(e)}")
            return {
                'success': False,
                'credit_score': 0.0,
                'rating': 'Unknown',
                'error': str(e),
                'method': 'error_fallback'
            }
    
    def get_ai_credit_assessment(self) -> Dict[str, Any]:
        """Get AI-powered credit assessment"""
        try:
            # Prepare prompt for AI assessment
            prompt = f"""
Analyze this trade finance application for creditworthiness:

Company: {self.application_data.get('company_name', 'N/A')}
Industry: {self.application_data.get('industry', 'N/A')}
Annual Revenue: ${self.application_data.get('annual_revenue', 0):,.2f}
Years in Business: {self.application_data.get('years_in_business', 0)}
Credit History: {self.application_data.get('credit_history', 'N/A')}
Trade Finance Amount: ${self.application_data.get('finance_amount', 0):,.2f}
Trade Type: {self.application_data.get('trade_type', 'N/A')}
Counterparty Country: {self.application_data.get('counterparty_country', 'N/A')}
Payment Terms: {self.application_data.get('payment_terms', 'N/A')}

Provide a credit assessment with:
1. Credit score (0-100)
2. Credit rating (AAA, AA, A, BBB, BB, B, CCC, CC, C, D)
3. Key strengths
4. Key risks
5. Recommendations

Respond in JSON format:
{{
    "credit_score": <score>,
    "credit_rating": "<rating>",
    "strengths": ["<strength1>", "<strength2>"],
    "risks": ["<risk1>", "<risk2>"],
    "recommendations": ["<rec1>", "<rec2>"],
    "confidence": <confidence_score>
}}
"""
            
            # Call Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json().get('response', '')
                
                # Parse JSON response
                try:
                    # Extract JSON from response
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_str = ai_response[json_start:json_end]
                        ai_result = json.loads(json_str)
                        
                        return {
                            'success': True,
                            'credit_score': float(ai_result.get('credit_score', 0)),
                            'credit_rating': ai_result.get('credit_rating', 'Unknown'),
                            'strengths': ai_result.get('strengths', []),
                            'risks': ai_result.get('risks', []),
                            'recommendations': ai_result.get('recommendations', []),
                            'confidence': float(ai_result.get('confidence', 0)),
                            'method': 'ai_powered',
                            'raw_response': ai_response
                        }
                    else:
                        raise ValueError("No valid JSON found in AI response")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse AI credit assessment: {str(e)}")
                    return {'success': False, 'error': f"JSON parsing error: {str(e)}"}
            else:
                logger.warning(f"AI credit assessment failed: HTTP {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"AI credit assessment request failed: {str(e)}")
            return {'success': False, 'error': f"Request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"AI credit assessment error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_rule_based_credit_assessment(self) -> Dict[str, Any]:
        """Get rule-based credit assessment"""
        try:
            score = 0
            factors = []
            
            # Annual revenue factor (0-25 points)
            revenue = float(self.application_data.get('annual_revenue', 0))
            if revenue >= 10000000:  # $10M+
                score += 25
                factors.append("Strong revenue base ($10M+)")
            elif revenue >= 5000000:  # $5M+
                score += 20
                factors.append("Good revenue base ($5M+)")
            elif revenue >= 1000000:  # $1M+
                score += 15
                factors.append("Moderate revenue base ($1M+)")
            elif revenue >= 500000:  # $500K+
                score += 10
                factors.append("Limited revenue base ($500K+)")
            else:
                score += 5
                factors.append("Low revenue base (<$500K)")
            
            # Years in business factor (0-20 points)
            years = int(self.application_data.get('years_in_business', 0))
            if years >= 10:
                score += 20
                factors.append("Established business (10+ years)")
            elif years >= 5:
                score += 15
                factors.append("Mature business (5+ years)")
            elif years >= 2:
                score += 10
                factors.append("Growing business (2+ years)")
            else:
                score += 5
                factors.append("New business (<2 years)")
            
            # Credit history factor (0-20 points)
            credit_history = self.application_data.get('credit_history', '').lower()
            if 'excellent' in credit_history:
                score += 20
                factors.append("Excellent credit history")
            elif 'good' in credit_history:
                score += 15
                factors.append("Good credit history")
            elif 'fair' in credit_history:
                score += 10
                factors.append("Fair credit history")
            elif 'poor' in credit_history:
                score += 5
                factors.append("Poor credit history")
            else:
                score += 10
                factors.append("Unknown credit history")
            
            # Finance amount vs revenue ratio (0-15 points)
            finance_amount = float(self.application_data.get('finance_amount', 0))
            if revenue > 0:
                ratio = finance_amount / revenue
                if ratio <= 0.1:  # 10% or less
                    score += 15
                    factors.append("Conservative financing ratio (≤10%)")
                elif ratio <= 0.25:  # 25% or less
                    score += 12
                    factors.append("Moderate financing ratio (≤25%)")
                elif ratio <= 0.5:  # 50% or less
                    score += 8
                    factors.append("High financing ratio (≤50%)")
                else:
                    score += 3
                    factors.append("Very high financing ratio (>50%)")
            else:
                score += 5
                factors.append("Unable to assess financing ratio")
            
            # Industry risk factor (0-10 points)
            industry = self.application_data.get('industry', '').lower()
            low_risk_industries = ['technology', 'healthcare', 'education', 'utilities']
            medium_risk_industries = ['manufacturing', 'retail', 'services', 'agriculture']
            high_risk_industries = ['oil', 'mining', 'construction', 'entertainment']
            
            if any(ind in industry for ind in low_risk_industries):
                score += 10
                factors.append("Low-risk industry")
            elif any(ind in industry for ind in medium_risk_industries):
                score += 7
                factors.append("Medium-risk industry")
            elif any(ind in industry for ind in high_risk_industries):
                score += 4
                factors.append("High-risk industry")
            else:
                score += 6
                factors.append("Unknown industry risk")
            
            # Country risk factor (0-10 points)
            country = self.application_data.get('counterparty_country', '').lower()
            low_risk_countries = ['united states', 'canada', 'germany', 'japan', 'australia', 'uk', 'france']
            medium_risk_countries = ['china', 'india', 'brazil', 'mexico', 'south korea', 'italy', 'spain']
            
            if any(c in country for c in low_risk_countries):
                score += 10
                factors.append("Low country risk")
            elif any(c in country for c in medium_risk_countries):
                score += 7
                factors.append("Medium country risk")
            else:
                score += 4
                factors.append("High country risk")
            
            # Determine credit rating
            credit_rating = self.get_credit_rating(score)
            
            return {
                'success': True,
                'credit_score': score,
                'credit_rating': credit_rating,
                'factors': factors,
                'method': 'rule_based'
            }
            
        except Exception as e:
            logger.error(f"Rule-based credit assessment error: {str(e)}")
            return {
                'success': False,
                'credit_score': 0,
                'credit_rating': 'Unknown',
                'error': str(e),
                'method': 'error_fallback'
            }
    
    def get_credit_rating(self, score: float) -> str:
        """Convert credit score to rating"""
        if score >= 90:
            return 'AAA'
        elif score >= 85:
            return 'AA'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'BBB'
        elif score >= 60:
            return 'BB'
        elif score >= 50:
            return 'B'
        elif score >= 40:
            return 'CCC'
        elif score >= 30:
            return 'CC'
        elif score >= 20:
            return 'C'
        else:
            return 'D'
    
    def check_compliance(self) -> Dict[str, Any]:
        """Check regulatory compliance"""
        try:
            compliance_score = 0
            checks = []
            issues = []
            
            # KYC/AML checks
            kyc_score = random.uniform(0.7, 1.0)  # Simulate KYC check
            compliance_score += kyc_score * 30
            checks.append(f"KYC/AML: {kyc_score:.2f}")
            
            if kyc_score < 0.8:
                issues.append("KYC documentation incomplete")
            
            # Sanctions screening
            sanctions_clear = random.choice([True, True, True, False])  # 75% pass rate
            if sanctions_clear:
                compliance_score += 25
                checks.append("Sanctions screening: CLEAR")
            else:
                checks.append("Sanctions screening: FLAGGED")
                issues.append("Potential sanctions match found")
            
            # Export/Import regulations
            trade_compliance = random.uniform(0.8, 1.0)
            compliance_score += trade_compliance * 25
            checks.append(f"Trade compliance: {trade_compliance:.2f}")
            
            # Documentation completeness
            doc_completeness = random.uniform(0.7, 1.0)
            compliance_score += doc_completeness * 20
            checks.append(f"Documentation: {doc_completeness:.2f}")
            
            if doc_completeness < 0.9:
                issues.append("Some documentation missing or incomplete")
            
            # Determine compliance status
            if compliance_score >= 85 and not issues:
                status = 'compliant'
            elif compliance_score >= 70:
                status = 'conditional'
            else:
                status = 'non_compliant'
            
            return {
                'success': True,
                'compliance_score': round(compliance_score, 2),
                'status': status,
                'checks': checks,
                'issues': issues,
                'method': 'automated'
            }
            
        except Exception as e:
            logger.error(f"Compliance check error: {str(e)}")
            return {
                'success': False,
                'compliance_score': 0,
                'status': 'error',
                'error': str(e),
                'method': 'error_fallback'
            }
    
    def analyze_risk(self) -> Dict[str, Any]:
        """Analyze overall risk"""
        try:
            risk_factors = []
            risk_score = 0
            
            # Market risk
            market_risk = random.uniform(0.1, 0.8)
            risk_score += market_risk * 25
            risk_factors.append(f"Market risk: {market_risk:.2f}")
            
            # Credit risk
            credit_risk = random.uniform(0.1, 0.7)
            risk_score += credit_risk * 30
            risk_factors.append(f"Credit risk: {credit_risk:.2f}")
            
            # Operational risk
            operational_risk = random.uniform(0.1, 0.6)
            risk_score += operational_risk * 20
            risk_factors.append(f"Operational risk: {operational_risk:.2f}")
            
            # Country risk
            country_risk = random.uniform(0.1, 0.9)
            risk_score += country_risk * 15
            risk_factors.append(f"Country risk: {country_risk:.2f}")
            
            # Currency risk
            currency_risk = random.uniform(0.1, 0.5)
            risk_score += currency_risk * 10
            risk_factors.append(f"Currency risk: {currency_risk:.2f}")
            
            # Determine risk level
            if risk_score <= 25:
                risk_level = 'very_low'
            elif risk_score <= 40:
                risk_level = 'low'
            elif risk_score <= 60:
                risk_level = 'medium'
            elif risk_score <= 80:
                risk_level = 'high'
            else:
                risk_level = 'very_high'
            
            return {
                'success': True,
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'method': 'comprehensive'
            }
            
        except Exception as e:
            logger.error(f"Risk analysis error: {str(e)}")
            return {
                'success': False,
                'risk_score': 100,
                'risk_level': 'very_high',
                'error': str(e),
                'method': 'error_fallback'
            }
    
    def make_final_decision(self, doc_results: Dict, credit_results: Dict, 
                          compliance_results: Dict, risk_results: Dict) -> Dict[str, Any]:
        """Make final approval decision"""
        try:
            # Calculate weighted score
            doc_score = doc_results.get('score', 0) if doc_results.get('success') else 0
            credit_score = credit_results.get('credit_score', 0) if credit_results.get('success') else 0
            compliance_score = compliance_results.get('compliance_score', 0) if compliance_results.get('success') else 0
            risk_score = 100 - risk_results.get('risk_score', 100) if risk_results.get('success') else 0
            
            # Weighted average (documents: 20%, credit: 40%, compliance: 25%, risk: 15%)
            final_score = (doc_score * 0.2 + credit_score * 0.4 + 
                          compliance_score * 0.25 + risk_score * 0.15)
            
            # Decision logic
            if final_score >= 80 and compliance_results.get('status') == 'compliant':
                decision = 'approved'
                conditions = []
            elif final_score >= 65 and compliance_results.get('status') in ['compliant', 'conditional']:
                decision = 'conditional_approval'
                conditions = [
                    "Enhanced monitoring required",
                    "Additional documentation may be requested",
                    "Periodic review of credit status"
                ]
            elif final_score >= 50:
                decision = 'manual_review'
                conditions = [
                    "Requires senior management approval",
                    "Additional due diligence required",
                    "Enhanced terms and conditions"
                ]
            else:
                decision = 'rejected'
                conditions = [
                    "Insufficient credit quality",
                    "High risk profile",
                    "Compliance concerns"
                ]
            
            return {
                'decision': decision,
                'final_score': round(final_score, 2),
                'conditions': conditions,
                'decision_date': datetime.now().isoformat(),
                'valid_until': (datetime.now() + timedelta(days=30)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Final decision error: {str(e)}")
            return {
                'decision': 'manual_review',
                'final_score': 0,
                'conditions': [f"Processing error: {str(e)}"],
                'decision_date': datetime.now().isoformat(),
                'error': str(e)
            }

class TradeFinanceApplicationWindow(QWidget):
    """Window for submitting trade finance applications"""
    
    application_submitted = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Trade Finance Application")
        self.setGeometry(100, 100, 800, 700)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Trade Finance Application")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Company Information
        company_group = QGroupBox("Company Information")
        company_layout = QFormLayout()
        
        self.company_name = QLineEdit()
        self.industry = QComboBox()
        self.industry.addItems([
            "Manufacturing", "Technology", "Healthcare", "Retail", "Agriculture",
            "Oil & Gas", "Mining", "Construction", "Services", "Other"
        ])
        self.annual_revenue = QDoubleSpinBox()
        self.annual_revenue.setRange(0, 999999999)
        self.annual_revenue.setSuffix(" USD")
        self.years_in_business = QSpinBox()
        self.years_in_business.setRange(0, 100)
        
        company_layout.addRow("Company Name:", self.company_name)
        company_layout.addRow("Industry:", self.industry)
        company_layout.addRow("Annual Revenue:", self.annual_revenue)
        company_layout.addRow("Years in Business:", self.years_in_business)
        
        company_group.setLayout(company_layout)
        scroll_layout.addWidget(company_group)
        
        # Trade Information
        trade_group = QGroupBox("Trade Information")
        trade_layout = QFormLayout()
        
        self.trade_type = QComboBox()
        self.trade_type.addItems([
            "Letter of Credit", "Documentary Collection", "Trade Loan", 
            "Export Financing", "Import Financing", "Supply Chain Finance"
        ])
        self.finance_amount = QDoubleSpinBox()
        self.finance_amount.setRange(0, 999999999)
        self.finance_amount.setSuffix(" USD")
        self.counterparty_name = QLineEdit()
        self.counterparty_country = QComboBox()
        self.counterparty_country.addItems([
            "United States", "Canada", "United Kingdom", "Germany", "France",
            "China", "Japan", "India", "Brazil", "Mexico", "Australia", "Other"
        ])
        self.payment_terms = QComboBox()
        self.payment_terms.addItems([
            "30 days", "60 days", "90 days", "120 days", "180 days", "Other"
        ])
        
        trade_layout.addRow("Trade Type:", self.trade_type)
        trade_layout.addRow("Finance Amount:", self.finance_amount)
        trade_layout.addRow("Counterparty Name:", self.counterparty_name)
        trade_layout.addRow("Counterparty Country:", self.counterparty_country)
        trade_layout.addRow("Payment Terms:", self.payment_terms)
        
        trade_group.setLayout(trade_layout)
        scroll_layout.addWidget(trade_group)
        
        # Financial Information
        financial_group = QGroupBox("Financial Information")
        financial_layout = QFormLayout()
        
        self.credit_history = QComboBox()
        self.credit_history.addItems(["Excellent", "Good", "Fair", "Poor", "Unknown"])
        self.existing_facilities = QDoubleSpinBox()
        self.existing_facilities.setRange(0, 999999999)
        self.existing_facilities.setSuffix(" USD")
        self.collateral_offered = QLineEdit()
        
        financial_layout.addRow("Credit History:", self.credit_history)
        financial_layout.addRow("Existing Credit Facilities:", self.existing_facilities)
        financial_layout.addRow("Collateral Offered:", self.collateral_offered)
        
        financial_group.setLayout(financial_layout)
        scroll_layout.addWidget(financial_group)
        
        # Additional Information
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout()
        
        self.purpose = QTextEdit()
        self.purpose.setMaximumHeight(100)
        self.special_requirements = QTextEdit()
        self.special_requirements.setMaximumHeight(100)
        
        additional_layout.addRow("Purpose of Trade Finance:", self.purpose)
        additional_layout.addRow("Special Requirements:", self.special_requirements)
        
        additional_group.setLayout(additional_layout)
        scroll_layout.addWidget(additional_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("Submit Application")
        self.submit_btn.clicked.connect(self.submit_application)
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.submit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def submit_application(self):
        """Submit the trade finance application"""
        try:
            # Validate required fields
            if not self.company_name.text().strip():
                QMessageBox.warning(self, "Validation Error", "Company name is required.")
                return
            
            if not self.counterparty_name.text().strip():
                QMessageBox.warning(self, "Validation Error", "Counterparty name is required.")
                return
            
            if self.finance_amount.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Finance amount must be greater than 0.")
                return
            
            # Create application data
            application_data = {
                'application_id': f"TF{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                'company_name': self.company_name.text().strip(),
                'industry': self.industry.currentText(),
                'annual_revenue': self.annual_revenue.value(),
                'years_in_business': self.years_in_business.value(),
                'trade_type': self.trade_type.currentText(),
                'finance_amount': self.finance_amount.value(),
                'counterparty_name': self.counterparty_name.text().strip(),
                'counterparty_country': self.counterparty_country.currentText(),
                'payment_terms': self.payment_terms.currentText(),
                'credit_history': self.credit_history.currentText(),
                'existing_facilities': self.existing_facilities.value(),
                'collateral_offered': self.collateral_offered.text().strip(),
                'purpose': self.purpose.toPlainText().strip(),
                'special_requirements': self.special_requirements.toPlainText().strip(),
                'submission_timestamp': datetime.now().isoformat(),
                'status': 'submitted'
            }
            
            # Emit signal
            self.application_submitted.emit(application_data)
            
            # Show confirmation
            QMessageBox.information(
                self, 
                "Application Submitted", 
                f"Your trade finance application {application_data['application_id']} has been submitted successfully."
            )
            
            # Clear form
            self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(self, "Submission Error", f"Error submitting application: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.company_name.clear()
        self.industry.setCurrentIndex(0)
        self.annual_revenue.setValue(0)
        self.years_in_business.setValue(0)
        self.trade_type.setCurrentIndex(0)
        self.finance_amount.setValue(0)
        self.counterparty_name.clear()
        self.counterparty_country.setCurrentIndex(0)
        self.payment_terms.setCurrentIndex(0)
        self.credit_history.setCurrentIndex(0)
        self.existing_facilities.setValue(0)
        self.collateral_offered.clear()
        self.purpose.clear()
        self.special_requirements.clear()

class TradeFinanceOfficerWindow(QWidget):
    """Window for trade finance officers to review applications"""
    
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_applications()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_applications)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Trade Finance Officer Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Trade Finance Officer Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status Filter:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "submitted", "processing", "approved", "rejected", "manual_review"])
        self.status_filter.currentTextChanged.connect(self.refresh_applications)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_applications)
        filter_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Applications table
        self.applications_table = QTableWidget()
        self.applications_table.setColumnCount(8)
        self.applications_table.setHorizontalHeaderLabels([
            "Application ID", "Company", "Trade Type", "Amount", "Status", "Risk Level", "Submitted", "Actions"
        ])
        
        # Set column widths
        header = self.applications_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.applications_table)
        
        # Details panel
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(200)
        self.details_text.setReadOnly(True)
        layout.addWidget(QLabel("Application Details:"))
        layout.addWidget(self.details_text)
        
        self.setLayout(layout)
    
    def refresh_applications(self):
        """Refresh the applications table"""
        try:
            # Get filter
            status_filter = self.status_filter.currentText()
            if status_filter == "All":
                status_filter = None
            
            # Get applications
            applications = self.db.get_applications(limit=100, status=status_filter)
            
            # Update table
            self.applications_table.setRowCount(len(applications))
            
            for row, app in enumerate(applications):
                # Application ID
                self.applications_table.setItem(row, 0, QTableWidgetItem(app.application_id or ""))
                
                # Company
                self.applications_table.setItem(row, 1, QTableWidgetItem(app.company_name or ""))
                
                # Trade Type
                self.applications_table.setItem(row, 2, QTableWidgetItem(app.trade_type or ""))
                
                # Amount
                amount_str = f"${app.finance_amount:,.2f}" if app.finance_amount else "$0.00"
                self.applications_table.setItem(row, 3, QTableWidgetItem(amount_str))
                
                # Status
                status_item = QTableWidgetItem(app.status or "")
                if app.status == 'approved':
                    status_item.setBackground(QColor(200, 255, 200))
                elif app.status == 'rejected':
                    status_item.setBackground(QColor(255, 200, 200))
                elif app.status == 'processing':
                    status_item.setBackground(QColor(255, 255, 200))
                self.applications_table.setItem(row, 4, status_item)
                
                # Risk Level
                risk_item = QTableWidgetItem(app.risk_level or "")
                if app.risk_level == 'low':
                    risk_item.setBackground(QColor(200, 255, 200))
                elif app.risk_level == 'high':
                    risk_item.setBackground(QColor(255, 200, 200))
                elif app.risk_level == 'very_high':
                    risk_item.setBackground(QColor(255, 150, 150))
                self.applications_table.setItem(row, 5, risk_item)
                
                # Submitted
                submitted_str = app.submitted_at.strftime('%Y-%m-%d %H:%M') if app.submitted_at else ""
                self.applications_table.setItem(row, 6, QTableWidgetItem(submitted_str))
                
                # Actions
                actions_btn = QPushButton("View Details")
                actions_btn.clicked.connect(lambda checked, a=app: self.show_application_details(a))
                self.applications_table.setCellWidget(row, 7, actions_btn)
            
            logger.info(f"Refreshed {len(applications)} applications")
            
        except Exception as e:
            logger.error(f"Error refreshing applications: {str(e)}")
    
    def show_application_details(self, application):
        """Show detailed information about an application"""
        try:
            details = f"""
Application ID: {application.application_id}
Company: {application.company_name}
Industry: {application.industry}
Annual Revenue: ${application.annual_revenue:,.2f}
Years in Business: {application.years_in_business}

Trade Information:
Type: {application.trade_type}
Amount: ${application.finance_amount:,.2f}
Counterparty: {application.counterparty_name}
Country: {application.counterparty_country}
Payment Terms: {application.payment_terms}

Status: {application.status}
Risk Level: {application.risk_level}
Submitted: {application.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if application.submitted_at else 'N/A'}
Processed: {application.processed_at.strftime('%Y-%m-%d %H:%M:%S') if application.processed_at else 'N/A'}

Purpose: {application.purpose}
Special Requirements: {application.special_requirements}
"""
            
            # Add processing results if available
            if application.processing_results:
                try:
                    results = json.loads(application.processing_results)
                    details += "\n\nProcessing Results:\n"
                    
                    if 'final_decision' in results:
                        decision = results['final_decision']
                        details += f"Decision: {decision.get('decision', 'N/A')}\n"
                        details += f"Final Score: {decision.get('final_score', 'N/A')}\n"
                        
                        if 'conditions' in decision:
                            details += "Conditions:\n"
                            for condition in decision['conditions']:
                                details += f"  - {condition}\n"
                    
                    if 'credit_assessment' in results:
                        credit = results['credit_assessment']
                        details += f"\nCredit Score: {credit.get('credit_score', 'N/A')}\n"
                        details += f"Credit Rating: {credit.get('credit_rating', 'N/A')}\n"
                    
                except json.JSONDecodeError:
                    details += "\nProcessing results available but could not be parsed."
            
            self.details_text.setPlainText(details)
            
        except Exception as e:
            logger.error(f"Error showing application details: {str(e)}")
            self.details_text.setPlainText(f"Error loading details: {str(e)}")

class TradeFinanceSystem(QMainWindow):
    """Main trade finance system application"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database and document processor
        self.db = Database()
        self.doc_processor = DocumentProcessor()
        
        # Processing threads
        self.processing_threads = {}
        
        self.init_ui()
        self.load_statistics()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(15000)  # Refresh every 15 seconds
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Trade Finance Management System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Trade Finance Management System")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Statistics panel
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stats_labels = {}
        stats_items = [
            ("Total Applications", "total_applications"),
            ("Pending", "submitted_applications"),
            ("Processing", "processing_applications"),
            ("Approved", "approved_applications"),
            ("Rejected", "rejected_applications"),
            ("Approval Rate", "approval_rate")
        ]
        
        for label_text, key in stats_items:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            
            value_label = QLabel("0")
            value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            desc_label = QLabel(label_text)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(desc_label)
            
            self.stats_labels[key] = value_label
            stats_layout.addWidget(stat_widget)
        
        layout.addWidget(stats_frame)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Application tab
        self.application_window = TradeFinanceApplicationWindow()
        self.application_window.application_submitted.connect(self.handle_new_application)
        self.tab_widget.addTab(self.application_window, "New Application")
        
        # Officer dashboard tab
        self.officer_window = TradeFinanceOfficerWindow(self.db)
        self.tab_widget.addTab(self.officer_window, "Officer Dashboard")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Trade Finance System Ready")
        
        # Last update label
        self.last_update_label = QLabel("Last updated: Never")
        layout.addWidget(self.last_update_label)
    
    def handle_new_application(self, application_data: Dict[str, Any]):
        """Handle new application submission"""
        try:
            # Add to database
            success = self.db.add_application(application_data)
            
            if success:
                # Start processing thread
                application_id = application_data['application_id']
                
                processing_thread = TradeFinanceProcessingThread(
                    application_data, self.db, self.doc_processor
                )
                processing_thread.progress_updated.connect(self.update_processing_progress)
                processing_thread.processing_completed.connect(self.handle_processing_completed)
                
                self.processing_threads[application_id] = processing_thread
                processing_thread.start()
                
                self.statusBar().showMessage(f"Processing application {application_id}...")
                logger.info(f"Started processing application {application_id}")
                
                # Refresh data
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to save application to database.")
                
        except Exception as e:
            logger.error(f"Error handling new application: {str(e)}")
            QMessageBox.critical(self, "Application Error", f"Error processing application: {str(e)}")
    
    def update_processing_progress(self, application_id: str, status: str, progress: int):
        """Update processing progress"""
        self.statusBar().showMessage(f"Application {application_id}: {status} ({progress}%)")
    
    def handle_processing_completed(self, application_id: str, results: Dict[str, Any]):
        """Handle completed processing"""
        try:
            if 'error' in results:
                self.statusBar().showMessage(f"Application {application_id}: Processing failed")
                logger.error(f"Processing failed for {application_id}: {results.get('error')}")
            else:
                decision = results.get('final_decision', {}).get('decision', 'unknown')
                self.statusBar().showMessage(f"Application {application_id}: {decision.title()}")
                logger.info(f"Processing completed for {application_id}: {decision}")
            
            # Clean up thread
            if application_id in self.processing_threads:
                del self.processing_threads[application_id]
            
            # Refresh data
            self.refresh_data()
            
        except Exception as e:
            logger.error(f"Error handling processing completion: {str(e)}")
    
    def load_statistics(self):
        """Load and display statistics"""
        try:
            stats = self.db.get_trade_finance_statistics()
            
            for key, label in self.stats_labels.items():
                value = stats.get(key, 0)
                if key == 'approval_rate':
                    label.setText(f"{value}%")
                else:
                    label.setText(str(value))
            
            logger.info("Statistics loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading statistics: {str(e)}")
            for label in self.stats_labels.values():
                label.setText("Error")
    
    def refresh_data(self):
        """Refresh all data"""
        try:
            self.load_statistics()
            self.officer_window.refresh_applications()
            self.last_update_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error refreshing data: {str(e)}")

def main():
    """Main function to run the application"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = TradeFinanceSystem()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()