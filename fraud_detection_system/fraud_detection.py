# fraud_detection.py

import sys
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QFormLayout, QProgressBar, QMessageBox, QHeaderView,
    QCheckBox, QDateTimeEdit, QSplitter
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor
from database import Database
from fraud_analyzer import FraudAnalyzer

class TransactionMonitoringThread(QThread):
    """Thread for real-time transaction monitoring and fraud detection"""
    
    transaction_processed = pyqtSignal(dict)
    fraud_detected = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    
    def __init__(self, database, fraud_analyzer):
        super().__init__()
        self.database = database
        self.fraud_analyzer = fraud_analyzer
        self.running = False
        self.processing_delay = 2  # seconds between transaction processing
        
        # Transaction templates for simulation
        self.transaction_templates = [
            {
                'type': 'purchase',
                'merchant_category': 'grocery',
                'amount_range': (10, 200),
                'location': 'local',
                'risk_level': 'low'
            },
            {
                'type': 'purchase',
                'merchant_category': 'gas_station',
                'amount_range': (20, 100),
                'location': 'local',
                'risk_level': 'low'
            },
            {
                'type': 'purchase',
                'merchant_category': 'restaurant',
                'amount_range': (15, 150),
                'location': 'local',
                'risk_level': 'low'
            },
            {
                'type': 'withdrawal',
                'merchant_category': 'atm',
                'amount_range': (20, 500),
                'location': 'local',
                'risk_level': 'medium'
            },
            {
                'type': 'purchase',
                'merchant_category': 'online',
                'amount_range': (25, 1000),
                'location': 'remote',
                'risk_level': 'medium'
            },
            {
                'type': 'transfer',
                'merchant_category': 'wire_transfer',
                'amount_range': (100, 5000),
                'location': 'international',
                'risk_level': 'high'
            },
            {
                'type': 'purchase',
                'merchant_category': 'luxury',
                'amount_range': (500, 10000),
                'location': 'remote',
                'risk_level': 'high'
            },
            # Suspicious patterns
            {
                'type': 'purchase',
                'merchant_category': 'electronics',
                'amount_range': (2000, 8000),
                'location': 'foreign',
                'risk_level': 'high',
                'suspicious': True
            },
            {
                'type': 'withdrawal',
                'merchant_category': 'atm',
                'amount_range': (1000, 2000),
                'location': 'foreign',
                'risk_level': 'high',
                'suspicious': True
            }
        ]
        
        # Customer profiles for simulation
        self.customer_profiles = [
            {
                'customer_id': 'CUST001',
                'name': 'Alice Johnson',
                'account_type': 'premium',
                'avg_monthly_spending': 3000,
                'typical_locations': ['New York', 'Boston'],
                'risk_profile': 'low'
            },
            {
                'customer_id': 'CUST002',
                'name': 'Bob Smith',
                'account_type': 'standard',
                'avg_monthly_spending': 1500,
                'typical_locations': ['Chicago'],
                'risk_profile': 'low'
            },
            {
                'customer_id': 'CUST003',
                'name': 'Carol Davis',
                'account_type': 'business',
                'avg_monthly_spending': 8000,
                'typical_locations': ['Los Angeles', 'San Francisco'],
                'risk_profile': 'medium'
            },
            {
                'customer_id': 'CUST004',
                'name': 'David Wilson',
                'account_type': 'standard',
                'avg_monthly_spending': 2000,
                'typical_locations': ['Miami'],
                'risk_profile': 'medium'
            },
            {
                'customer_id': 'CUST005',
                'name': 'Eve Brown',
                'account_type': 'premium',
                'avg_monthly_spending': 5000,
                'typical_locations': ['Seattle', 'Portland'],
                'risk_profile': 'low'
            }
        ]
    
    def run(self):
        """Main monitoring loop"""
        self.running = True
        self.status_update.emit("Transaction monitoring started")
        
        while self.running:
            try:
                # Generate and process a transaction
                transaction = self._generate_transaction()
                
                # Analyze for fraud
                fraud_result = self.fraud_analyzer.analyze_transaction(transaction)
                
                # Update transaction with fraud analysis results
                transaction.update({
                    'fraud_score': fraud_result.get('fraud_score', 0),
                    'risk_level': fraud_result.get('risk_level', 'low'),
                    'fraud_indicators': fraud_result.get('fraud_indicators', []),
                    'analysis_method': fraud_result.get('analysis_method', 'rule_based'),
                    'status': 'flagged' if fraud_result.get('is_fraud', False) else 'approved',
                    'ai_confidence': fraud_result.get('ai_confidence', 0)
                })
                
                # Save to database
                self.database.add_transaction(transaction)
                
                # Emit signals
                self.transaction_processed.emit(transaction)
                
                if fraud_result.get('is_fraud', False):
                    self.fraud_detected.emit(transaction)
                
                # Update status
                status = f"Processed transaction {transaction['transaction_id']} - {transaction['status'].upper()}"
                self.status_update.emit(status)
                
                # Wait before processing next transaction
                time.sleep(self.processing_delay)
                
            except Exception as e:
                self.status_update.emit(f"Error processing transaction: {str(e)}")
                time.sleep(1)
        
        self.status_update.emit("Transaction monitoring stopped")
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
    
    def set_processing_delay(self, delay: float):
        """Set the delay between transaction processing"""
        self.processing_delay = delay
    
    def _generate_transaction(self) -> Dict[str, Any]:
        """Generate a simulated transaction"""
        # Select random template and customer
        template = random.choice(self.transaction_templates)
        customer = random.choice(self.customer_profiles)
        
        # Generate transaction ID
        transaction_id = f"TXN{int(time.time())}{random.randint(100, 999)}"
        
        # Generate amount within template range
        amount = round(random.uniform(*template['amount_range']), 2)
        
        # Determine location
        if template['location'] == 'local':
            location = random.choice(customer['typical_locations'])
        elif template['location'] == 'remote':
            remote_locations = ['Las Vegas', 'Orlando', 'Denver', 'Phoenix', 'Atlanta']
            location = random.choice(remote_locations)
        elif template['location'] == 'foreign':
            foreign_locations = ['London, UK', 'Paris, France', 'Tokyo, Japan', 'Sydney, Australia']
            location = random.choice(foreign_locations)
        else:
            location = random.choice(customer['typical_locations'])
        
        # Generate merchant name
        merchant_names = {
            'grocery': ['SuperMart', 'FreshFoods', 'QuickShop', 'GreenGrocer'],
            'gas_station': ['FuelStop', 'QuickGas', 'EnergyPlus', 'SpeedFuel'],
            'restaurant': ['Tasty Bites', 'Golden Spoon', 'Urban Kitchen', 'Cafe Delight'],
            'atm': ['CityBank ATM', 'QuickCash ATM', 'BankPlus ATM', 'Express ATM'],
            'online': ['WebStore', 'DigitalMart', 'OnlineShop', 'CyberStore'],
            'wire_transfer': ['International Wire', 'Global Transfer', 'Swift Transfer'],
            'luxury': ['Luxury Boutique', 'Premium Store', 'Elite Shopping', 'High-End Retail'],
            'electronics': ['TechWorld', 'ElectroMart', 'GadgetStore', 'DigitalHub']
        }
        
        merchant = random.choice(merchant_names.get(template['merchant_category'], ['Unknown Merchant']))
        
        # Add suspicious patterns if marked
        if template.get('suspicious', False):
            # Make amount unusually high for customer profile
            if amount < customer['avg_monthly_spending'] * 0.5:
                amount = customer['avg_monthly_spending'] * random.uniform(0.8, 1.5)
        
        # Generate timestamp (recent)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
        
        transaction = {
            'transaction_id': transaction_id,
            'customer_id': customer['customer_id'],
            'customer_name': customer['name'],
            'amount': amount,
            'merchant': merchant,
            'merchant_category': template['merchant_category'],
            'transaction_type': template['type'],
            'location': location,
            'timestamp': timestamp.isoformat(),
            'account_type': customer['account_type'],
            'customer_risk_profile': customer['risk_profile'],
            'template_risk_level': template['risk_level'],
            'is_suspicious_template': template.get('suspicious', False)
        }
        
        return transaction

class TransactionInputWindow(QWidget):
    """Window for manual transaction input"""
    
    transaction_submitted = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Manual Transaction Input")
        self.setGeometry(200, 200, 500, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Manual Transaction Entry")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Form
        form_group = QGroupBox("Transaction Details")
        form_layout = QFormLayout()
        
        # Customer ID
        self.customer_id_input = QComboBox()
        self.customer_id_input.addItems(['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005'])
        self.customer_id_input.setEditable(True)
        form_layout.addRow("Customer ID:", self.customer_id_input)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(100.00)
        form_layout.addRow("Amount ($):", self.amount_input)
        
        # Merchant
        self.merchant_input = QLineEdit()
        self.merchant_input.setPlaceholderText("Enter merchant name")
        form_layout.addRow("Merchant:", self.merchant_input)
        
        # Merchant Category
        self.category_input = QComboBox()
        self.category_input.addItems([
            'grocery', 'gas_station', 'restaurant', 'atm', 'online',
            'wire_transfer', 'luxury', 'electronics', 'other'
        ])
        form_layout.addRow("Category:", self.category_input)
        
        # Transaction Type
        self.type_input = QComboBox()
        self.type_input.addItems(['purchase', 'withdrawal', 'transfer', 'deposit'])
        form_layout.addRow("Type:", self.type_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter location")
        form_layout.addRow("Location:", self.location_input)
        
        # Timestamp
        self.timestamp_input = QDateTimeEdit()
        self.timestamp_input.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Timestamp:", self.timestamp_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Submit button
        self.submit_button = QPushButton("Submit Transaction")
        self.submit_button.clicked.connect(self.submit_transaction)
        layout.addWidget(self.submit_button)
        
        # Status
        self.status_label = QLabel("Ready to submit transaction")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def submit_transaction(self):
        """Submit the manual transaction"""
        try:
            # Generate transaction ID
            transaction_id = f"MAN{int(time.time())}{random.randint(100, 999)}"
            
            # Create transaction data
            transaction = {
                'transaction_id': transaction_id,
                'customer_id': self.customer_id_input.currentText(),
                'customer_name': f"Customer {self.customer_id_input.currentText()}",
                'amount': self.amount_input.value(),
                'merchant': self.merchant_input.text() or "Unknown Merchant",
                'merchant_category': self.category_input.currentText(),
                'transaction_type': self.type_input.currentText(),
                'location': self.location_input.text() or "Unknown Location",
                'timestamp': self.timestamp_input.dateTime().toPython().isoformat(),
                'account_type': 'standard',
                'customer_risk_profile': 'medium',
                'template_risk_level': 'medium',
                'is_suspicious_template': False,
                'manual_entry': True
            }
            
            # Emit signal
            self.transaction_submitted.emit(transaction)
            
            # Update status
            self.status_label.setText(f"Transaction {transaction_id} submitted successfully")
            
            # Reset form
            self.amount_input.setValue(100.00)
            self.merchant_input.clear()
            self.location_input.clear()
            self.timestamp_input.setDateTime(QDateTime.currentDateTime())
            
        except Exception as e:
            self.status_label.setText(f"Error submitting transaction: {str(e)}")

class FraudAnalystWindow(QWidget):
    """Window for fraud analysts to review flagged transactions"""
    
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.init_ui()
        self.refresh_flagged_transactions()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Fraud Analyst Dashboard")
        self.setGeometry(300, 300, 1000, 700)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Fraud Analyst Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_flagged_transactions)
        controls_layout.addWidget(self.refresh_button)
        
        self.auto_refresh_checkbox = QCheckBox("Auto Refresh (5s)")
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_checkbox)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Flagged transactions table
        self.flagged_table = QTableWidget()
        self.flagged_table.setColumnCount(12)
        self.flagged_table.setHorizontalHeaderLabels([
            "Transaction ID", "Customer", "Amount", "Merchant", "Location",
            "Fraud Score", "Risk Level", "Status", "Timestamp", "Method", "Confidence", "Actions"
        ])
        
        # Set column widths
        header = self.flagged_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.flagged_table.itemDoubleClicked.connect(self.view_transaction_details)
        layout.addWidget(self.flagged_table)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout()
        
        self.total_flagged_label = QLabel("Total Flagged: 0")
        self.high_risk_label = QLabel("High Risk: 0")
        self.pending_review_label = QLabel("Pending Review: 0")
        
        stats_layout.addWidget(self.total_flagged_label)
        stats_layout.addWidget(self.high_risk_label)
        stats_layout.addWidget(self.pending_review_label)
        stats_layout.addStretch()
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.setLayout(layout)
        
        # Auto refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_flagged_transactions)
    
    def toggle_auto_refresh(self, enabled):
        """Toggle auto refresh"""
        if enabled:
            self.refresh_timer.start(5000)  # 5 seconds
        else:
            self.refresh_timer.stop()
    
    def refresh_flagged_transactions(self):
        """Refresh the flagged transactions table"""
        try:
            flagged_transactions = self.database.get_flagged_transactions()
            
            self.flagged_table.setRowCount(len(flagged_transactions))
            
            for row, transaction in enumerate(flagged_transactions):
                # Transaction ID
                self.flagged_table.setItem(row, 0, QTableWidgetItem(transaction.transaction_id))
                
                # Customer
                self.flagged_table.setItem(row, 1, QTableWidgetItem(transaction.customer_name or transaction.customer_id))
                
                # Amount
                amount_item = QTableWidgetItem(f"${transaction.amount:,.2f}")
                self.flagged_table.setItem(row, 2, amount_item)
                
                # Merchant
                self.flagged_table.setItem(row, 3, QTableWidgetItem(transaction.merchant))
                
                # Location
                self.flagged_table.setItem(row, 4, QTableWidgetItem(transaction.location))
                
                # Fraud Score
                score_item = QTableWidgetItem(f"{transaction.fraud_score:.1f}")
                if transaction.fraud_score >= 80:
                    score_item.setBackground(QColor(255, 200, 200))  # Light red
                elif transaction.fraud_score >= 60:
                    score_item.setBackground(QColor(255, 255, 200))  # Light yellow
                self.flagged_table.setItem(row, 5, score_item)
                
                # Risk Level
                risk_item = QTableWidgetItem(transaction.risk_level.upper())
                if transaction.risk_level == 'high':
                    risk_item.setBackground(QColor(255, 200, 200))
                elif transaction.risk_level == 'medium':
                    risk_item.setBackground(QColor(255, 255, 200))
                self.flagged_table.setItem(row, 6, risk_item)
                
                # Status
                status_item = QTableWidgetItem(transaction.status.upper())
                self.flagged_table.setItem(row, 7, status_item)
                
                # Timestamp
                timestamp = datetime.fromisoformat(transaction.timestamp.replace('Z', '+00:00'))
                self.flagged_table.setItem(row, 8, QTableWidgetItem(timestamp.strftime("%Y-%m-%d %H:%M")))
                
                # Method
                self.flagged_table.setItem(row, 9, QTableWidgetItem(transaction.analysis_method or 'rule_based'))
                
                # Confidence
                confidence = transaction.ai_confidence or 0
                self.flagged_table.setItem(row, 10, QTableWidgetItem(f"{confidence:.0f}%"))
                
                # Actions (placeholder)
                self.flagged_table.setItem(row, 11, QTableWidgetItem("Review"))
            
            # Update statistics
            self._update_statistics(flagged_transactions)
            
        except Exception as e:
            print(f"Error refreshing flagged transactions: {e}")
    
    def _update_statistics(self, transactions):
        """Update statistics labels"""
        total_flagged = len(transactions)
        high_risk = sum(1 for t in transactions if t.risk_level == 'high')
        pending_review = sum(1 for t in transactions if t.status == 'flagged')
        
        self.total_flagged_label.setText(f"Total Flagged: {total_flagged}")
        self.high_risk_label.setText(f"High Risk: {high_risk}")
        self.pending_review_label.setText(f"Pending Review: {pending_review}")
    
    def view_transaction_details(self, item):
        """View detailed information about a transaction"""
        row = item.row()
        transaction_id = self.flagged_table.item(row, 0).text()
        
        try:
            transaction = self.database.get_transaction_by_id(transaction_id)
            if transaction:
                self._show_transaction_details(transaction)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load transaction details: {str(e)}")
    
    def _show_transaction_details(self, transaction):
        """Show detailed transaction information in a dialog"""
        details = f"""Transaction Details:

Transaction ID: {transaction.transaction_id}
Customer: {transaction.customer_name} ({transaction.customer_id})
Amount: ${transaction.amount:,.2f}
Merchant: {transaction.merchant}
Category: {transaction.merchant_category}
Type: {transaction.transaction_type}
Location: {transaction.location}
Timestamp: {transaction.timestamp}

Fraud Analysis:
Fraud Score: {transaction.fraud_score:.1f}/100
Risk Level: {transaction.risk_level.upper()}
Status: {transaction.status.upper()}
Analysis Method: {transaction.analysis_method or 'rule_based'}
AI Confidence: {transaction.ai_confidence or 0:.0f}%

Fraud Indicators:
{chr(10).join(transaction.fraud_indicators.split(',') if transaction.fraud_indicators else ['None'])}

Account Information:
Account Type: {transaction.account_type or 'N/A'}
Customer Risk Profile: {transaction.customer_risk_profile or 'N/A'}"""
        
        QMessageBox.information(self, "Transaction Details", details)

class FraudDetectionSystem(QMainWindow):
    """Main fraud detection system application"""
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.fraud_analyzer = FraudAnalyzer()
        self.monitoring_thread = None
        self.init_ui()
        self.setup_monitoring()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Fraud Detection System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Real-Time Fraud Detection System")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Monitoring tab
        self.monitoring_tab = self._create_monitoring_tab()
        self.tab_widget.addTab(self.monitoring_tab, "Real-Time Monitoring")
        
        # Manual input tab
        self.input_window = TransactionInputWindow()
        self.input_window.transaction_submitted.connect(self.process_manual_transaction)
        self.tab_widget.addTab(self.input_window, "Manual Transaction")
        
        # Analyst dashboard tab
        self.analyst_window = FraudAnalystWindow(self.database)
        self.tab_widget.addTab(self.analyst_window, "Fraud Analysis")
        
        layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(layout)
    
    def _create_monitoring_tab(self):
        """Create the real-time monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_group = QGroupBox("Monitoring Controls")
        controls_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        controls_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        
        # Processing delay control
        controls_layout.addWidget(QLabel("Delay (s):"))
        self.delay_spinbox = QDoubleSpinBox()
        self.delay_spinbox.setRange(0.1, 10.0)
        self.delay_spinbox.setValue(2.0)
        self.delay_spinbox.setSingleStep(0.1)
        self.delay_spinbox.valueChanged.connect(self.update_processing_delay)
        controls_layout.addWidget(self.delay_spinbox)
        
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Status and progress
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("System ready")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Recent transactions and alerts
        splitter = QSplitter()
        
        # Recent transactions
        transactions_group = QGroupBox("Recent Transactions")
        transactions_layout = QVBoxLayout()
        
        self.transactions_text = QTextEdit()
        self.transactions_text.setMaximumHeight(200)
        transactions_layout.addWidget(self.transactions_text)
        
        transactions_group.setLayout(transactions_layout)
        splitter.addWidget(transactions_group)
        
        # Fraud alerts
        alerts_group = QGroupBox("Fraud Alerts")
        alerts_layout = QVBoxLayout()
        
        self.alerts_text = QTextEdit()
        self.alerts_text.setMaximumHeight(200)
        self.alerts_text.setStyleSheet("QTextEdit { background-color: #ffe6e6; }")
        alerts_layout.addWidget(self.alerts_text)
        
        alerts_group.setLayout(alerts_layout)
        splitter.addWidget(alerts_group)
        
        layout.addWidget(splitter)
        
        widget.setLayout(layout)
        return widget
    
    def setup_monitoring(self):
        """Setup the monitoring thread"""
        self.monitoring_thread = TransactionMonitoringThread(self.database, self.fraud_analyzer)
        self.monitoring_thread.transaction_processed.connect(self.on_transaction_processed)
        self.monitoring_thread.fraud_detected.connect(self.on_fraud_detected)
        self.monitoring_thread.status_update.connect(self.on_status_update)
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring_thread and not self.monitoring_thread.isRunning():
            self.monitoring_thread.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if self.monitoring_thread and self.monitoring_thread.isRunning():
            self.monitoring_thread.stop()
            self.monitoring_thread.wait()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setVisible(False)
    
    def update_processing_delay(self, delay):
        """Update the processing delay"""
        if self.monitoring_thread:
            self.monitoring_thread.set_processing_delay(delay)
    
    def process_manual_transaction(self, transaction):
        """Process a manually entered transaction"""
        try:
            # Analyze for fraud
            fraud_result = self.fraud_analyzer.analyze_transaction(transaction)
            
            # Update transaction with fraud analysis results
            transaction.update({
                'fraud_score': fraud_result.get('fraud_score', 0),
                'risk_level': fraud_result.get('risk_level', 'low'),
                'fraud_indicators': fraud_result.get('fraud_indicators', []),
                'analysis_method': fraud_result.get('analysis_method', 'rule_based'),
                'status': 'flagged' if fraud_result.get('is_fraud', False) else 'approved',
                'ai_confidence': fraud_result.get('ai_confidence', 0)
            })
            
            # Save to database
            self.database.add_transaction(transaction)
            
            # Update displays
            self.on_transaction_processed(transaction)
            
            if fraud_result.get('is_fraud', False):
                self.on_fraud_detected(transaction)
            
            # Refresh analyst dashboard
            self.analyst_window.refresh_flagged_transactions()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error processing manual transaction: {str(e)}")
    
    def on_transaction_processed(self, transaction):
        """Handle processed transaction"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = transaction['status'].upper()
        amount = transaction['amount']
        merchant = transaction['merchant']
        score = transaction.get('fraud_score', 0)
        
        message = f"[{timestamp}] {status} - ${amount:,.2f} at {merchant} (Score: {score:.1f})\n"
        self.transactions_text.append(message)
        
        # Keep only last 50 lines
        text = self.transactions_text.toPlainText()
        lines = text.split('\n')
        if len(lines) > 50:
            self.transactions_text.setPlainText('\n'.join(lines[-50:]))
    
    def on_fraud_detected(self, transaction):
        """Handle fraud detection"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        customer = transaction.get('customer_name', transaction.get('customer_id', 'Unknown'))
        amount = transaction['amount']
        merchant = transaction['merchant']
        score = transaction.get('fraud_score', 0)
        risk = transaction.get('risk_level', 'unknown').upper()
        
        alert = f"[{timestamp}] FRAUD ALERT - {customer}: ${amount:,.2f} at {merchant}\n"
        alert += f"Risk Level: {risk}, Score: {score:.1f}\n"
        
        indicators = transaction.get('fraud_indicators', [])
        if isinstance(indicators, str):
            indicators = indicators.split(',') if indicators else []
        
        if indicators:
            alert += f"Indicators: {', '.join(indicators)}\n"
        
        alert += "\n"
        
        self.alerts_text.append(alert)
        
        # Keep only last 20 alerts
        text = self.alerts_text.toPlainText()
        alerts = text.split('\n\n')
        if len(alerts) > 20:
            self.alerts_text.setPlainText('\n\n'.join(alerts[-20:]))
    
    def on_status_update(self, status):
        """Handle status updates"""
        self.status_label.setText(status)
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.monitoring_thread and self.monitoring_thread.isRunning():
            self.monitoring_thread.stop()
            self.monitoring_thread.wait()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = FraudDetectionSystem()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()