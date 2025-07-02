# credit_scoring.py

import requests
import json
import time
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CreditScoring:
    """AI-powered credit scoring system for loan applications"""
    
    def __init__(self, api_base="http://localhost:11434/api/generate", model="llama3.2:1b"):
        """Initialize the credit scoring system"""
        self.api_base = api_base
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Credit scoring weights for different factors
        self.scoring_weights = {
            'credit_score': 0.35,      # 35% weight
            'debt_to_income': 0.25,    # 25% weight
            'employment_stability': 0.20,  # 20% weight
            'income_adequacy': 0.15,   # 15% weight
            'loan_to_income': 0.05     # 5% weight
        }
        
        logger.info(f"CreditScoring initialized with model: {self.model}")
    
    def evaluate_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a loan application using AI-powered analysis"""
        logger.info(f"Starting credit evaluation for application: {application_data.get('reference', 'N/A')}")
        
        # First, perform basic calculations
        financial_metrics = self._calculate_financial_metrics(application_data)
        
        # Create comprehensive prompt for AI analysis
        prompt = self._create_evaluation_prompt(application_data, financial_metrics)
        logger.debug(f"Generated evaluation prompt: {prompt[:500]}...")  # Log first 500 chars
        
        # Try AI evaluation first
        ai_result = self._get_ai_evaluation(prompt)
        
        if ai_result and ai_result.get('success', False):
            logger.info("AI evaluation successful")
            # Combine AI insights with calculated metrics
            final_result = self._combine_ai_and_metrics(ai_result, financial_metrics, application_data)
        else:
            logger.warning("AI evaluation failed, falling back to rule-based scoring")
            # Fallback to rule-based evaluation
            final_result = self._rule_based_evaluation(application_data, financial_metrics)
        
        # Add additional metadata
        final_result.update({
            'evaluation_timestamp': datetime.now().isoformat(),
            'evaluation_method': 'ai_powered' if ai_result and ai_result.get('success') else 'rule_based',
            'financial_metrics': financial_metrics
        })
        
        logger.info(f"Credit evaluation completed with status: {final_result.get('status', 'unknown')}")
        return final_result
    
    def _calculate_financial_metrics(self, application_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key financial metrics for the application"""
        try:
            # Extract financial data
            annual_income = float(application_data.get('annual_income', 0))
            loan_amount = float(application_data.get('loan_amount', 0))
            existing_debt = float(application_data.get('existing_debt', 0))
            loan_term = int(application_data.get('loan_term', 60))
            credit_score = int(application_data.get('credit_score', 0))
            employment_years = int(application_data.get('employment_years', 0))
            
            # Calculate monthly values
            monthly_income = annual_income / 12
            monthly_existing_debt = existing_debt / 12
            
            # Estimate monthly loan payment (simple calculation)
            # Using a basic formula: P = L[c(1 + c)^n]/[(1 + c)^n - 1]
            # Where P = monthly payment, L = loan amount, c = monthly interest rate, n = number of payments
            estimated_interest_rate = self._estimate_interest_rate(credit_score) / 100 / 12
            if estimated_interest_rate > 0:
                monthly_payment = loan_amount * (estimated_interest_rate * (1 + estimated_interest_rate)**loan_term) / ((1 + estimated_interest_rate)**loan_term - 1)
            else:
                monthly_payment = loan_amount / loan_term
            
            # Calculate ratios
            total_monthly_debt = monthly_existing_debt + monthly_payment
            debt_to_income_ratio = (total_monthly_debt / monthly_income * 100) if monthly_income > 0 else 999
            loan_to_income_ratio = (loan_amount / annual_income * 100) if annual_income > 0 else 999
            
            metrics = {
                'monthly_income': monthly_income,
                'monthly_existing_debt': monthly_existing_debt,
                'estimated_monthly_payment': monthly_payment,
                'total_monthly_debt': total_monthly_debt,
                'debt_to_income_ratio': debt_to_income_ratio,
                'loan_to_income_ratio': loan_to_income_ratio,
                'estimated_interest_rate': self._estimate_interest_rate(credit_score),
                'employment_stability_score': self._calculate_employment_score(employment_years, application_data.get('employment_status', ''))
            }
            
            logger.debug(f"Calculated financial metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {str(e)}")
            return {}
    
    def _estimate_interest_rate(self, credit_score: int) -> float:
        """Estimate interest rate based on credit score"""
        if credit_score >= 750:
            return 3.5 + random.uniform(0, 1.0)  # 3.5-4.5%
        elif credit_score >= 700:
            return 4.5 + random.uniform(0, 1.5)  # 4.5-6.0%
        elif credit_score >= 650:
            return 6.0 + random.uniform(0, 2.0)  # 6.0-8.0%
        elif credit_score >= 600:
            return 8.0 + random.uniform(0, 3.0)  # 8.0-11.0%
        else:
            return 11.0 + random.uniform(0, 4.0)  # 11.0-15.0%
    
    def _calculate_employment_score(self, employment_years: int, employment_status: str) -> float:
        """Calculate employment stability score"""
        base_score = 0
        
        # Years of employment
        if employment_years >= 5:
            base_score += 40
        elif employment_years >= 3:
            base_score += 30
        elif employment_years >= 2:
            base_score += 20
        elif employment_years >= 1:
            base_score += 10
        
        # Employment type
        if employment_status == "Full-time":
            base_score += 30
        elif employment_status == "Part-time":
            base_score += 15
        elif employment_status == "Self-employed":
            base_score += 20
        elif employment_status == "Unemployed":
            base_score -= 50
        
        return min(100, max(0, base_score))
    
    def _create_evaluation_prompt(self, application_data: Dict[str, Any], financial_metrics: Dict[str, float]) -> str:
        """Create a comprehensive prompt for AI evaluation"""
        prompt = f"""You are an expert credit analyst at a major bank. Analyze this loan application and provide a detailed assessment.

APPLICANT INFORMATION:
- Name: {application_data.get('applicant_name', 'N/A')}
- Annual Income: ${application_data.get('annual_income', 0):,.2f}
- Employment: {application_data.get('employment_status', 'N/A')} at {application_data.get('employer', 'N/A')}
- Employment Duration: {application_data.get('employment_years', 0)} years
- Credit Score: {application_data.get('credit_score', 0)}

LOAN REQUEST:
- Amount: ${application_data.get('loan_amount', 0):,.2f}
- Purpose: {application_data.get('loan_purpose', 'N/A')}
- Term: {application_data.get('loan_term', 0)} months
- Existing Debt: ${application_data.get('existing_debt', 0):,.2f}

CALCULATED METRICS:
- Monthly Income: ${financial_metrics.get('monthly_income', 0):,.2f}
- Estimated Monthly Payment: ${financial_metrics.get('estimated_monthly_payment', 0):,.2f}
- Debt-to-Income Ratio: {financial_metrics.get('debt_to_income_ratio', 0):.1f}%
- Loan-to-Income Ratio: {financial_metrics.get('loan_to_income_ratio', 0):.1f}%
- Employment Stability Score: {financial_metrics.get('employment_stability_score', 0):.1f}/100

ANALYSIS REQUIREMENTS:
1. Assess creditworthiness based on the 5 C's of credit (Character, Capacity, Capital, Collateral, Conditions)
2. Evaluate risk factors and strengths
3. Consider loan purpose appropriateness
4. Analyze debt-to-income ratio (ideal <36%, acceptable <43%, risky >43%)
5. Assess employment stability and income reliability
6. Provide specific recommendations

Respond ONLY with a JSON object containing your analysis:

{{
    "approved": true/false,
    "status": "APPROVED"/"CONDITIONAL_APPROVAL"/"REJECTED",
    "risk_level": "low"/"medium"/"high",
    "confidence_score": 0-100,
    "recommended_interest_rate": 0.0,
    "recommended_loan_amount": 0.0,
    "conditions": ["list of conditions if conditional approval"],
    "risk_factors": ["list of identified risk factors"],
    "strengths": ["list of applicant strengths"],
    "reason": "detailed explanation of decision",
    "recommendations": ["list of recommendations for applicant"]
}}

Do not include any text outside the JSON object."""
        
        return prompt
    
    def _get_ai_evaluation(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get AI evaluation from the language model"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to call AI evaluation API")
                
                response = requests.post(
                    self.api_base,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=60  # Increased timeout for complex analysis
                )
                
                logger.debug(f"AI API Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    parsed_result = self._parse_ai_response(result['response'])
                    
                    if parsed_result:
                        parsed_result['success'] = True
                        return parsed_result
                    else:
                        logger.warning(f"Failed to parse AI response (attempt {attempt + 1})")
                else:
                    logger.error(f"AI API error (attempt {attempt + 1}): {response.status_code}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"AI API request error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error in AI evaluation (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error("All AI evaluation attempts failed")
        return None
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse the AI response JSON"""
        try:
            logger.debug(f"Parsing AI response: {response_text[:500]}...")  # Log first 500 chars
            
            # Clean up the response text
            json_str = response_text.strip()
            if not json_str.startswith('{'):
                json_str = json_str[json_str.find('{'):]
            if not json_str.endswith('}'):
                json_str = json_str[:json_str.rfind('}')+1]
            
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['approved', 'status', 'risk_level', 'reason']
            if not all(field in result for field in required_fields):
                logger.error(f"Missing required fields in AI response. Required: {required_fields}, Got: {list(result.keys())}")
                return None
            
            # Validate field values
            if result['status'] not in ['APPROVED', 'CONDITIONAL_APPROVAL', 'REJECTED']:
                result['status'] = 'REJECTED'  # Default to rejected if invalid
            
            if result['risk_level'] not in ['low', 'medium', 'high']:
                result['risk_level'] = 'high'  # Default to high risk if invalid
            
            # Ensure confidence score is within range
            if 'confidence_score' in result:
                result['confidence_score'] = max(0, min(100, result.get('confidence_score', 0)))
            
            logger.debug(f"Successfully parsed AI response: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}\nResponse text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}\nResponse text: {response_text}")
            return None
    
    def _combine_ai_and_metrics(self, ai_result: Dict[str, Any], financial_metrics: Dict[str, float], application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine AI insights with calculated financial metrics"""
        try:
            # Start with AI result
            combined_result = ai_result.copy()
            
            # Add calculated metrics
            combined_result.update({
                'debt_to_income_ratio': financial_metrics.get('debt_to_income_ratio', 0),
                'loan_to_income_ratio': financial_metrics.get('loan_to_income_ratio', 0),
                'employment_stability_score': financial_metrics.get('employment_stability_score', 0),
                'estimated_monthly_payment': financial_metrics.get('estimated_monthly_payment', 0)
            })
            
            # Use AI recommended interest rate or fall back to calculated
            if 'recommended_interest_rate' not in combined_result or combined_result['recommended_interest_rate'] <= 0:
                combined_result['recommended_interest_rate'] = financial_metrics.get('estimated_interest_rate', 0)
            
            # Use AI recommended loan amount or original amount
            if 'recommended_loan_amount' not in combined_result or combined_result['recommended_loan_amount'] <= 0:
                combined_result['recommended_loan_amount'] = float(application_data.get('loan_amount', 0))
            
            # Ensure boolean fields are properly set
            combined_result['approved'] = bool(combined_result.get('approved', False))
            
            # Add risk assessment details
            if not combined_result.get('risk_factors'):
                combined_result['risk_factors'] = self._identify_risk_factors(application_data, financial_metrics)
            
            if not combined_result.get('strengths'):
                combined_result['strengths'] = self._identify_strengths(application_data, financial_metrics)
            
            logger.debug(f"Combined AI and metrics result: {combined_result}")
            return combined_result
            
        except Exception as e:
            logger.error(f"Error combining AI and metrics: {str(e)}")
            # Fallback to rule-based evaluation
            return self._rule_based_evaluation(application_data, financial_metrics)
    
    def _rule_based_evaluation(self, application_data: Dict[str, Any], financial_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Fallback rule-based credit evaluation"""
        try:
            logger.info("Performing rule-based credit evaluation")
            
            # Extract key data
            credit_score = int(application_data.get('credit_score', 0))
            debt_to_income = financial_metrics.get('debt_to_income_ratio', 999)
            employment_score = financial_metrics.get('employment_stability_score', 0)
            annual_income = float(application_data.get('annual_income', 0))
            loan_amount = float(application_data.get('loan_amount', 0))
            
            # Calculate overall score
            total_score = 0
            max_score = 100
            
            # Credit score component (35%)
            if credit_score >= 750:
                credit_component = 35
            elif credit_score >= 700:
                credit_component = 28
            elif credit_score >= 650:
                credit_component = 21
            elif credit_score >= 600:
                credit_component = 14
            else:
                credit_component = 7
            
            total_score += credit_component
            
            # Debt-to-income component (25%)
            if debt_to_income <= 30:
                dti_component = 25
            elif debt_to_income <= 36:
                dti_component = 20
            elif debt_to_income <= 43:
                dti_component = 15
            elif debt_to_income <= 50:
                dti_component = 10
            else:
                dti_component = 0
            
            total_score += dti_component
            
            # Employment stability component (20%)
            employment_component = (employment_score / 100) * 20
            total_score += employment_component
            
            # Income adequacy component (15%)
            if annual_income >= 100000:
                income_component = 15
            elif annual_income >= 75000:
                income_component = 12
            elif annual_income >= 50000:
                income_component = 9
            elif annual_income >= 30000:
                income_component = 6
            else:
                income_component = 3
            
            total_score += income_component
            
            # Loan-to-income component (5%)
            loan_to_income = financial_metrics.get('loan_to_income_ratio', 999)
            if loan_to_income <= 200:  # 2x annual income
                lti_component = 5
            elif loan_to_income <= 300:  # 3x annual income
                lti_component = 3
            elif loan_to_income <= 500:  # 5x annual income
                lti_component = 1
            else:
                lti_component = 0
            
            total_score += lti_component
            
            # Determine approval status
            if total_score >= 80:
                status = "APPROVED"
                risk_level = "low"
                approved = True
            elif total_score >= 65:
                status = "CONDITIONAL_APPROVAL"
                risk_level = "medium"
                approved = True
            else:
                status = "REJECTED"
                risk_level = "high"
                approved = False
            
            # Generate conditions for conditional approval
            conditions = []
            if status == "CONDITIONAL_APPROVAL":
                if debt_to_income > 36:
                    conditions.append("Reduce existing debt to improve debt-to-income ratio")
                if employment_score < 50:
                    conditions.append("Provide additional employment verification")
                if credit_score < 700:
                    conditions.append("Consider a co-signer or additional collateral")
            
            # Identify risk factors and strengths
            risk_factors = self._identify_risk_factors(application_data, financial_metrics)
            strengths = self._identify_strengths(application_data, financial_metrics)
            
            # Generate reason
            reason = f"Rule-based evaluation score: {total_score:.1f}/100. "
            if approved:
                reason += f"Application meets lending criteria with {risk_level} risk profile."
            else:
                reason += "Application does not meet minimum lending criteria."
            
            # Generate recommendations
            recommendations = self._generate_recommendations(application_data, financial_metrics, approved)
            
            result = {
                'approved': approved,
                'status': status,
                'risk_level': risk_level,
                'confidence_score': min(95, total_score + 10),  # Slightly boost confidence for rule-based
                'recommended_interest_rate': financial_metrics.get('estimated_interest_rate', 0),
                'recommended_loan_amount': loan_amount if approved else 0,
                'conditions': conditions,
                'risk_factors': risk_factors,
                'strengths': strengths,
                'reason': reason,
                'recommendations': recommendations,
                'total_score': total_score,
                'score_breakdown': {
                    'credit_score_component': credit_component,
                    'debt_to_income_component': dti_component,
                    'employment_component': employment_component,
                    'income_component': income_component,
                    'loan_to_income_component': lti_component
                }
            }
            
            logger.info(f"Rule-based evaluation completed with score: {total_score:.1f}/100, status: {status}")
            return result
            
        except Exception as e:
            logger.error(f"Error in rule-based evaluation: {str(e)}")
            return {
                'approved': False,
                'status': "ERROR",
                'risk_level': "high",
                'reason': f"Error in evaluation process: {str(e)}",
                'confidence_score': 0
            }
    
    def _identify_risk_factors(self, application_data: Dict[str, Any], financial_metrics: Dict[str, float]) -> List[str]:
        """Identify risk factors in the application"""
        risk_factors = []
        
        credit_score = int(application_data.get('credit_score', 0))
        debt_to_income = financial_metrics.get('debt_to_income_ratio', 0)
        employment_years = int(application_data.get('employment_years', 0))
        annual_income = float(application_data.get('annual_income', 0))
        employment_status = application_data.get('employment_status', '')
        
        if credit_score < 650:
            risk_factors.append(f"Below-average credit score: {credit_score}")
        
        if debt_to_income > 43:
            risk_factors.append(f"High debt-to-income ratio: {debt_to_income:.1f}%")
        
        if employment_years < 2:
            risk_factors.append(f"Limited employment history: {employment_years} years")
        
        if annual_income < 30000:
            risk_factors.append(f"Low annual income: ${annual_income:,.2f}")
        
        if employment_status in ["Part-time", "Unemployed"]:
            risk_factors.append(f"Unstable employment status: {employment_status}")
        
        return risk_factors
    
    def _identify_strengths(self, application_data: Dict[str, Any], financial_metrics: Dict[str, float]) -> List[str]:
        """Identify strengths in the application"""
        strengths = []
        
        credit_score = int(application_data.get('credit_score', 0))
        debt_to_income = financial_metrics.get('debt_to_income_ratio', 999)
        employment_years = int(application_data.get('employment_years', 0))
        annual_income = float(application_data.get('annual_income', 0))
        employment_status = application_data.get('employment_status', '')
        
        if credit_score >= 750:
            strengths.append(f"Excellent credit score: {credit_score}")
        elif credit_score >= 700:
            strengths.append(f"Good credit score: {credit_score}")
        
        if debt_to_income <= 30:
            strengths.append(f"Low debt-to-income ratio: {debt_to_income:.1f}%")
        elif debt_to_income <= 36:
            strengths.append(f"Acceptable debt-to-income ratio: {debt_to_income:.1f}%")
        
        if employment_years >= 5:
            strengths.append(f"Stable employment history: {employment_years} years")
        
        if annual_income >= 75000:
            strengths.append(f"Strong annual income: ${annual_income:,.2f}")
        
        if employment_status == "Full-time":
            strengths.append("Stable full-time employment")
        
        return strengths
    
    def _generate_recommendations(self, application_data: Dict[str, Any], financial_metrics: Dict[str, float], approved: bool) -> List[str]:
        """Generate recommendations for the applicant"""
        recommendations = []
        
        if not approved:
            credit_score = int(application_data.get('credit_score', 0))
            debt_to_income = financial_metrics.get('debt_to_income_ratio', 0)
            employment_years = int(application_data.get('employment_years', 0))
            
            if credit_score < 650:
                recommendations.append("Work on improving credit score by paying bills on time and reducing credit utilization")
            
            if debt_to_income > 43:
                recommendations.append("Reduce existing debt to improve debt-to-income ratio before reapplying")
            
            if employment_years < 2:
                recommendations.append("Consider waiting until you have more stable employment history")
            
            recommendations.append("Consider applying for a smaller loan amount")
            recommendations.append("Explore options for a co-signer or additional collateral")
        else:
            recommendations.append("Maintain good credit habits to keep favorable loan terms")
            recommendations.append("Consider setting up automatic payments to ensure timely loan payments")
            if financial_metrics.get('debt_to_income_ratio', 0) > 30:
                recommendations.append("Monitor your debt-to-income ratio and avoid taking on additional debt")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Test the credit scoring system
    scoring_system = CreditScoring()
    
    # Test application data
    test_application = {
        'reference': 'LOAN-TEST-001',
        'applicant_name': 'John Doe',
        'annual_income': 75000.0,
        'employment_status': 'Full-time',
        'employer': 'Tech Corp',
        'employment_years': 5,
        'loan_amount': 25000.0,
        'loan_purpose': 'Home improvement',
        'loan_term': 60,
        'existing_debt': 15000.0,
        'credit_score': 720
    }
    
    try:
        # Evaluate the application
        result = scoring_system.evaluate_application(test_application)
        
        print("Credit Scoring Result:")
        print(f"Approved: {result.get('approved', False)}")
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Risk Level: {result.get('risk_level', 'Unknown')}")
        print(f"Confidence: {result.get('confidence_score', 0)}%")
        print(f"Recommended Interest Rate: {result.get('recommended_interest_rate', 0):.2f}%")
        print(f"Reason: {result.get('reason', 'No reason provided')}")
        
        if result.get('risk_factors'):
            print(f"Risk Factors: {', '.join(result['risk_factors'])}")
        
        if result.get('strengths'):
            print(f"Strengths: {', '.join(result['strengths'])}")
        
        if result.get('recommendations'):
            print(f"Recommendations: {', '.join(result['recommendations'])}")
        
    except Exception as e:
        print(f"Test error: {e}")
    
    print("Credit scoring test completed")