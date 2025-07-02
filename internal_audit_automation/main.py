#!/usr/bin/env python3
"""
Internal Audit Automation System - Main Entry Point

This module serves as the main entry point for the Internal Audit Automation System.
It initializes the database, sets up the GUI application, and handles application lifecycle.

Features:
- Database initialization and migration
- GUI application startup
- Error handling and logging
- Configuration management
- System health checks

Author: AI Assistant
Date: 2024
"""

import sys
import os
import logging
import traceback
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from audit_automation import InternalAuditSystem
    from database import Database
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are in the same directory.")
    sys.exit(1)

class AuditSystemLauncher:
    """Main launcher class for the Internal Audit Automation System"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.database = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"audit_system_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Internal Audit Automation System starting...")
    
    def create_splash_screen(self):
        """Create and show splash screen"""
        # Create a simple splash screen
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(QColor(45, 52, 54))
        
        painter = QPainter(splash_pixmap)
        painter.setPen(QColor(255, 255, 255))
        
        # Title
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(50, 100, "Internal Audit Automation")
        
        # Subtitle
        subtitle_font = QFont("Arial", 12)
        painter.setFont(subtitle_font)
        painter.drawText(50, 130, "Professional Audit Management System")
        
        # Version
        version_font = QFont("Arial", 10)
        painter.setFont(version_font)
        painter.drawText(50, 200, "Version 1.0.0")
        painter.drawText(50, 220, "Loading...")
        
        painter.end()
        
        splash = QSplashScreen(splash_pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        splash.show()
        
        return splash
    
    def initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            self.logger.info("Initializing database...")
            
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Initialize database
            db_path = data_dir / "audit_system.db"
            self.database = Database(str(db_path))
            
            # Test database connection
            stats = self.database.get_audit_statistics()
            self.logger.info(f"Database initialized successfully. Current stats: {stats}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def create_sample_data(self):
        """Create sample data for demonstration purposes"""
        try:
            # Check if we already have data
            stats = self.database.get_audit_statistics()
            if stats.get('total_audits', 0) > 0:
                self.logger.info("Sample data already exists, skipping creation.")
                return True
            
            self.logger.info("Creating sample data...")
            
            # Sample audit plans
            sample_plans = [
                {
                    'plan_id': 'AUD-2024-001',
                    'audit_type': 'Financial Audit',
                    'department': 'Finance',
                    'scope': 'Review of financial controls and procedures',
                    'start_date': '2024-01-15',
                    'end_date': '2024-02-15',
                    'auditor': 'John Smith',
                    'status': 'Completed',
                    'risk_level': 'High',
                    'objectives': ['Assess financial controls', 'Review compliance', 'Identify risks'],
                    'procedures': ['Document review', 'Control testing', 'Substantive testing']
                },
                {
                    'plan_id': 'AUD-2024-002',
                    'audit_type': 'IT Audit',
                    'department': 'Information Technology',
                    'scope': 'Cybersecurity and data protection assessment',
                    'start_date': '2024-02-01',
                    'end_date': '2024-03-01',
                    'auditor': 'Sarah Johnson',
                    'status': 'In Progress',
                    'risk_level': 'High',
                    'objectives': ['Assess IT security', 'Review access controls', 'Evaluate data protection'],
                    'procedures': ['Security testing', 'Access review', 'Policy assessment']
                },
                {
                    'plan_id': 'AUD-2024-003',
                    'audit_type': 'Operational Audit',
                    'department': 'Operations',
                    'scope': 'Process efficiency and effectiveness review',
                    'start_date': '2024-03-01',
                    'end_date': '2024-04-01',
                    'auditor': 'Michael Brown',
                    'status': 'Planned',
                    'risk_level': 'Medium',
                    'objectives': ['Review operational processes', 'Assess efficiency', 'Identify improvements'],
                    'procedures': ['Process mapping', 'Performance analysis', 'Best practice review']
                },
                {
                    'plan_id': 'AUD-2024-004',
                    'audit_type': 'Compliance Audit',
                    'department': 'Human Resources',
                    'scope': 'HR policies and regulatory compliance',
                    'start_date': '2024-04-01',
                    'end_date': '2024-05-01',
                    'auditor': 'Emily Davis',
                    'status': 'Planned',
                    'risk_level': 'Medium',
                    'objectives': ['Review HR policies', 'Assess compliance', 'Evaluate training programs'],
                    'procedures': ['Policy review', 'Compliance testing', 'Training assessment']
                }
            ]
            
            # Add sample audit plans
            for plan in sample_plans:
                self.database.add_audit_plan(plan)
            
            # Sample findings for completed audit
            sample_findings = [
                {
                    'finding_id': 'FIND-2024-001',
                    'audit_id': 'AUD-2024-001',
                    'category': 'Internal Controls',
                    'severity': 'High',
                    'description': 'Segregation of duties not properly implemented in accounts payable process',
                    'recommendation': 'Implement proper segregation of duties with approval workflows',
                    'status': 'Open',
                    'due_date': '2024-03-15',
                    'assigned_to': 'Finance Manager'
                },
                {
                    'finding_id': 'FIND-2024-002',
                    'audit_id': 'AUD-2024-001',
                    'category': 'Documentation',
                    'severity': 'Medium',
                    'description': 'Financial procedures documentation is outdated',
                    'recommendation': 'Update all financial procedure documents to reflect current practices',
                    'status': 'In Progress',
                    'due_date': '2024-04-01',
                    'assigned_to': 'Finance Team Lead'
                },
                {
                    'finding_id': 'FIND-2024-003',
                    'audit_id': 'AUD-2024-002',
                    'category': 'Access Controls',
                    'severity': 'Critical',
                    'description': 'Privileged access accounts not regularly reviewed',
                    'recommendation': 'Implement quarterly privileged access review process',
                    'status': 'Open',
                    'due_date': '2024-03-01',
                    'assigned_to': 'IT Security Manager'
                }
            ]
            
            # Add sample findings
            for finding in sample_findings:
                self.database.add_audit_finding(finding)
            
            # Sample risk assessments
            sample_risks = [
                {
                    'assessment_id': 'RISK-2024-001',
                    'audit_plan_id': 'AUD-2024-001',
                    'risk_category': 'Financial Risk',
                    'risk_description': 'Risk of financial misstatement due to weak controls',
                    'inherent_risk_rating': 'High',
                    'control_effectiveness': 'Partially Effective',
                    'residual_risk_rating': 'Medium',
                    'likelihood_score': 7,
                    'impact_score': 8,
                    'risk_score': 56,
                    'risk_owner': 'CFO',
                    'next_review_date': '2024-06-01'
                },
                {
                    'assessment_id': 'RISK-2024-002',
                    'audit_plan_id': 'AUD-2024-002',
                    'risk_category': 'Cybersecurity Risk',
                    'risk_description': 'Risk of data breach due to inadequate access controls',
                    'inherent_risk_rating': 'Critical',
                    'control_effectiveness': 'Ineffective',
                    'residual_risk_rating': 'High',
                    'likelihood_score': 8,
                    'impact_score': 9,
                    'risk_score': 72,
                    'risk_owner': 'CTO',
                    'next_review_date': '2024-05-01'
                }
            ]
            
            # Add sample risk assessments
            for risk in sample_risks:
                self.database.add_risk_assessment(risk)
            
            self.logger.info("Sample data created successfully.")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sample data: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def show_error_dialog(self, title, message):
        """Show error dialog to user"""
        if self.app:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
    
    def run(self):
        """Main application entry point"""
        try:
            # Create QApplication
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Internal Audit Automation System")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Audit Solutions")
            
            # Show splash screen
            splash = self.create_splash_screen()
            self.app.processEvents()
            
            # Initialize database
            splash.showMessage("Initializing database...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor(255, 255, 255))
            self.app.processEvents()
            
            if not self.initialize_database():
                splash.close()
                self.show_error_dialog(
                    "Database Error",
                    "Failed to initialize database. Please check the logs for more information."
                )
                return 1
            
            # Create sample data
            splash.showMessage("Setting up sample data...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor(255, 255, 255))
            self.app.processEvents()
            
            self.create_sample_data()
            
            # Initialize main window
            splash.showMessage("Loading application...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor(255, 255, 255))
            self.app.processEvents()
            
            self.main_window = InternalAuditSystem(self.database)
            
            # Close splash screen and show main window
            splash.finish(self.main_window)
            self.main_window.show()
            
            self.logger.info("Application started successfully.")
            
            # Run the application
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Application startup failed: {e}")
            self.logger.error(traceback.format_exc())
            
            if hasattr(self, 'app') and self.app:
                self.show_error_dialog(
                    "Startup Error",
                    f"Failed to start the application:\n{str(e)}\n\nPlease check the logs for more information."
                )
            else:
                print(f"Critical error: {e}")
                print("Please check the logs for more information.")
            
            return 1
        
        finally:
            # Cleanup
            if self.database:
                try:
                    self.database.close()
                    self.logger.info("Database connection closed.")
                except Exception as e:
                    self.logger.error(f"Error closing database: {e}")
            
            self.logger.info("Application shutdown complete.")

def main():
    """Main function"""
    launcher = AuditSystemLauncher()
    return launcher.run()

if __name__ == "__main__":
    sys.exit(main())