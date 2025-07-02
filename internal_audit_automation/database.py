from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Dict, Optional
import json

Base = declarative_base()

class AuditPlan(Base):
    __tablename__ = 'audit_plans'
    
    id = Column(Integer, primary_key=True)
    plan_id = Column(String(50), unique=True, nullable=False)
    audit_type = Column(String(50), nullable=False)
    department = Column(String(100), nullable=False)
    scope = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    auditor = Column(String(100), nullable=False)
    status = Column(String(50), default='Planned')
    risk_level = Column(String(20))
    objectives = Column(Text)  # JSON string
    procedures = Column(Text)  # JSON string
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    findings = relationship("AuditFinding", back_populates="audit_plan")
    execution_steps = relationship("AuditExecutionStep", back_populates="audit_plan")
    risk_assessments = relationship("RiskAssessment", back_populates="audit_plan")

class AuditFinding(Base):
    __tablename__ = 'audit_findings'
    
    id = Column(Integer, primary_key=True)
    finding_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'), nullable=False)
    category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text)
    status = Column(String(50), default='Open')  # Open, In Progress, Resolved, Closed
    assigned_to = Column(String(100))
    due_date = Column(DateTime)
    resolution_date = Column(DateTime)
    resolution_notes = Column(Text)
    impact_assessment = Column(Text)
    root_cause = Column(Text)
    management_response = Column(Text)
    follow_up_required = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="findings")
    remediation_actions = relationship("RemediationAction", back_populates="finding")

class AuditExecutionStep(Base):
    __tablename__ = 'audit_execution_steps'
    
    id = Column(Integer, primary_key=True)
    step_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'), nullable=False)
    step_name = Column(String(200), nullable=False)
    step_type = Column(String(50))  # Planning, Risk Assessment, Control Testing, etc.
    description = Column(Text)
    status = Column(String(50), default='Pending')  # Pending, In Progress, Completed, Skipped
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration_hours = Column(Float)
    assigned_auditor = Column(String(100))
    completion_percentage = Column(Integer, default=0)
    notes = Column(Text)
    evidence_collected = Column(Text)  # JSON string
    test_results = Column(Text)  # JSON string
    ai_insights = Column(Text)  # JSON string
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="execution_steps")

class RiskAssessment(Base):
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'), nullable=False)
    risk_category = Column(String(100), nullable=False)
    risk_description = Column(Text, nullable=False)
    inherent_risk_rating = Column(String(20))  # Low, Medium, High, Critical
    control_effectiveness = Column(String(20))  # Effective, Partially Effective, Ineffective
    residual_risk_rating = Column(String(20))  # Low, Medium, High, Critical
    likelihood_score = Column(Integer)  # 1-10
    impact_score = Column(Integer)  # 1-10
    risk_score = Column(Integer)  # likelihood * impact
    mitigation_strategies = Column(Text)
    monitoring_procedures = Column(Text)
    risk_owner = Column(String(100))
    assessment_date = Column(DateTime, default=datetime.utcnow)
    next_review_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="risk_assessments")

class RemediationAction(Base):
    __tablename__ = 'remediation_actions'
    
    id = Column(Integer, primary_key=True)
    action_id = Column(String(50), unique=True, nullable=False)
    finding_id = Column(String(50), ForeignKey('audit_findings.finding_id'), nullable=False)
    action_description = Column(Text, nullable=False)
    action_type = Column(String(50))  # Corrective, Preventive, Detective
    priority = Column(String(20))  # Low, Medium, High, Critical
    assigned_to = Column(String(100), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(50), default='Planned')  # Planned, In Progress, Completed, Overdue
    completion_date = Column(DateTime)
    completion_notes = Column(Text)
    effectiveness_rating = Column(String(20))  # Effective, Partially Effective, Ineffective
    cost_estimate = Column(Float)
    actual_cost = Column(Float)
    resources_required = Column(Text)
    dependencies = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    finding = relationship("AuditFinding", back_populates="remediation_actions")

class ControlTesting(Base):
    __tablename__ = 'control_testing'
    
    id = Column(Integer, primary_key=True)
    test_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'), nullable=False)
    control_name = Column(String(200), nullable=False)
    control_type = Column(String(50))  # Preventive, Detective, Corrective
    control_frequency = Column(String(50))  # Daily, Weekly, Monthly, Quarterly, Annual
    test_objective = Column(Text)
    test_procedure = Column(Text)
    sample_size = Column(Integer)
    population_size = Column(Integer)
    test_method = Column(String(50))  # Inquiry, Observation, Inspection, Re-performance
    test_results = Column(Text)
    exceptions_found = Column(Integer, default=0)
    exception_details = Column(Text)
    control_effectiveness = Column(String(20))  # Effective, Partially Effective, Ineffective
    deficiency_level = Column(String(20))  # None, Minor, Significant, Material
    auditor_conclusion = Column(Text)
    test_date = Column(DateTime, default=datetime.utcnow)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditEvidence(Base):
    __tablename__ = 'audit_evidence'
    
    id = Column(Integer, primary_key=True)
    evidence_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'), nullable=False)
    evidence_type = Column(String(50))  # Document, Interview, Observation, Analysis
    evidence_source = Column(String(200))
    evidence_description = Column(Text, nullable=False)
    file_path = Column(String(500))  # Path to stored evidence file
    file_type = Column(String(50))  # PDF, Excel, Word, Image, etc.
    relevance_rating = Column(String(20))  # High, Medium, Low
    reliability_rating = Column(String(20))  # High, Medium, Low
    sufficiency_rating = Column(String(20))  # Sufficient, Insufficient
    collected_by = Column(String(100), nullable=False)
    collection_date = Column(DateTime, default=datetime.utcnow)
    review_status = Column(String(50), default='Pending')  # Pending, Reviewed, Approved
    reviewer = Column(String(100))
    review_date = Column(DateTime)
    review_notes = Column(Text)
    retention_period = Column(Integer)  # Days to retain evidence
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditReport(Base):
    __tablename__ = 'audit_reports'
    
    id = Column(Integer, primary_key=True)
    report_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'), nullable=False)
    report_type = Column(String(50))  # Draft, Final, Management Letter, Summary
    report_title = Column(String(200), nullable=False)
    executive_summary = Column(Text)
    audit_scope = Column(Text)
    methodology = Column(Text)
    key_findings = Column(Text)  # JSON string
    recommendations = Column(Text)  # JSON string
    management_responses = Column(Text)  # JSON string
    conclusion = Column(Text)
    overall_rating = Column(String(20))  # Satisfactory, Needs Improvement, Unsatisfactory
    report_status = Column(String(50), default='Draft')  # Draft, Under Review, Final, Distributed
    prepared_by = Column(String(100), nullable=False)
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))
    issue_date = Column(DateTime)
    distribution_list = Column(Text)  # JSON string
    follow_up_required = Column(Boolean, default=True)
    follow_up_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(50), unique=True, nullable=False)
    audit_plan_id = Column(String(50), ForeignKey('audit_plans.plan_id'))
    user_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))  # AuditPlan, Finding, Evidence, etc.
    entity_id = Column(String(50))
    old_values = Column(Text)  # JSON string
    new_values = Column(Text)  # JSON string
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self, db_path: str = "audit_system.db"):
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def close(self):
        self.session.close()
    
    # Audit Plan Methods
    def add_audit_plan(self, plan_data: Dict) -> bool:
        try:
            audit_plan = AuditPlan(
                plan_id=plan_data['plan_id'],
                audit_type=plan_data['audit_type'],
                department=plan_data['department'],
                scope=plan_data.get('scope', ''),
                start_date=datetime.fromisoformat(plan_data['start_date']) if isinstance(plan_data['start_date'], str) else plan_data['start_date'],
                end_date=datetime.fromisoformat(plan_data['end_date']) if isinstance(plan_data['end_date'], str) else plan_data['end_date'],
                auditor=plan_data['auditor'],
                status=plan_data.get('status', 'Planned'),
                risk_level=plan_data.get('risk_level', 'Medium'),
                objectives=json.dumps(plan_data.get('objectives', [])),
                procedures=json.dumps(plan_data.get('procedures', []))
            )
            
            self.session.add(audit_plan)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error adding audit plan: {e}")
            self.session.rollback()
            return False
    
    def get_audit_plan(self, plan_id: str) -> Optional[Dict]:
        try:
            plan = self.session.query(AuditPlan).filter_by(plan_id=plan_id).first()
            if plan:
                return {
                    'plan_id': plan.plan_id,
                    'audit_type': plan.audit_type,
                    'department': plan.department,
                    'scope': plan.scope,
                    'start_date': plan.start_date.isoformat() if plan.start_date else None,
                    'end_date': plan.end_date.isoformat() if plan.end_date else None,
                    'auditor': plan.auditor,
                    'status': plan.status,
                    'risk_level': plan.risk_level,
                    'objectives': json.loads(plan.objectives) if plan.objectives else [],
                    'procedures': json.loads(plan.procedures) if plan.procedures else [],
                    'created_date': plan.created_date.isoformat() if plan.created_date else None
                }
            return None
        except Exception as e:
            print(f"Error getting audit plan: {e}")
            return None
    
    def get_all_audit_plans(self) -> List[Dict]:
        try:
            plans = self.session.query(AuditPlan).all()
            return [{
                'plan_id': plan.plan_id,
                'audit_type': plan.audit_type,
                'department': plan.department,
                'scope': plan.scope,
                'start_date': plan.start_date.isoformat() if plan.start_date else None,
                'end_date': plan.end_date.isoformat() if plan.end_date else None,
                'auditor': plan.auditor,
                'status': plan.status,
                'risk_level': plan.risk_level,
                'objectives': json.loads(plan.objectives) if plan.objectives else [],
                'procedures': json.loads(plan.procedures) if plan.procedures else [],
                'created_date': plan.created_date.isoformat() if plan.created_date else None
            } for plan in plans]
        except Exception as e:
            print(f"Error getting audit plans: {e}")
            return []
    
    def update_audit_plan_status(self, plan_id: str, status: str) -> bool:
        try:
            plan = self.session.query(AuditPlan).filter_by(plan_id=plan_id).first()
            if plan:
                plan.status = status
                plan.updated_date = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating audit plan status: {e}")
            self.session.rollback()
            return False
    
    # Audit Finding Methods
    def add_audit_finding(self, finding_data: Dict) -> bool:
        try:
            finding = AuditFinding(
                finding_id=finding_data['finding_id'],
                audit_plan_id=finding_data['audit_id'],
                category=finding_data['category'],
                severity=finding_data['severity'],
                title=finding_data.get('title', finding_data['description'][:100]),
                description=finding_data['description'],
                recommendation=finding_data.get('recommendation', ''),
                status=finding_data.get('status', 'Open'),
                assigned_to=finding_data.get('assigned_to', ''),
                due_date=datetime.fromisoformat(finding_data['due_date']) if isinstance(finding_data['due_date'], str) else finding_data['due_date'],
                impact_assessment=finding_data.get('impact_assessment', ''),
                root_cause=finding_data.get('root_cause', ''),
                management_response=finding_data.get('management_response', ''),
                follow_up_required=finding_data.get('follow_up_required', True)
            )
            
            self.session.add(finding)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error adding audit finding: {e}")
            self.session.rollback()
            return False
    
    def get_audit_findings(self, audit_id: str = None) -> List[Dict]:
        try:
            query = self.session.query(AuditFinding)
            if audit_id:
                query = query.filter_by(audit_plan_id=audit_id)
            
            findings = query.all()
            return [{
                'finding_id': finding.finding_id,
                'audit_id': finding.audit_plan_id,
                'category': finding.category,
                'severity': finding.severity,
                'title': finding.title,
                'description': finding.description,
                'recommendation': finding.recommendation,
                'status': finding.status,
                'assigned_to': finding.assigned_to,
                'due_date': finding.due_date.isoformat() if finding.due_date else None,
                'resolution_date': finding.resolution_date.isoformat() if finding.resolution_date else None,
                'created_date': finding.created_date.isoformat() if finding.created_date else None
            } for finding in findings]
        except Exception as e:
            print(f"Error getting audit findings: {e}")
            return []
    
    def update_finding_status(self, finding_id: str, status: str, resolution_notes: str = None) -> bool:
        try:
            finding = self.session.query(AuditFinding).filter_by(finding_id=finding_id).first()
            if finding:
                finding.status = status
                if status in ['Resolved', 'Closed']:
                    finding.resolution_date = datetime.utcnow()
                if resolution_notes:
                    finding.resolution_notes = resolution_notes
                finding.updated_date = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating finding status: {e}")
            self.session.rollback()
            return False
    
    # Risk Assessment Methods
    def add_risk_assessment(self, assessment_data: Dict) -> bool:
        try:
            assessment = RiskAssessment(
                assessment_id=assessment_data['assessment_id'],
                audit_plan_id=assessment_data['audit_plan_id'],
                risk_category=assessment_data['risk_category'],
                risk_description=assessment_data['risk_description'],
                inherent_risk_rating=assessment_data.get('inherent_risk_rating', 'Medium'),
                control_effectiveness=assessment_data.get('control_effectiveness', 'Effective'),
                residual_risk_rating=assessment_data.get('residual_risk_rating', 'Medium'),
                likelihood_score=assessment_data.get('likelihood_score', 5),
                impact_score=assessment_data.get('impact_score', 5),
                risk_score=assessment_data.get('risk_score', 25),
                mitigation_strategies=assessment_data.get('mitigation_strategies', ''),
                monitoring_procedures=assessment_data.get('monitoring_procedures', ''),
                risk_owner=assessment_data.get('risk_owner', ''),
                next_review_date=datetime.fromisoformat(assessment_data['next_review_date']) if assessment_data.get('next_review_date') else None
            )
            
            self.session.add(assessment)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error adding risk assessment: {e}")
            self.session.rollback()
            return False
    
    def get_risk_assessments(self, audit_id: str = None) -> List[Dict]:
        try:
            query = self.session.query(RiskAssessment)
            if audit_id:
                query = query.filter_by(audit_plan_id=audit_id)
            
            assessments = query.all()
            return [{
                'assessment_id': assessment.assessment_id,
                'audit_plan_id': assessment.audit_plan_id,
                'risk_category': assessment.risk_category,
                'risk_description': assessment.risk_description,
                'inherent_risk_rating': assessment.inherent_risk_rating,
                'control_effectiveness': assessment.control_effectiveness,
                'residual_risk_rating': assessment.residual_risk_rating,
                'likelihood_score': assessment.likelihood_score,
                'impact_score': assessment.impact_score,
                'risk_score': assessment.risk_score,
                'risk_owner': assessment.risk_owner,
                'assessment_date': assessment.assessment_date.isoformat() if assessment.assessment_date else None
            } for assessment in assessments]
        except Exception as e:
            print(f"Error getting risk assessments: {e}")
            return []
    
    # Audit Evidence Methods
    def add_audit_evidence(self, evidence_data: Dict) -> bool:
        try:
            evidence = AuditEvidence(
                evidence_id=evidence_data['evidence_id'],
                audit_plan_id=evidence_data['audit_plan_id'],
                evidence_type=evidence_data['evidence_type'],
                evidence_source=evidence_data.get('evidence_source', ''),
                evidence_description=evidence_data['evidence_description'],
                file_path=evidence_data.get('file_path', ''),
                file_type=evidence_data.get('file_type', ''),
                relevance_rating=evidence_data.get('relevance_rating', 'Medium'),
                reliability_rating=evidence_data.get('reliability_rating', 'Medium'),
                sufficiency_rating=evidence_data.get('sufficiency_rating', 'Sufficient'),
                collected_by=evidence_data['collected_by'],
                retention_period=evidence_data.get('retention_period', 2555)  # 7 years default
            )
            
            self.session.add(evidence)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error adding audit evidence: {e}")
            self.session.rollback()
            return False
    
    # Statistics Methods
    def get_audit_statistics(self) -> Dict:
        try:
            total_audits = self.session.query(AuditPlan).count()
            active_audits = self.session.query(AuditPlan).filter_by(status='In Progress').count()
            completed_audits = self.session.query(AuditPlan).filter_by(status='Completed').count()
            planned_audits = self.session.query(AuditPlan).filter_by(status='Planned').count()
            
            total_findings = self.session.query(AuditFinding).count()
            open_findings = self.session.query(AuditFinding).filter_by(status='Open').count()
            high_risk_findings = self.session.query(AuditFinding).filter_by(severity='High').count()
            critical_findings = self.session.query(AuditFinding).filter_by(severity='Critical').count()
            
            # Risk distribution
            risk_distribution = {
                'Low': self.session.query(AuditPlan).filter_by(risk_level='Low').count(),
                'Medium': self.session.query(AuditPlan).filter_by(risk_level='Medium').count(),
                'High': self.session.query(AuditPlan).filter_by(risk_level='High').count()
            }
            
            # Department distribution
            departments = self.session.query(AuditPlan.department).distinct().all()
            department_stats = {}
            for dept in departments:
                dept_name = dept[0]
                dept_count = self.session.query(AuditPlan).filter_by(department=dept_name).count()
                department_stats[dept_name] = dept_count
            
            return {
                'total_audits': total_audits,
                'active_audits': active_audits,
                'completed_audits': completed_audits,
                'planned_audits': planned_audits,
                'total_findings': total_findings,
                'open_findings': open_findings,
                'high_risk_findings': high_risk_findings,
                'critical_findings': critical_findings,
                'risk_distribution': risk_distribution,
                'department_stats': department_stats
            }
        except Exception as e:
            print(f"Error getting audit statistics: {e}")
            return {}
    
    # Audit Log Methods
    def add_audit_log(self, log_data: Dict) -> bool:
        try:
            log_entry = AuditLog(
                log_id=log_data['log_id'],
                audit_plan_id=log_data.get('audit_plan_id'),
                user_id=log_data['user_id'],
                action=log_data['action'],
                entity_type=log_data.get('entity_type', ''),
                entity_id=log_data.get('entity_id', ''),
                old_values=json.dumps(log_data.get('old_values', {})),
                new_values=json.dumps(log_data.get('new_values', {})),
                ip_address=log_data.get('ip_address', ''),
                user_agent=log_data.get('user_agent', ''),
                session_id=log_data.get('session_id', '')
            )
            
            self.session.add(log_entry)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error adding audit log: {e}")
            self.session.rollback()
            return False
    
    def search_audit_plans(self, search_term: str) -> List[Dict]:
        try:
            plans = self.session.query(AuditPlan).filter(
                AuditPlan.department.contains(search_term) |
                AuditPlan.audit_type.contains(search_term) |
                AuditPlan.auditor.contains(search_term) |
                AuditPlan.scope.contains(search_term)
            ).all()
            
            return [{
                'plan_id': plan.plan_id,
                'audit_type': plan.audit_type,
                'department': plan.department,
                'auditor': plan.auditor,
                'status': plan.status,
                'risk_level': plan.risk_level,
                'start_date': plan.start_date.isoformat() if plan.start_date else None
            } for plan in plans]
        except Exception as e:
            print(f"Error searching audit plans: {e}")
            return []
    
    def cleanup_old_data(self, days_old: int = 2555) -> bool:
        """Clean up old audit data (default 7 years)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old completed audits
            old_audits = self.session.query(AuditPlan).filter(
                AuditPlan.status == 'Completed',
                AuditPlan.updated_date < cutoff_date
            ).all()
            
            for audit in old_audits:
                # Delete related findings
                self.session.query(AuditFinding).filter_by(audit_plan_id=audit.plan_id).delete()
                # Delete related evidence
                self.session.query(AuditEvidence).filter_by(audit_plan_id=audit.plan_id).delete()
                # Delete the audit plan
                self.session.delete(audit)
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            self.session.rollback()
            return False