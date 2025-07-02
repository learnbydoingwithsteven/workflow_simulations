# document_processor.py

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Document processing and verification for trade finance"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate"):
        """Initialize document processor"""
        self.ollama_url = ollama_url
        self.supported_documents = {
            'commercial_invoice': 'Commercial Invoice',
            'bill_of_lading': 'Bill of Lading',
            'packing_list': 'Packing List',
            'certificate_of_origin': 'Certificate of Origin',
            'insurance_certificate': 'Insurance Certificate',
            'inspection_certificate': 'Inspection Certificate',
            'letter_of_credit': 'Letter of Credit',
            'bank_guarantee': 'Bank Guarantee',
            'export_license': 'Export License',
            'import_permit': 'Import Permit'
        }
        
        logger.info("Document processor initialized")
    
    def verify_documents_ai(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered document verification"""
        try:
            # Prepare document verification prompt
            prompt = self._create_document_verification_prompt(application_data)
            
            # Call Ollama API
            response = requests.post(
                self.ollama_url,
                json={
                    'model': 'llama3.2',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.2,
                        'top_p': 0.9
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                ai_response = response.json().get('response', '')
                
                # Parse AI response
                parsed_result = self._parse_ai_verification_response(ai_response)
                
                if parsed_result.get('success'):
                    logger.info("AI document verification completed successfully")
                    return {
                        'success': True,
                        'score': parsed_result.get('verification_score', 0),
                        'document_status': parsed_result.get('document_status', {}),
                        'issues': parsed_result.get('issues', []),
                        'recommendations': parsed_result.get('recommendations', []),
                        'confidence': parsed_result.get('confidence', 0),
                        'method': 'ai_powered',
                        'processing_time': parsed_result.get('processing_time', 0),
                        'raw_response': ai_response
                    }
                else:
                    logger.warning("AI document verification failed to parse response")
                    return {'success': False, 'error': 'Failed to parse AI response'}
            else:
                logger.warning(f"AI document verification failed: HTTP {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"AI document verification request failed: {str(e)}")
            return {'success': False, 'error': f"Request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"AI document verification error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_documents_rules(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based document verification"""
        try:
            start_time = time.time()
            
            verification_score = 0
            document_status = {}
            issues = []
            recommendations = []
            
            # Required documents based on trade type
            required_docs = self._get_required_documents(application_data.get('trade_type', ''))
            
            # Simulate document verification for each required document
            for doc_type in required_docs:
                doc_result = self._verify_single_document(doc_type, application_data)
                document_status[doc_type] = doc_result
                
                if doc_result['status'] == 'verified':
                    verification_score += doc_result['score']
                elif doc_result['status'] == 'missing':
                    issues.append(f"{self.supported_documents.get(doc_type, doc_type)} is missing")
                    recommendations.append(f"Please provide {self.supported_documents.get(doc_type, doc_type)}")
                elif doc_result['status'] == 'invalid':
                    issues.append(f"{self.supported_documents.get(doc_type, doc_type)} has validation issues")
                    recommendations.append(f"Please review and resubmit {self.supported_documents.get(doc_type, doc_type)}")
            
            # Calculate average score
            if required_docs:
                verification_score = verification_score / len(required_docs)
            
            # Additional checks
            additional_checks = self._perform_additional_checks(application_data)
            verification_score = (verification_score + additional_checks['score']) / 2
            
            if additional_checks['issues']:
                issues.extend(additional_checks['issues'])
            if additional_checks['recommendations']:
                recommendations.extend(additional_checks['recommendations'])
            
            processing_time = time.time() - start_time
            
            logger.info(f"Rule-based document verification completed in {processing_time:.2f}s")
            
            return {
                'success': True,
                'score': round(verification_score, 2),
                'document_status': document_status,
                'issues': issues,
                'recommendations': recommendations,
                'method': 'rule_based',
                'processing_time': round(processing_time, 2),
                'required_documents': required_docs
            }
            
        except Exception as e:
            logger.error(f"Rule-based document verification error: {str(e)}")
            return {
                'success': False,
                'score': 0,
                'error': str(e),
                'method': 'error_fallback'
            }
    
    def _create_document_verification_prompt(self, application_data: Dict[str, Any]) -> str:
        """Create prompt for AI document verification"""
        trade_type = application_data.get('trade_type', 'Unknown')
        company_name = application_data.get('company_name', 'Unknown')
        counterparty = application_data.get('counterparty_name', 'Unknown')
        amount = application_data.get('finance_amount', 0)
        country = application_data.get('counterparty_country', 'Unknown')
        
        prompt = f"""
Analyze this trade finance application for document verification:

Trade Details:
- Type: {trade_type}
- Company: {company_name}
- Counterparty: {counterparty}
- Amount: ${amount:,.2f}
- Country: {country}
- Payment Terms: {application_data.get('payment_terms', 'Unknown')}

Required Documents Analysis:
For {trade_type}, verify the completeness and validity of trade finance documents.

Evaluate:
1. Document completeness (all required documents present)
2. Document validity (proper format, signatures, dates)
3. Document consistency (information matches across documents)
4. Regulatory compliance (meets international trade standards)
5. Risk indicators (unusual patterns, discrepancies)

Provide verification results:
1. Overall verification score (0-100)
2. Status for each document type
3. Issues found
4. Recommendations for improvement
5. Confidence level in verification

Respond in JSON format:
{{
    "verification_score": <score>,
    "document_status": {{
        "commercial_invoice": {{"status": "verified/missing/invalid", "score": <score>, "notes": "<notes>"}},
        "bill_of_lading": {{"status": "verified/missing/invalid", "score": <score>, "notes": "<notes>"}},
        "packing_list": {{"status": "verified/missing/invalid", "score": <score>, "notes": "<notes>"}}
    }},
    "issues": ["<issue1>", "<issue2>"],
    "recommendations": ["<rec1>", "<rec2>"],
    "confidence": <confidence_score>,
    "processing_time": <time_in_seconds>
}}
"""
        
        return prompt
    
    def _parse_ai_verification_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI verification response"""
        try:
            # Extract JSON from response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['verification_score', 'document_status']
                if all(field in result for field in required_fields):
                    return {
                        'success': True,
                        **result
                    }
                else:
                    missing_fields = [f for f in required_fields if f not in result]
                    return {
                        'success': False,
                        'error': f"Missing required fields: {missing_fields}"
                    }
            else:
                return {
                    'success': False,
                    'error': "No valid JSON found in AI response"
                }
                
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"JSON parsing error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Response parsing error: {str(e)}"
            }
    
    def _get_required_documents(self, trade_type: str) -> List[str]:
        """Get required documents based on trade type"""
        trade_type_lower = trade_type.lower()
        
        base_documents = ['commercial_invoice', 'packing_list']
        
        if 'letter of credit' in trade_type_lower:
            return base_documents + ['letter_of_credit', 'bill_of_lading', 'certificate_of_origin', 'insurance_certificate']
        elif 'documentary collection' in trade_type_lower:
            return base_documents + ['bill_of_lading', 'certificate_of_origin']
        elif 'export financing' in trade_type_lower:
            return base_documents + ['export_license', 'bill_of_lading', 'insurance_certificate']
        elif 'import financing' in trade_type_lower:
            return base_documents + ['import_permit', 'bill_of_lading']
        elif 'trade loan' in trade_type_lower:
            return base_documents + ['bank_guarantee', 'certificate_of_origin']
        elif 'supply chain finance' in trade_type_lower:
            return base_documents + ['inspection_certificate']
        else:
            return base_documents + ['bill_of_lading']
    
    def _verify_single_document(self, doc_type: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a single document (simulated)"""
        try:
            # Simulate document verification with random results
            # In a real system, this would involve actual document analysis
            
            # Probability of document being present and valid
            presence_probability = 0.85  # 85% chance document is present
            validity_probability = 0.90  # 90% chance valid if present
            
            is_present = random.random() < presence_probability
            
            if not is_present:
                return {
                    'status': 'missing',
                    'score': 0,
                    'notes': f"{self.supported_documents.get(doc_type, doc_type)} not provided"
                }
            
            is_valid = random.random() < validity_probability
            
            if not is_valid:
                issues = random.choice([
                    "Invalid signature",
                    "Expired document",
                    "Incorrect format",
                    "Missing required fields",
                    "Inconsistent information"
                ])
                return {
                    'status': 'invalid',
                    'score': random.uniform(20, 50),
                    'notes': f"{self.supported_documents.get(doc_type, doc_type)}: {issues}"
                }
            
            # Document is valid
            score = random.uniform(80, 100)
            quality_notes = random.choice([
                "All required fields present",
                "Valid signatures and dates",
                "Meets regulatory standards",
                "Consistent with other documents",
                "High quality documentation"
            ])
            
            return {
                'status': 'verified',
                'score': score,
                'notes': f"{self.supported_documents.get(doc_type, doc_type)}: {quality_notes}"
            }
            
        except Exception as e:
            logger.error(f"Error verifying document {doc_type}: {str(e)}")
            return {
                'status': 'error',
                'score': 0,
                'notes': f"Verification error: {str(e)}"
            }
    
    def _perform_additional_checks(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform additional document consistency checks"""
        try:
            score = 0
            issues = []
            recommendations = []
            
            # Check 1: Amount consistency
            finance_amount = application_data.get('finance_amount', 0)
            if finance_amount > 0:
                # Simulate amount verification across documents
                amount_consistent = random.random() > 0.1  # 90% consistency rate
                if amount_consistent:
                    score += 25
                else:
                    issues.append("Amount discrepancy found across documents")
                    recommendations.append("Verify amounts in all financial documents")
            
            # Check 2: Date consistency
            date_consistent = random.random() > 0.15  # 85% consistency rate
            if date_consistent:
                score += 25
            else:
                issues.append("Date inconsistencies found")
                recommendations.append("Ensure all document dates are logical and consistent")
            
            # Check 3: Party name consistency
            party_consistent = random.random() > 0.05  # 95% consistency rate
            if party_consistent:
                score += 25
            else:
                issues.append("Party name variations found across documents")
                recommendations.append("Standardize party names across all documents")
            
            # Check 4: Product/commodity consistency
            product_consistent = random.random() > 0.1  # 90% consistency rate
            if product_consistent:
                score += 25
            else:
                issues.append("Product description inconsistencies")
                recommendations.append("Align product descriptions across all documents")
            
            return {
                'score': score,
                'issues': issues,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error in additional checks: {str(e)}")
            return {
                'score': 0,
                'issues': [f"Additional check error: {str(e)}"],
                'recommendations': ["Manual review required due to system error"]
            }
    
    def extract_document_data(self, document_type: str, document_content: str) -> Dict[str, Any]:
        """Extract structured data from document content"""
        try:
            # This would typically use OCR and NLP to extract data
            # For simulation, we'll return mock extracted data
            
            extracted_data = {
                'document_type': document_type,
                'extraction_timestamp': datetime.now().isoformat(),
                'confidence': random.uniform(0.8, 0.98),
                'extracted_fields': {}
            }
            
            if document_type == 'commercial_invoice':
                extracted_data['extracted_fields'] = {
                    'invoice_number': f"INV-{random.randint(10000, 99999)}",
                    'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                    'total_amount': random.uniform(10000, 1000000),
                    'currency': 'USD',
                    'seller': 'ABC Trading Company',
                    'buyer': 'XYZ Import Corp'
                }
            elif document_type == 'bill_of_lading':
                extracted_data['extracted_fields'] = {
                    'bl_number': f"BL-{random.randint(100000, 999999)}",
                    'vessel_name': f"MV {random.choice(['Atlantic', 'Pacific', 'Global', 'Ocean'])} {random.choice(['Star', 'Pioneer', 'Express', 'Trader'])}",
                    'port_of_loading': random.choice(['Shanghai', 'Rotterdam', 'Los Angeles', 'Hamburg']),
                    'port_of_discharge': random.choice(['New York', 'Long Beach', 'Felixstowe', 'Singapore']),
                    'shipping_date': datetime.now().strftime('%Y-%m-%d')
                }
            elif document_type == 'letter_of_credit':
                extracted_data['extracted_fields'] = {
                    'lc_number': f"LC-{random.randint(1000000, 9999999)}",
                    'issuing_bank': random.choice(['Chase Bank', 'HSBC', 'Citibank', 'Bank of America']),
                    'amount': random.uniform(50000, 5000000),
                    'expiry_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
                    'beneficiary': 'Export Trading LLC'
                }
            
            logger.info(f"Document data extracted for {document_type}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting document data: {str(e)}")
            return {
                'document_type': document_type,
                'extraction_timestamp': datetime.now().isoformat(),
                'error': str(e),
                'confidence': 0.0
            }
    
    def validate_document_signatures(self, document_type: str, signature_data: bytes) -> Dict[str, Any]:
        """Validate digital signatures on documents"""
        try:
            # Simulate signature validation
            # In a real system, this would use cryptographic signature verification
            
            validation_result = {
                'document_type': document_type,
                'validation_timestamp': datetime.now().isoformat(),
                'signature_valid': random.random() > 0.05,  # 95% valid rate
                'certificate_valid': random.random() > 0.02,  # 98% valid rate
                'trust_chain_valid': random.random() > 0.03,  # 97% valid rate
            }
            
            # Overall validity
            validation_result['overall_valid'] = (
                validation_result['signature_valid'] and
                validation_result['certificate_valid'] and
                validation_result['trust_chain_valid']
            )
            
            if not validation_result['overall_valid']:
                issues = []
                if not validation_result['signature_valid']:
                    issues.append("Invalid digital signature")
                if not validation_result['certificate_valid']:
                    issues.append("Invalid certificate")
                if not validation_result['trust_chain_valid']:
                    issues.append("Broken trust chain")
                
                validation_result['issues'] = issues
            
            logger.info(f"Signature validation completed for {document_type}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating signatures: {str(e)}")
            return {
                'document_type': document_type,
                'validation_timestamp': datetime.now().isoformat(),
                'error': str(e),
                'overall_valid': False
            }
    
    def check_document_compliance(self, document_type: str, country_code: str) -> Dict[str, Any]:
        """Check document compliance with country-specific regulations"""
        try:
            # Simulate compliance checking
            compliance_result = {
                'document_type': document_type,
                'country_code': country_code,
                'check_timestamp': datetime.now().isoformat(),
                'compliance_checks': []
            }
            
            # Common compliance checks
            checks = [
                {'name': 'Format Compliance', 'status': random.choice(['pass', 'pass', 'pass', 'fail'])},
                {'name': 'Required Fields', 'status': random.choice(['pass', 'pass', 'pass', 'fail'])},
                {'name': 'Regulatory Standards', 'status': random.choice(['pass', 'pass', 'fail'])},
                {'name': 'International Trade Rules', 'status': random.choice(['pass', 'pass', 'pass', 'fail'])}
            ]
            
            compliance_result['compliance_checks'] = checks
            
            # Overall compliance
            failed_checks = [check for check in checks if check['status'] == 'fail']
            compliance_result['overall_compliant'] = len(failed_checks) == 0
            compliance_result['compliance_score'] = (len(checks) - len(failed_checks)) / len(checks) * 100
            
            if failed_checks:
                compliance_result['failed_checks'] = [check['name'] for check in failed_checks]
            
            logger.info(f"Compliance check completed for {document_type} in {country_code}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error checking compliance: {str(e)}")
            return {
                'document_type': document_type,
                'country_code': country_code,
                'check_timestamp': datetime.now().isoformat(),
                'error': str(e),
                'overall_compliant': False,
                'compliance_score': 0
            }
    
    def generate_verification_report(self, application_id: str, verification_results: Dict[str, Any]) -> str:
        """Generate a comprehensive verification report"""
        try:
            report_lines = [
                "TRADE FINANCE DOCUMENT VERIFICATION REPORT",
                "=" * 50,
                f"Application ID: {application_id}",
                f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "VERIFICATION SUMMARY",
                "-" * 20,
                f"Overall Score: {verification_results.get('score', 0):.1f}/100",
                f"Verification Method: {verification_results.get('method', 'Unknown')}",
                f"Processing Time: {verification_results.get('processing_time', 0):.2f} seconds",
                ""
            ]
            
            # Document status
            if 'document_status' in verification_results:
                report_lines.extend([
                    "DOCUMENT STATUS",
                    "-" * 15
                ])
                
                for doc_type, status in verification_results['document_status'].items():
                    doc_name = self.supported_documents.get(doc_type, doc_type)
                    report_lines.append(f"{doc_name}: {status.get('status', 'Unknown').upper()}")
                    if 'score' in status:
                        report_lines.append(f"  Score: {status['score']:.1f}/100")
                    if 'notes' in status:
                        report_lines.append(f"  Notes: {status['notes']}")
                    report_lines.append("")
            
            # Issues
            if verification_results.get('issues'):
                report_lines.extend([
                    "ISSUES IDENTIFIED",
                    "-" * 17
                ])
                for i, issue in enumerate(verification_results['issues'], 1):
                    report_lines.append(f"{i}. {issue}")
                report_lines.append("")
            
            # Recommendations
            if verification_results.get('recommendations'):
                report_lines.extend([
                    "RECOMMENDATIONS",
                    "-" * 15
                ])
                for i, rec in enumerate(verification_results['recommendations'], 1):
                    report_lines.append(f"{i}. {rec}")
                report_lines.append("")
            
            # Confidence
            if 'confidence' in verification_results:
                report_lines.extend([
                    "CONFIDENCE METRICS",
                    "-" * 18,
                    f"Verification Confidence: {verification_results['confidence']:.1f}%",
                    ""
                ])
            
            report_lines.extend([
                "END OF REPORT",
                "=" * 50
            ])
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Error generating verification report: {str(e)}")
            return f"Error generating report: {str(e)}"
    
    def get_document_requirements(self, trade_type: str, country: str) -> Dict[str, Any]:
        """Get document requirements for specific trade type and country"""
        try:
            required_docs = self._get_required_documents(trade_type)
            
            requirements = {
                'trade_type': trade_type,
                'country': country,
                'required_documents': [],
                'optional_documents': [],
                'country_specific_requirements': []
            }
            
            # Add document details
            for doc_type in required_docs:
                doc_info = {
                    'type': doc_type,
                    'name': self.supported_documents.get(doc_type, doc_type),
                    'mandatory': True,
                    'description': self._get_document_description(doc_type)
                }
                requirements['required_documents'].append(doc_info)
            
            # Add optional documents
            optional_docs = ['inspection_certificate', 'insurance_certificate']
            for doc_type in optional_docs:
                if doc_type not in required_docs:
                    doc_info = {
                        'type': doc_type,
                        'name': self.supported_documents.get(doc_type, doc_type),
                        'mandatory': False,
                        'description': self._get_document_description(doc_type)
                    }
                    requirements['optional_documents'].append(doc_info)
            
            # Add country-specific requirements
            country_reqs = self._get_country_specific_requirements(country)
            requirements['country_specific_requirements'] = country_reqs
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error getting document requirements: {str(e)}")
            return {
                'trade_type': trade_type,
                'country': country,
                'error': str(e),
                'required_documents': [],
                'optional_documents': [],
                'country_specific_requirements': []
            }
    
    def _get_document_description(self, doc_type: str) -> str:
        """Get description for document type"""
        descriptions = {
            'commercial_invoice': 'Document showing the transaction between buyer and seller',
            'bill_of_lading': 'Receipt for goods shipped and contract for their delivery',
            'packing_list': 'Detailed list of goods in each package',
            'certificate_of_origin': 'Document certifying the country of origin of goods',
            'insurance_certificate': 'Proof of insurance coverage for the shipment',
            'inspection_certificate': 'Document certifying goods meet specified standards',
            'letter_of_credit': 'Bank guarantee of payment upon meeting conditions',
            'bank_guarantee': 'Bank promise to pay if conditions are not met',
            'export_license': 'Government permission to export specific goods',
            'import_permit': 'Government permission to import specific goods'
        }
        return descriptions.get(doc_type, 'Trade finance document')
    
    def _get_country_specific_requirements(self, country: str) -> List[str]:
        """Get country-specific document requirements"""
        country_lower = country.lower()
        
        if 'united states' in country_lower or 'usa' in country_lower:
            return [
                "AES (Automated Export System) filing required for exports over $2,500",
                "OFAC sanctions screening required",
                "Anti-dumping duty documentation if applicable"
            ]
        elif 'china' in country_lower:
            return [
                "China Compulsory Certification (CCC) for applicable products",
                "SAFE (State Administration of Foreign Exchange) registration",
                "Customs declaration in Chinese language"
            ]
        elif 'european union' in country_lower or any(eu_country in country_lower for eu_country in ['germany', 'france', 'italy', 'spain']):
            return [
                "CE marking for applicable products",
                "EORI (Economic Operators Registration and Identification) number",
                "EUR.1 or EUR-MED certificate for preferential treatment"
            ]
        else:
            return [
                "Standard customs declaration",
                "Country-specific import/export permits if required",
                "Local language translation of key documents may be required"
            ]

# Example usage and testing
if __name__ == "__main__":
    # Test the document processor
    processor = DocumentProcessor()
    
    # Test application data
    test_application = {
        'application_id': 'TF20240101001',
        'company_name': 'Global Trade Corp',
        'trade_type': 'Letter of Credit',
        'finance_amount': 500000,
        'counterparty_name': 'International Imports Ltd',
        'counterparty_country': 'Germany',
        'payment_terms': '90 days'
    }
    
    try:
        # Test rule-based verification
        print("Testing rule-based document verification...")
        rule_results = processor.verify_documents_rules(test_application)
        print(f"Rule-based verification score: {rule_results.get('score', 0)}")
        
        # Test document requirements
        print("\nTesting document requirements...")
        requirements = processor.get_document_requirements('Letter of Credit', 'Germany')
        print(f"Required documents: {len(requirements.get('required_documents', []))}")
        
        # Test verification report
        print("\nGenerating verification report...")
        report = processor.generate_verification_report('TF20240101001', rule_results)
        print("Report generated successfully")
        
        print("\nDocument processor test completed")
        
    except Exception as e:
        print(f"Document processor test error: {e}")