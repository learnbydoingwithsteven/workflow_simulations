import sys
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox,
    QProgressBar, QMessageBox, QSplitter, QFrame, QDateEdit,
    QCheckBox, QSlider, QScrollArea, QGridLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt
import requests

@dataclass
class AuditFinding:
    finding_id: str
    audit_id: str
    category: str
    severity: str
    description: str
    recommendation: str
    status: str
    assigned_to: str
    due_date: str
    created_date: str

@dataclass
class AuditPlan:
    plan_id: str
    audit_type: str
    department: str
    scope: str
    start_date: str
    end_date: str
    auditor: str
    status: str
    risk_level: str
    objectives: List[str]
    procedures: List[str]

class AuditProcessingThread(QThread):
    progress_updated = pyqtSignal(str, int)
    audit_completed = pyqtSignal(str, dict)
    finding_generated = pyqtSignal(dict)
    
    def __init__(self, audit_plan: AuditPlan):
        super().__init__()
        self.audit_plan = audit_plan
        self.is_running = True
        
    def run(self):
        """Simulate audit execution process"""
        try:
            # Phase 1: Planning and Preparation
            self.progress_updated.emit("Planning and Preparation", 10)
            time.sleep(2)
            
            # Phase 2: Risk Assessment
            self.progress_updated.emit("Conducting Risk Assessment", 25)
            risk_assessment = self.perform_risk_assessment()
            time.sleep(3)
            
            # Phase 3: Control Testing
            self.progress_updated.emit("Testing Internal Controls", 50)
            control_results = self.test_internal_controls()
            time.sleep(4)
            
            # Phase 4: Substantive Testing
            self.progress_updated.emit("Performing Substantive Testing", 75)
            substantive_results = self.perform_substantive_testing()
            time.sleep(3)
            
            # Phase 5: AI-Powered Analysis
            self.progress_updated.emit("AI Analysis and Pattern Detection", 85)
            ai_insights = self.perform_ai_analysis()
            time.sleep(2)
            
            # Phase 6: Generate Findings
            self.progress_updated.emit("Generating Audit Findings", 95)
            findings = self.generate_findings(risk_assessment, control_results, substantive_results, ai_insights)
            
            # Phase 7: Finalization
            self.progress_updated.emit("Finalizing Audit Report", 100)
            
            audit_result = {
                'audit_id': self.audit_plan.plan_id,
                'status': 'Completed',
                'completion_date': datetime.now().isoformat(),
                'risk_assessment': risk_assessment,
                'control_results': control_results,
                'substantive_results': substantive_results,
                'ai_insights': ai_insights,
                'findings_count': len(findings),
                'high_risk_findings': len([f for f in findings if f['severity'] == 'High']),
                'medium_risk_findings': len([f for f in findings if f['severity'] == 'Medium']),
                'low_risk_findings': len([f for f in findings if f['severity'] == 'Low'])
            }
            
            # Emit findings
            for finding in findings:
                self.finding_generated.emit(finding)
                time.sleep(0.5)
            
            self.audit_completed.emit(self.audit_plan.plan_id, audit_result)
            
        except Exception as e:
            print(f"Error in audit processing: {e}")
    
    def perform_risk_assessment(self) -> Dict:
        """Simulate risk assessment process"""
        risk_factors = [
            'Financial reporting accuracy',
            'Regulatory compliance',
            'Operational efficiency',
            'Data security and privacy',
            'Fraud prevention',
            'Asset protection',
            'Process controls',
            'IT general controls'
        ]
        
        assessment = {}
        for factor in risk_factors:
            risk_level = random.choice(['Low', 'Medium', 'High'])
            impact = random.randint(1, 10)
            likelihood = random.randint(1, 10)
            assessment[factor] = {
                'risk_level': risk_level,
                'impact': impact,
                'likelihood': likelihood,
                'risk_score': impact * likelihood
            }
        
        return assessment
    
    def test_internal_controls(self) -> Dict:
        """Simulate internal control testing"""
        controls = [
            'Authorization controls',
            'Segregation of duties',
            'Documentation controls',
            'Physical safeguards',
            'Independent verification',
            'Information processing controls',
            'Performance reviews',
            'Reconciliation controls'
        ]
        
        results = {}
        for control in controls:
            effectiveness = random.choice(['Effective', 'Partially Effective', 'Ineffective'])
            test_results = random.randint(70, 100)
            deficiencies = random.randint(0, 5)
            
            results[control] = {
                'effectiveness': effectiveness,
                'test_score': test_results,
                'deficiencies_found': deficiencies,
                'sample_size': random.randint(20, 100),
                'exceptions': random.randint(0, 10)
            }
        
        return results
    
    def perform_substantive_testing(self) -> Dict:
        """Simulate substantive testing procedures"""
        procedures = [
            'Account reconciliations',
            'Transaction testing',
            'Analytical procedures',
            'Confirmation procedures',
            'Physical inventory counts',
            'Cut-off testing',
            'Valuation testing',
            'Completeness testing'
        ]
        
        results = {}
        for procedure in procedures:
            accuracy = random.randint(85, 100)
            errors_found = random.randint(0, 8)
            materiality_threshold = random.randint(1000, 50000)
            
            results[procedure] = {
                'accuracy_rate': accuracy,
                'errors_identified': errors_found,
                'materiality_threshold': materiality_threshold,
                'population_tested': random.randint(100, 1000),
                'sample_tested': random.randint(20, 100)
            }
        
        return results
    
    def perform_ai_analysis(self) -> Dict:
        """Simulate AI-powered audit analysis"""
        try:
            # Simulate AI analysis with Ollama
            prompt = f"""
            Analyze the following audit scenario for {self.audit_plan.department} department:
            
            Audit Type: {self.audit_plan.audit_type}
            Risk Level: {self.audit_plan.risk_level}
            Scope: {self.audit_plan.scope}
            
            Please provide insights on:
            1. Key risk areas to focus on
            2. Potential control weaknesses
            3. Recommended audit procedures
            4. Red flags to watch for
            5. Industry-specific considerations
            
            Respond in JSON format with structured analysis.
            """
            
            # Try to get AI insights
            ai_response = self.get_ai_insights(prompt)
            
            if ai_response:
                return ai_response
            else:
                # Fallback to rule-based analysis
                return self.rule_based_analysis()
                
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self.rule_based_analysis()
    
    def get_ai_insights(self, prompt: str) -> Optional[Dict]:
        """Get insights from AI model"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get('response', '')
                
                # Try to parse JSON from AI response
                try:
                    # Extract JSON from response
                    start_idx = ai_text.find('{')
                    end_idx = ai_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = ai_text[start_idx:end_idx]
                        return json.loads(json_str)
                except:
                    pass
                
                # If JSON parsing fails, create structured response
                return {
                    'ai_analysis': ai_text,
                    'risk_indicators': ['High transaction volumes', 'Manual processes', 'Limited oversight'],
                    'control_recommendations': ['Implement automated controls', 'Enhance monitoring', 'Improve documentation'],
                    'focus_areas': ['Revenue recognition', 'Expense management', 'Asset valuation'],
                    'confidence_score': random.randint(75, 95)
                }
            
        except Exception as e:
            print(f"AI request error: {e}")
            return None
    
    def rule_based_analysis(self) -> Dict:
        """Fallback rule-based analysis"""
        department_risks = {
            'Finance': ['Revenue recognition', 'Financial reporting', 'Cash management'],
            'Operations': ['Process efficiency', 'Quality control', 'Resource utilization'],
            'IT': ['Data security', 'System availability', 'Access controls'],
            'HR': ['Payroll accuracy', 'Compliance', 'Employee data protection'],
            'Procurement': ['Vendor management', 'Contract compliance', 'Cost control']
        }
        
        audit_type_procedures = {
            'Financial': ['Account reconciliation', 'Transaction testing', 'Analytical review'],
            'Operational': ['Process mapping', 'Efficiency analysis', 'Control testing'],
            'Compliance': ['Regulatory review', 'Policy adherence', 'Documentation check'],
            'IT': ['Security assessment', 'Access review', 'Data integrity check']
        }
        
        risks = department_risks.get(self.audit_plan.department, ['General business risks'])
        procedures = audit_type_procedures.get(self.audit_plan.audit_type, ['Standard procedures'])
        
        return {
            'identified_risks': risks,
            'recommended_procedures': procedures,
            'risk_score': random.randint(60, 90),
            'control_effectiveness': random.choice(['Strong', 'Adequate', 'Weak']),
            'analysis_method': 'Rule-based',
            'confidence_score': random.randint(70, 85)
        }
    
    def generate_findings(self, risk_assessment: Dict, control_results: Dict, 
                         substantive_results: Dict, ai_insights: Dict) -> List[Dict]:
        """Generate audit findings based on test results"""
        findings = []
        
        # Generate findings based on control deficiencies
        for control, result in control_results.items():
            if result['effectiveness'] == 'Ineffective' or result['deficiencies_found'] > 3:
                finding = {
                    'finding_id': f"F{random.randint(1000, 9999)}",
                    'audit_id': self.audit_plan.plan_id,
                    'category': 'Internal Controls',
                    'severity': 'High' if result['effectiveness'] == 'Ineffective' else 'Medium',
                    'description': f"Control deficiency identified in {control.lower()}",
                    'recommendation': f"Strengthen {control.lower()} to ensure proper oversight",
                    'status': 'Open',
                    'assigned_to': 'Management',
                    'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
                    'created_date': datetime.now().isoformat()
                }
                findings.append(finding)
        
        # Generate findings based on substantive testing
        for procedure, result in substantive_results.items():
            if result['errors_identified'] > 5 or result['accuracy_rate'] < 90:
                severity = 'High' if result['accuracy_rate'] < 85 else 'Medium'
                finding = {
                    'finding_id': f"F{random.randint(1000, 9999)}",
                    'audit_id': self.audit_plan.plan_id,
                    'category': 'Substantive Testing',
                    'severity': severity,
                    'description': f"Errors identified in {procedure.lower()}",
                    'recommendation': f"Review and improve {procedure.lower()} procedures",
                    'status': 'Open',
                    'assigned_to': 'Department Head',
                    'due_date': (datetime.now() + timedelta(days=45)).isoformat(),
                    'created_date': datetime.now().isoformat()
                }
                findings.append(finding)
        
        # Generate findings based on risk assessment
        for risk_factor, assessment in risk_assessment.items():
            if assessment['risk_score'] > 70:
                finding = {
                    'finding_id': f"F{random.randint(1000, 9999)}",
                    'audit_id': self.audit_plan.plan_id,
                    'category': 'Risk Management',
                    'severity': 'High' if assessment['risk_score'] > 80 else 'Medium',
                    'description': f"High risk identified in {risk_factor.lower()}",
                    'recommendation': f"Implement additional controls for {risk_factor.lower()}",
                    'status': 'Open',
                    'assigned_to': 'Risk Manager',
                    'due_date': (datetime.now() + timedelta(days=60)).isoformat(),
                    'created_date': datetime.now().isoformat()
                }
                findings.append(finding)
        
        return findings

class AuditPlanWindow(QWidget):
    audit_submitted = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create Audit Plan")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Form
        form_layout = QGridLayout()
        
        # Audit Type
        form_layout.addWidget(QLabel("Audit Type:"), 0, 0)
        self.audit_type = QComboBox()
        self.audit_type.addItems(["Financial", "Operational", "Compliance", "IT", "Performance"])
        form_layout.addWidget(self.audit_type, 0, 1)
        
        # Department
        form_layout.addWidget(QLabel("Department:"), 1, 0)
        self.department = QComboBox()
        self.department.addItems(["Finance", "Operations", "IT", "HR", "Procurement", "Sales", "Marketing"])
        form_layout.addWidget(self.department, 1, 1)
        
        # Scope
        form_layout.addWidget(QLabel("Audit Scope:"), 2, 0)
        self.scope = QTextEdit()
        self.scope.setMaximumHeight(80)
        self.scope.setPlaceholderText("Describe the scope and objectives of the audit...")
        form_layout.addWidget(self.scope, 2, 1)
        
        # Start Date
        form_layout.addWidget(QLabel("Start Date:"), 3, 0)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        form_layout.addWidget(self.start_date, 3, 1)
        
        # End Date
        form_layout.addWidget(QLabel("End Date:"), 4, 0)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(30))
        form_layout.addWidget(self.end_date, 4, 1)
        
        # Auditor
        form_layout.addWidget(QLabel("Lead Auditor:"), 5, 0)
        self.auditor = QComboBox()
        self.auditor.addItems(["John Smith", "Sarah Johnson", "Mike Davis", "Lisa Chen", "David Wilson"])
        form_layout.addWidget(self.auditor, 5, 1)
        
        # Risk Level
        form_layout.addWidget(QLabel("Risk Level:"), 6, 0)
        self.risk_level = QComboBox()
        self.risk_level.addItems(["Low", "Medium", "High"])
        form_layout.addWidget(self.risk_level, 6, 1)
        
        layout.addLayout(form_layout)
        
        # Objectives
        objectives_group = QGroupBox("Audit Objectives")
        objectives_layout = QVBoxLayout()
        
        self.objectives = QTextEdit()
        self.objectives.setMaximumHeight(100)
        self.objectives.setPlaceholderText("List the key objectives of this audit...")
        objectives_layout.addWidget(self.objectives)
        
        objectives_group.setLayout(objectives_layout)
        layout.addWidget(objectives_group)
        
        # Procedures
        procedures_group = QGroupBox("Audit Procedures")
        procedures_layout = QVBoxLayout()
        
        self.procedures = QTextEdit()
        self.procedures.setMaximumHeight(100)
        self.procedures.setPlaceholderText("Outline the audit procedures to be performed...")
        procedures_layout.addWidget(self.procedures)
        
        procedures_group.setLayout(procedures_layout)
        layout.addWidget(procedures_group)
        
        # Submit Button
        submit_btn = QPushButton("Create Audit Plan")
        submit_btn.clicked.connect(self.submit_audit_plan)
        layout.addWidget(submit_btn)
        
        self.setLayout(layout)
    
    def submit_audit_plan(self):
        plan_data = {
            'plan_id': f"AUD{random.randint(1000, 9999)}",
            'audit_type': self.audit_type.currentText(),
            'department': self.department.currentText(),
            'scope': self.scope.toPlainText(),
            'start_date': self.start_date.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date.date().toString("yyyy-MM-dd"),
            'auditor': self.auditor.currentText(),
            'status': 'Planned',
            'risk_level': self.risk_level.currentText(),
            'objectives': self.objectives.toPlainText().split('\n') if self.objectives.toPlainText() else [],
            'procedures': self.procedures.toPlainText().split('\n') if self.procedures.toPlainText() else []
        }
        
        self.audit_submitted.emit(plan_data)
        
        # Clear form
        self.scope.clear()
        self.objectives.clear()
        self.procedures.clear()
        
        QMessageBox.information(self, "Success", "Audit plan created successfully!")

class AuditorDashboard(QWidget):
    audit_started = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.audit_plans = []
        self.audit_results = {}
        self.findings = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Auditor Dashboard")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Audit Plans Tab
        plans_tab = QWidget()
        plans_layout = QVBoxLayout()
        
        # Plans Table
        self.plans_table = QTableWidget()
        self.plans_table.setColumnCount(8)
        self.plans_table.setHorizontalHeaderLabels([
            "Plan ID", "Type", "Department", "Auditor", "Start Date", "Status", "Risk Level", "Actions"
        ])
        plans_layout.addWidget(self.plans_table)
        
        plans_tab.setLayout(plans_layout)
        tabs.addTab(plans_tab, "Audit Plans")
        
        # Findings Tab
        findings_tab = QWidget()
        findings_layout = QVBoxLayout()
        
        # Findings Table
        self.findings_table = QTableWidget()
        self.findings_table.setColumnCount(7)
        self.findings_table.setHorizontalHeaderLabels([
            "Finding ID", "Audit ID", "Category", "Severity", "Description", "Status", "Due Date"
        ])
        findings_layout.addWidget(self.findings_table)
        
        findings_tab.setLayout(findings_layout)
        tabs.addTab(findings_tab, "Audit Findings")
        
        # Results Tab
        results_tab = QWidget()
        results_layout = QVBoxLayout()
        
        # Results Display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        results_layout.addWidget(self.results_display)
        
        results_tab.setLayout(results_layout)
        tabs.addTab(results_tab, "Audit Results")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def add_audit_plan(self, plan_data: Dict):
        self.audit_plans.append(plan_data)
        self.refresh_plans_table()
    
    def refresh_plans_table(self):
        self.plans_table.setRowCount(len(self.audit_plans))
        
        for row, plan in enumerate(self.audit_plans):
            self.plans_table.setItem(row, 0, QTableWidgetItem(plan['plan_id']))
            self.plans_table.setItem(row, 1, QTableWidgetItem(plan['audit_type']))
            self.plans_table.setItem(row, 2, QTableWidgetItem(plan['department']))
            self.plans_table.setItem(row, 3, QTableWidgetItem(plan['auditor']))
            self.plans_table.setItem(row, 4, QTableWidgetItem(plan['start_date']))
            self.plans_table.setItem(row, 5, QTableWidgetItem(plan['status']))
            self.plans_table.setItem(row, 6, QTableWidgetItem(plan['risk_level']))
            
            # Action button
            if plan['status'] == 'Planned':
                start_btn = QPushButton("Start Audit")
                start_btn.clicked.connect(lambda checked, pid=plan['plan_id']: self.start_audit(pid))
                self.plans_table.setCellWidget(row, 7, start_btn)
    
    def start_audit(self, plan_id: str):
        # Update plan status
        for plan in self.audit_plans:
            if plan['plan_id'] == plan_id:
                plan['status'] = 'In Progress'
                break
        
        self.refresh_plans_table()
        self.audit_started.emit(plan_id)
    
    def add_finding(self, finding_data: Dict):
        self.findings.append(finding_data)
        self.refresh_findings_table()
    
    def refresh_findings_table(self):
        self.findings_table.setRowCount(len(self.findings))
        
        for row, finding in enumerate(self.findings):
            self.findings_table.setItem(row, 0, QTableWidgetItem(finding['finding_id']))
            self.findings_table.setItem(row, 1, QTableWidgetItem(finding['audit_id']))
            self.findings_table.setItem(row, 2, QTableWidgetItem(finding['category']))
            self.findings_table.setItem(row, 3, QTableWidgetItem(finding['severity']))
            self.findings_table.setItem(row, 4, QTableWidgetItem(finding['description'][:50] + "..."))
            self.findings_table.setItem(row, 5, QTableWidgetItem(finding['status']))
            self.findings_table.setItem(row, 6, QTableWidgetItem(finding['due_date'][:10]))
    
    def update_audit_result(self, audit_id: str, result: Dict):
        self.audit_results[audit_id] = result
        
        # Update plan status
        for plan in self.audit_plans:
            if plan['plan_id'] == audit_id:
                plan['status'] = 'Completed'
                break
        
        self.refresh_plans_table()
        self.update_results_display()
    
    def update_results_display(self):
        results_text = "<h3>Audit Results Summary</h3>"
        
        for audit_id, result in self.audit_results.items():
            results_text += f"""
            <h4>Audit ID: {audit_id}</h4>
            <p><strong>Status:</strong> {result['status']}</p>
            <p><strong>Completion Date:</strong> {result['completion_date'][:10]}</p>
            <p><strong>Total Findings:</strong> {result['findings_count']}</p>
            <p><strong>High Risk:</strong> {result['high_risk_findings']}</p>
            <p><strong>Medium Risk:</strong> {result['medium_risk_findings']}</p>
            <p><strong>Low Risk:</strong> {result['low_risk_findings']}</p>
            <hr>
            """
        
        self.results_display.setHtml(results_text)

class InternalAuditSystem(QMainWindow):
    def __init__(self, database=None):
        super().__init__()
        self.database = database
        self.audit_threads = {}
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        self.setWindowTitle("Internal Audit Automation System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Audit Planning
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        left_panel.setMaximumWidth(400)
        
        left_layout = QVBoxLayout()
        
        # System title
        title = QLabel("Internal Audit Automation")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        
        # Statistics
        stats_group = QGroupBox("System Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_html = """
        <div style='font-family: Arial; font-size: 12px;'>
            <p><strong>Active Audits:</strong> <span style='color: #2196F3;'>0</span></p>
            <p><strong>Completed Audits:</strong> <span style='color: #4CAF50;'>0</span></p>
            <p><strong>Open Findings:</strong> <span style='color: #FF9800;'>0</span></p>
            <p><strong>High Risk Findings:</strong> <span style='color: #F44336;'>0</span></p>
            <p><strong>System Uptime:</strong> <span style='color: #9C27B0;'>100%</span></p>
        </div>
        """
        
        self.stats_label = QLabel(self.stats_html)
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        # Audit Plan Form
        self.audit_plan_window = AuditPlanWindow()
        self.audit_plan_window.audit_submitted.connect(self.handle_audit_submission)
        left_layout.addWidget(self.audit_plan_window)
        
        # Progress tracking
        progress_group = QGroupBox("Audit Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("No active audits")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        left_layout.addWidget(progress_group)
        
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)
        
        # Right panel - Dashboard
        self.auditor_dashboard = AuditorDashboard()
        self.auditor_dashboard.audit_started.connect(self.start_audit_execution)
        main_layout.addWidget(self.auditor_dashboard)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Internal Audit System Ready")
    
    def handle_audit_submission(self, plan_data: Dict):
        self.auditor_dashboard.add_audit_plan(plan_data)
        
        # Store in database if available
        if self.database:
            try:
                self.database.add_audit_plan(plan_data)
                self.statusBar().showMessage(f"Audit plan {plan_data['plan_id']} created and saved to database")
            except Exception as e:
                self.statusBar().showMessage(f"Error saving to database: {str(e)}")
        else:
            self.statusBar().showMessage(f"Audit plan {plan_data['plan_id']} created successfully")
    
    def start_audit_execution(self, plan_id: str):
        # Find the audit plan
        plan_data = None
        for plan in self.auditor_dashboard.audit_plans:
            if plan['plan_id'] == plan_id:
                plan_data = plan
                break
        
        if plan_data:
            # Create audit plan object
            audit_plan = AuditPlan(
                plan_id=plan_data['plan_id'],
                audit_type=plan_data['audit_type'],
                department=plan_data['department'],
                scope=plan_data['scope'],
                start_date=plan_data['start_date'],
                end_date=plan_data['end_date'],
                auditor=plan_data['auditor'],
                status=plan_data['status'],
                risk_level=plan_data['risk_level'],
                objectives=plan_data['objectives'],
                procedures=plan_data['procedures']
            )
            
            # Start audit processing thread
            audit_thread = AuditProcessingThread(audit_plan)
            audit_thread.progress_updated.connect(self.update_progress)
            audit_thread.audit_completed.connect(self.handle_audit_completion)
            audit_thread.finding_generated.connect(self.handle_finding_generated)
            
            self.audit_threads[plan_id] = audit_thread
            audit_thread.start()
            
            self.statusBar().showMessage(f"Audit {plan_id} execution started")
    
    def update_progress(self, phase: str, progress: int):
        self.progress_label.setText(f"Current Phase: {phase}")
        self.progress_bar.setValue(progress)
    
    def handle_audit_completion(self, audit_id: str, result: Dict):
        self.auditor_dashboard.update_audit_result(audit_id, result)
        self.progress_label.setText("Audit completed")
        self.progress_bar.setValue(100)
        
        # Update database if available
        if self.database:
            try:
                # Update audit plan status to 'Completed'
                self.database.update_audit_plan_status(audit_id, 'Completed')
                
                # Add audit execution steps if they exist in the result
                if 'execution_steps' in result:
                    for step in result['execution_steps']:
                        self.database.add_audit_execution_step(step)
            except Exception as e:
                self.statusBar().showMessage(f"Error updating database: {str(e)}")
        
        # Clean up thread
        if audit_id in self.audit_threads:
            del self.audit_threads[audit_id]
        
        self.statusBar().showMessage(f"Audit {audit_id} completed successfully")
    
    def handle_finding_generated(self, finding_data: Dict):
        self.auditor_dashboard.add_finding(finding_data)
        
        # Store in database if available
        if self.database:
            try:
                self.database.add_audit_finding(finding_data)
            except Exception as e:
                self.statusBar().showMessage(f"Error saving finding to database: {str(e)}")
    
    def refresh_data(self):
        # Update statistics
        if self.database:
            # Get statistics from database
            stats = self.database.get_audit_statistics()
            active_audits = stats.get('active_audits', 0)
            completed_audits = stats.get('completed_audits', 0)
            open_findings = stats.get('open_findings', 0)
            high_risk_findings = stats.get('high_risk_findings', 0)
        else:
            # Fallback to dashboard data if database is not available
            active_audits = len([p for p in self.auditor_dashboard.audit_plans if p['status'] == 'In Progress'])
            completed_audits = len([p for p in self.auditor_dashboard.audit_plans if p['status'] == 'Completed'])
            open_findings = len([f for f in self.auditor_dashboard.findings if f['status'] == 'Open'])
            high_risk_findings = len([f for f in self.auditor_dashboard.findings if f['severity'] == 'High'])
        
        self.stats_html = f"""
        <div style='font-family: Arial; font-size: 12px;'>
            <p><strong>Active Audits:</strong> <span style='color: #2196F3;'>{active_audits}</span></p>
            <p><strong>Completed Audits:</strong> <span style='color: #4CAF50;'>{completed_audits}</span></p>
            <p><strong>Open Findings:</strong> <span style='color: #FF9800;'>{open_findings}</span></p>
            <p><strong>High Risk Findings:</strong> <span style='color: #F44336;'>{high_risk_findings}</span></p>
            <p><strong>Last Updated:</strong> <span style='color: #9C27B0;'>{datetime.now().strftime('%H:%M:%S')}</span></p>
        </div>
        """
        
        self.stats_label.setText(self.stats_html)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = InternalAuditSystem()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()