# payment.py

import sys
import random
import time
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QComboBox, QMessageBox, QProgressBar,
                            QTableWidget, QTableWidgetItem, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from database import Database
from llm_screening import LLMScreening

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Predefined transaction templates
TRANSACTION_TEMPLATES = {
    "Normal Business Payment": {
        "sender_name": "ABC Corporation",
        "sender_account": "1234567890",
        "receiver_name": "XYZ Supplies Ltd",
        "receiver_account": "0987654321",
        "amount": 5000.00,
        "currency": "USD",
        "purpose": "Office supplies and equipment purchase"
    },
    "High Value Transaction": {
        "sender_name": "Global Investments Inc",
        "sender_account": "9876543210",
        "receiver_name": "Real Estate Holdings LLC",
        "receiver_account": "5432109876",
        "amount": 2500000.00,
        "currency": "USD",
        "purpose": "Property acquisition payment"
    },
    "Suspicious Pattern": {
        "sender_name": "John Smith",
        "sender_account": "1111222233",
        "receiver_name": "Multiple Recipients Corp",
        "receiver_account": "9999888877",
        "amount": 9999.99,
        "currency": "EUR",
        "purpose": "Consulting fees for various services"
    },
    "International Transfer": {
        "sender_name": "European Trading GmbH",
        "sender_account": "DE89370400440532013000",
        "receiver_name": "Asian Exports Ltd",
        "receiver_account": "HK586593825614789",
        "amount": 50000.00,
        "currency": "EUR",
        "purpose": "International trade payment for goods"
    }
}

class PaymentThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    
    def __init__(self, payment_data, use_llm=True):
        super().__init__()
        self.payment_data = payment_data
        self.use_llm = use_llm
        self.llm_screening = LLMScreening()
        logger.info(f"PaymentThread initialized with use_llm={use_llm}")
    
    def run(self):
        logger.info(f"Starting payment processing for reference: {self.payment_data.get('reference', 'N/A')}")
        
        # Simulate processing steps
        for i in range(101):
            self.progress.emit(i)
            time.sleep(0.02)
        
        if self.use_llm:
            logger.info("Using LLM for screening")
            screening_result = self.llm_screening.screen_payment(self.payment_data)
        else:
            logger.info("Using rule-based screening")
            # Simple rule-based screening
            amount = float(self.payment_data['amount'])
            is_international = len(self.payment_data['sender_account']) > 10 or len(self.payment_data['receiver_account']) > 10
            
            if amount > 1000000:
                screening_result = {
                    'allowed': False,
                    'risk_level': 'high',
                    'reason': 'High-value transaction requires additional verification'
                }
            elif is_international:
                screening_result = {
                    'allowed': True,
                    'risk_level': 'medium',
                    'reason': 'International transfer - standard verification required'
                }
            else:
                screening_result = {
                    'allowed': True,
                    'risk_level': 'low',
                    'reason': 'Standard domestic transaction'
                }
            
            logger.info(f"Rule-based screening result: {screening_result}")
        
        self.finished.emit(screening_result)

class ClientWindow(QMainWindow):
    payment_submitted = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Payment Submission - Client")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Style
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QLabel { font-size: 12px; color: #333; }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 10px 20px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:disabled { background-color: #BDBDBD; }
            QGroupBox { 
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 1em;
            }
        """)
        
        # Transaction Templates
        template_group = QGroupBox("Transaction Templates")
        template_layout = QVBoxLayout()
        
        template_label = QLabel("Choose a predefined transaction:")
        self.template_combo = QComboBox()
        self.template_combo.addItem("Custom Transaction")
        self.template_combo.addItems(TRANSACTION_TEMPLATES.keys())
        self.template_combo.currentTextChanged.connect(self.load_template)
        
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Form fields
        form_layout = QVBoxLayout()
        
        # Sender Information
        sender_group = self.create_form_group("Sender Information")
        self.sender_name = QLineEdit()
        self.sender_account = QLineEdit()
        sender_group.addRow("Sender Name:", self.sender_name)
        sender_group.addRow("Sender Account:", self.sender_account)
        form_layout.addLayout(sender_group)
        
        # Receiver Information
        receiver_group = self.create_form_group("Receiver Information")
        self.receiver_name = QLineEdit()
        self.receiver_account = QLineEdit()
        receiver_group.addRow("Receiver Name:", self.receiver_name)
        receiver_group.addRow("Receiver Account:", self.receiver_account)
        form_layout.addLayout(receiver_group)
        
        # Payment Details
        payment_group = self.create_form_group("Payment Details")
        self.amount = QLineEdit()
        self.currency = QComboBox()
        self.currency.addItems(["USD", "EUR", "GBP", "JPY"])
        self.payment_purpose = QTextEdit()
        self.payment_purpose.setMaximumHeight(60)
        payment_group.addRow("Amount:", self.amount)
        payment_group.addRow("Currency:", self.currency)
        payment_group.addRow("Purpose:", self.payment_purpose)
        form_layout.addLayout(payment_group)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)
        self.submit_button = QPushButton("Submit Payment")
        self.submit_button.clicked.connect(self.submit_payment)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(self.submit_button)
        layout.addLayout(button_layout)
    
    def load_template(self, template_name):
        if template_name == "Custom Transaction":
            self.clear_form()
            return
        
        template = TRANSACTION_TEMPLATES[template_name]
        self.sender_name.setText(template["sender_name"])
        self.sender_account.setText(template["sender_account"])
        self.receiver_name.setText(template["receiver_name"])
        self.receiver_account.setText(template["receiver_account"])
        self.amount.setText(str(template["amount"]))
        self.currency.setCurrentText(template["currency"])
        self.payment_purpose.setPlainText(template["purpose"])
    
    def create_form_group(self, title):
        from PyQt6.QtWidgets import QFormLayout
        group_label = QLabel(title)
        group_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QFormLayout()
        layout.addRow(group_label)
        return layout
    
    def submit_payment(self):
        if not self.validate_form():
            return
        
        payment_data = {
            'sender_name': self.sender_name.text(),
            'sender_account': self.sender_account.text(),
            'receiver_name': self.receiver_name.text(),
            'receiver_account': self.receiver_account.text(),
            'amount': float(self.amount.text()),
            'currency': self.currency.currentText(),
            'purpose': self.payment_purpose.toPlainText(),
            'reference': f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'status': 'PENDING'
        }
        
        self.payment_submitted.emit(payment_data)
        QMessageBox.information(self, "Success", "Payment submitted for processing")
        self.clear_form()
    
    def validate_form(self):
        if not all([self.sender_name.text(), self.sender_account.text(),
                   self.receiver_name.text(), self.receiver_account.text(),
                   self.amount.text(), self.payment_purpose.toPlainText()]):
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return False
        
        try:
            amount = float(self.amount.text())
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount!")
            return False
        
        return True
    
    def clear_form(self):
        self.sender_name.clear()
        self.sender_account.clear()
        self.receiver_name.clear()
        self.receiver_account.clear()
        self.amount.clear()
        self.currency.setCurrentIndex(0)
        self.payment_purpose.clear()

class BankClerkWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Payment Processing - Bank Clerk")
        self.setMinimumSize(1000, 600)
        self.setup_ui()
        logger.info("Bank Clerk Window initialized")
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Settings
        settings_group = QGroupBox("Processing Settings")
        settings_layout = QHBoxLayout()
        
        self.use_llm_checkbox = QCheckBox("Use LLM for Screening")
        self.use_llm_checkbox.setChecked(True)
        settings_layout.addWidget(self.use_llm_checkbox)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(7)
        self.payments_table.setHorizontalHeaderLabels([
            "Reference", "Sender", "Receiver", "Amount", "Status", 
            "Risk Level", "Actions"
        ])
        layout.addWidget(self.payments_table)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_payments)
        layout.addWidget(refresh_button)
        
        self.load_payments()
    
    def load_payments(self):
        payments = self.db.get_all_payments()
        self.payments_table.setRowCount(len(payments))
        
        for i, payment in enumerate(payments):
            self.payments_table.setItem(i, 0, QTableWidgetItem(payment.reference))
            self.payments_table.setItem(i, 1, QTableWidgetItem(payment.sender_name))
            self.payments_table.setItem(i, 2, QTableWidgetItem(payment.receiver_name))
            self.payments_table.setItem(i, 3, QTableWidgetItem(
                f"{payment.amount} {payment.currency}"))
            self.payments_table.setItem(i, 4, QTableWidgetItem(payment.status))
            
            # Add view button if payment is pending
            if payment.status == 'PENDING':
                view_button = QPushButton("View")
                view_button.clicked.connect(
                    lambda checked, ref=payment.reference: self.view_payment(ref))
                self.payments_table.setCellWidget(i, 6, view_button)
    
    def view_payment(self, reference):
        logger.info(f"Viewing payment with reference: {reference}")
        payment = self.db.get_payment(reference)
        if payment:
            use_llm = self.use_llm_checkbox.isChecked()
            logger.info(f"Opening screening window with LLM={use_llm}")
            ScreeningResultWindow(payment, self.db, use_llm, self).show()

class ScreeningResultWindow(QMainWindow):
    def __init__(self, payment, db, use_llm=True, parent=None):
        super().__init__(parent)
        self.payment = payment
        self.db = db
        self.use_llm = use_llm
        self.setWindowTitle(f"Screening Result - {payment.reference}")
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Payment details
        details_text = f"""
        Payment Reference: {self.payment.reference}
        Sender: {self.payment.sender_name} ({self.payment.sender_account})
        Receiver: {self.payment.receiver_name} ({self.payment.receiver_account})
        Amount: {self.payment.amount} {self.payment.currency}
        Purpose: {self.payment.purpose}
        """
        details_label = QLabel(details_text)
        layout.addWidget(details_label)
        
        # Screening result
        if self.payment.llm_screening_result:
            result_label = QLabel("Screening Result:")
            result_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(result_label)
            
            result_text = QTextEdit()
            result_text.setPlainText(self.payment.llm_screening_result)
            result_text.setReadOnly(True)
            layout.addWidget(result_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        approve_button = QPushButton("Approve")
        approve_button.clicked.connect(self.approve_payment)
        reject_button = QPushButton("Reject")
        reject_button.clicked.connect(self.reject_payment)
        button_layout.addWidget(approve_button)
        button_layout.addWidget(reject_button)
        layout.addLayout(button_layout)
    
    def approve_payment(self):
        self.db.update_payment_status(
            self.payment.reference, 
            'APPROVED', 
            datetime.now()
        )
        self.close()
        if isinstance(self.parent(), BankClerkWindow):
            self.parent().load_payments()
    
    def reject_payment(self):
        self.db.update_payment_status(
            self.payment.reference, 
            'REJECTED', 
            datetime.now()
        )
        self.close()
        if isinstance(self.parent(), BankClerkWindow):
            self.parent().load_payments()

class PaymentSystem:
    def __init__(self):
        self.db = Database()
        self.client_window = ClientWindow()
        self.clerk_window = BankClerkWindow(self.db)
        
        # Connect signals
        self.client_window.payment_submitted.connect(self.process_payment)
        logger.info("Payment System initialized")
    
    def show(self):
        self.client_window.show()
        self.clerk_window.show()
    
    def process_payment(self, payment_data):
        logger.info(f"Processing new payment: {payment_data['reference']}")
        
        # Save to database
        payment = self.db.add_payment(payment_data)
        logger.info(f"Payment saved to database with ID: {payment.id}")
        
        # Start processing thread
        use_llm = self.clerk_window.use_llm_checkbox.isChecked()
        logger.info(f"Starting payment thread with LLM={use_llm}")
        self.payment_thread = PaymentThread(payment_data, use_llm)
        self.payment_thread.finished.connect(
            lambda result: self.handle_screening_result(payment.reference, result))
        self.payment_thread.start()
    
    def handle_screening_result(self, reference, result):
        logger.info(f"Handling screening result for payment {reference}")
        logger.debug(f"Screening result: {result}")
        
        payment = self.db.get_payment(reference)
        if payment:
            payment.llm_screening_result = str(result)
            payment.is_high_risk = result['risk_level'] == 'high'
            self.db.session.commit()
            logger.info(f"Updated payment {reference} with screening result")
            self.clerk_window.load_payments()

def main():
    app = QApplication(sys.argv)
    system = PaymentSystem()
    system.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
   
