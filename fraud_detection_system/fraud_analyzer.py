# fraud_analyzer.py

import requests
import json
import time
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FraudAnalyzer:
    """AI-powered fraud detection and analysis system"""
    
    def __init__(self, api_base="http://localhost:11434/api/generate", model="llama3.2:1b"):
        """Initialize the fraud analyzer"""
        self.api_base = api_base
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        # Fraud detection rules and weights
        self.fraud_rules = {
            'amount_threshold': {
                'high_amount': 5000,      # Transactions above this are high risk
                'very_high_amount': 10000, # Transactions above this are very high risk
                'weight': 25
            },
            'location_risk': {
                'foreign_countries': ['London, UK', 'Paris, France', 'Tokyo, Japan', 'Sydney, Australia'],
                'high_risk_locations': ['Unknown Location', 'Foreign Location'],
                'weight': 20
            },
            'time_patterns': {
                'unusual_hours': [(23, 6)],  # 11 PM to 6 AM
                'weight': 10
            },
            'merchant_risk': {
                'high_risk_categories': ['wire_transfer', 'luxury', 'electronics'],
                'medium_risk_categories': ['online', 'atm'],
                'weight': 15
            },
            'velocity_checks': {
                'max_transactions_per_hour': 5,
                'max_amount_per_hour': 2000,
                'weight': 20
            },
            'customer_behavior': {
                'account_age_threshold': 30,  # days
                'weight': 10
            }
        }
        
        # Known fraud patterns
        self.fraud_patterns = [
            {
                'name': 'card_testing',
                'description': 'Multiple small transactions in short time',
                'indicators': ['multiple_small_amounts', 'short_time_window'],
                'risk_score': 80
            },
            {
                'name': 'account_takeover',
                'description': 'Unusual location with high-value transaction',
                'indicators': ['foreign_location', 'high_amount', 'unusual_merchant'],
                'risk_score': 90
            },
            {
                'name': 'synthetic_identity',
                'description': 'New account with immediate high-value transactions',
                'indicators': ['new_account', 'high_amount', 'limited_history'],
                'risk_score': 85
            },
            {
                'name': 'money_laundering',
                'description': 'Structured transactions just below reporting thresholds',
                'indicators': ['structured_amounts', 'frequent_transfers', 'round_amounts'],
                'risk_score': 95
            }
        ]
        
        logger.info(f"FraudAnalyzer initialized with model: {self.model}")
    
    def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a transaction for fraud indicators"""
        logger.info(f"Starting fraud analysis for transaction: {transaction.get('transaction_id', 'N/A')}")
        
        # Perform rule-based analysis first
        rule_based_result = self._rule_based_analysis(transaction)
        
        # Create comprehensive prompt for AI analysis
        prompt = self._create_fraud_analysis_prompt(transaction, rule_based_result)
        logger.debug(f"Generated fraud analysis prompt: {prompt[:500]}...")  # Log first 500 chars
        
        # Try AI analysis
        ai_result = self._get_ai_analysis(prompt)
        
        if ai_result and ai_result.get('success', False):
            logger.info("AI fraud analysis successful")
            # Combine AI insights with rule-based analysis
            final_result = self._combine_ai_and_rules(ai_result, rule_based_result, transaction)
        else:
            logger.warning("AI fraud analysis failed, using rule-based analysis only")
            # Use rule-based analysis only
            final_result = rule_based_result
            final_result['analysis_method'] = 'rule_based'
        
        # Add metadata
        final_result.update({
            'analysis_timestamp': datetime.now().isoformat(),
            'analyzer_version': '1.0'
        })
        
        logger.info(f"Fraud analysis completed - Score: {final_result.get('fraud_score', 0):.1f}, Risk: {final_result.get('risk_level', 'unknown')}")
        return final_result
    
    def _rule_based_analysis(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Perform rule-based fraud analysis"""
        try:
            logger.debug("Performing rule-based fraud analysis")
            
            fraud_score = 0
            fraud_indicators = []
            risk_factors = []
            
            # Extract transaction data
            amount = float(transaction.get('amount', 0))
            location = transaction.get('location', '')
            merchant_category = transaction.get('merchant_category', '')
            transaction_type = transaction.get('transaction_type', '')
            timestamp_str = transaction.get('timestamp', '')
            customer_id = transaction.get('customer_id', '')
            
            # Parse timestamp
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.now()
            except:
                timestamp = datetime.now()
            
            # 1. Amount-based checks
            amount_score = self._analyze_amount(amount, fraud_indicators, risk_factors)
            fraud_score += amount_score
            
            # 2. Location-based checks
            location_score = self._analyze_location(location, fraud_indicators, risk_factors)
            fraud_score += location_score
            
            # 3. Time-based checks
            time_score = self._analyze_time_patterns(timestamp, fraud_indicators, risk_factors)
            fraud_score += time_score
            
            # 4. Merchant category checks
            merchant_score = self._analyze_merchant_category(merchant_category, fraud_indicators, risk_factors)
            fraud_score += merchant_score
            
            # 5. Transaction type checks
            type_score = self._analyze_transaction_type(transaction_type, amount, fraud_indicators, risk_factors)
            fraud_score += type_score
            
            # 6. Velocity checks (simplified - would need transaction history in real system)
            velocity_score = self._analyze_velocity_patterns(transaction, fraud_indicators, risk_factors)
            fraud_score += velocity_score
            
            # 7. Pattern matching
            pattern_score = self._analyze_fraud_patterns(transaction, fraud_indicators, risk_factors)
            fraud_score += pattern_score
            
            # Determine risk level and fraud status
            if fraud_score >= 80:
                risk_level = 'high'
                is_fraud = True
            elif fraud_score >= 50:
                risk_level = 'medium'
                is_fraud = True
            elif fraud_score >= 30:
                risk_level = 'low'
                is_fraud = False
            else:
                risk_level = 'very_low'
                is_fraud = False
            
            # Generate explanation
            explanation = self._generate_rule_explanation(fraud_score, fraud_indicators, risk_factors)
            
            result = {
                'fraud_score': min(100, fraud_score),
                'risk_level': risk_level,
                'is_fraud': is_fraud,
                'fraud_indicators': fraud_indicators,
                'risk_factors': risk_factors,
                'explanation': explanation,
                'confidence': min(95, fraud_score + 10),  # Rule-based confidence
                'analysis_method': 'rule_based',
                'score_breakdown': {
                    'amount_score': amount_score,
                    'location_score': location_score,
                    'time_score': time_score,
                    'merchant_score': merchant_score,
                    'type_score': type_score,
                    'velocity_score': velocity_score,
                    'pattern_score': pattern_score
                }
            }
            
            logger.debug(f"Rule-based analysis result: Score={fraud_score:.1f}, Risk={risk_level}")
            return result
            
        except Exception as e:
            logger.error(f"Error in rule-based analysis: {str(e)}")
            return {
                'fraud_score': 50,  # Default medium risk
                'risk_level': 'medium',
                'is_fraud': True,
                'fraud_indicators': ['analysis_error'],
                'explanation': f"Error in fraud analysis: {str(e)}",
                'confidence': 0,
                'analysis_method': 'error'
            }
    
    def _analyze_amount(self, amount: float, indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze transaction amount for fraud indicators"""
        score = 0
        rules = self.fraud_rules['amount_threshold']
        
        if amount >= rules['very_high_amount']:
            score += rules['weight']
            indicators.append('very_high_amount')
            risk_factors.append(f"Very high transaction amount: ${amount:,.2f}")
        elif amount >= rules['high_amount']:
            score += rules['weight'] * 0.7
            indicators.append('high_amount')
            risk_factors.append(f"High transaction amount: ${amount:,.2f}")
        
        # Check for round amounts (potential structuring)
        if amount % 1000 == 0 and amount >= 1000:
            score += 5
            indicators.append('round_amount')
            risk_factors.append(f"Round amount transaction: ${amount:,.2f}")
        
        # Check for amounts just below reporting thresholds
        if 9000 <= amount < 10000:
            score += 15
            indicators.append('structured_amount')
            risk_factors.append(f"Amount just below reporting threshold: ${amount:,.2f}")
        
        return score
    
    def _analyze_location(self, location: str, indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze transaction location for fraud indicators"""
        score = 0
        rules = self.fraud_rules['location_risk']
        
        # Check for foreign locations
        for foreign_location in rules['foreign_countries']:
            if foreign_location.lower() in location.lower():
                score += rules['weight']
                indicators.append('foreign_location')
                risk_factors.append(f"Transaction in foreign location: {location}")
                break
        
        # Check for high-risk locations
        for high_risk in rules['high_risk_locations']:
            if high_risk.lower() in location.lower():
                score += rules['weight'] * 0.8
                indicators.append('high_risk_location')
                risk_factors.append(f"Transaction in high-risk location: {location}")
                break
        
        # Check for unknown or suspicious location patterns
        if not location or location.lower() in ['unknown', 'n/a', '']:
            score += 10
            indicators.append('unknown_location')
            risk_factors.append("Transaction location unknown")
        
        return score
    
    def _analyze_time_patterns(self, timestamp: datetime, indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze transaction timing for fraud indicators"""
        score = 0
        rules = self.fraud_rules['time_patterns']
        
        hour = timestamp.hour
        
        # Check for unusual hours
        for start_hour, end_hour in rules['unusual_hours']:
            if start_hour > end_hour:  # Overnight period
                if hour >= start_hour or hour <= end_hour:
                    score += rules['weight']
                    indicators.append('unusual_hours')
                    risk_factors.append(f"Transaction at unusual hour: {hour:02d}:00")
                    break
            else:
                if start_hour <= hour <= end_hour:
                    score += rules['weight']
                    indicators.append('unusual_hours')
                    risk_factors.append(f"Transaction at unusual hour: {hour:02d}:00")
                    break
        
        # Check for weekend transactions (higher risk for business accounts)
        if timestamp.weekday() >= 5:  # Saturday = 5, Sunday = 6
            score += 5
            indicators.append('weekend_transaction')
            risk_factors.append("Transaction on weekend")
        
        return score
    
    def _analyze_merchant_category(self, category: str, indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze merchant category for fraud indicators"""
        score = 0
        rules = self.fraud_rules['merchant_risk']
        
        if category in rules['high_risk_categories']:
            score += rules['weight']
            indicators.append('high_risk_merchant')
            risk_factors.append(f"High-risk merchant category: {category}")
        elif category in rules['medium_risk_categories']:
            score += rules['weight'] * 0.6
            indicators.append('medium_risk_merchant')
            risk_factors.append(f"Medium-risk merchant category: {category}")
        
        return score
    
    def _analyze_transaction_type(self, transaction_type: str, amount: float, indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze transaction type for fraud indicators"""
        score = 0
        
        # Wire transfers are inherently higher risk
        if transaction_type == 'transfer':
            score += 15
            indicators.append('wire_transfer')
            risk_factors.append("Wire transfer transaction")
            
            # Large wire transfers are very high risk
            if amount >= 5000:
                score += 10
                indicators.append('large_wire_transfer')
                risk_factors.append(f"Large wire transfer: ${amount:,.2f}")
        
        # Large cash withdrawals
        elif transaction_type == 'withdrawal' and amount >= 1000:
            score += 10
            indicators.append('large_withdrawal')
            risk_factors.append(f"Large cash withdrawal: ${amount:,.2f}")
        
        return score
    
    def _analyze_velocity_patterns(self, transaction: Dict[str, Any], indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze transaction velocity patterns (simplified)"""
        score = 0
        
        # In a real system, this would check transaction history
        # For simulation, we'll use some heuristics based on transaction data
        
        # Check if this looks like a rapid-fire transaction
        if transaction.get('is_suspicious_template', False):
            score += 20
            indicators.append('suspicious_pattern')
            risk_factors.append("Transaction matches suspicious pattern")
        
        # Simulate velocity check based on customer risk profile
        customer_risk = transaction.get('customer_risk_profile', 'medium')
        if customer_risk == 'high':
            score += 15
            indicators.append('high_risk_customer')
            risk_factors.append("Customer has high risk profile")
        
        return score
    
    def _analyze_fraud_patterns(self, transaction: Dict[str, Any], indicators: List[str], risk_factors: List[str]) -> float:
        """Analyze for known fraud patterns"""
        score = 0
        
        amount = float(transaction.get('amount', 0))
        location = transaction.get('location', '')
        merchant_category = transaction.get('merchant_category', '')
        
        # Check each known pattern
        for pattern in self.fraud_patterns:
            pattern_indicators = pattern['indicators']
            matches = 0
            
            # Check pattern indicators
            if 'high_amount' in pattern_indicators and amount >= 5000:
                matches += 1
            
            if 'foreign_location' in pattern_indicators:
                foreign_keywords = ['UK', 'France', 'Japan', 'Australia']
                if any(keyword in location for keyword in foreign_keywords):
                    matches += 1
            
            if 'unusual_merchant' in pattern_indicators and merchant_category in ['luxury', 'electronics']:
                matches += 1
            
            if 'wire_transfer' in pattern_indicators and transaction.get('transaction_type') == 'transfer':
                matches += 1
            
            # If pattern matches, add to score
            if matches >= len(pattern_indicators) * 0.6:  # 60% match threshold
                pattern_score = pattern['risk_score'] * 0.3  # Scale down for rule-based
                score += pattern_score
                indicators.append(f"pattern_{pattern['name']}")
                risk_factors.append(f"Matches {pattern['name']} pattern: {pattern['description']}")
        
        return score
    
    def _generate_rule_explanation(self, fraud_score: float, indicators: List[str], risk_factors: List[str]) -> str:
        """Generate explanation for rule-based analysis"""
        explanation = f"Rule-based fraud analysis score: {fraud_score:.1f}/100. "
        
        if fraud_score >= 80:
            explanation += "HIGH RISK - Multiple fraud indicators detected. "
        elif fraud_score >= 50:
            explanation += "MEDIUM RISK - Some fraud indicators present. "
        elif fraud_score >= 30:
            explanation += "LOW RISK - Minor risk factors identified. "
        else:
            explanation += "VERY LOW RISK - No significant fraud indicators. "
        
        if risk_factors:
            explanation += f"Key factors: {'; '.join(risk_factors[:3])}"  # Top 3 factors
        
        return explanation
    
    def _create_fraud_analysis_prompt(self, transaction: Dict[str, Any], rule_result: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for AI fraud analysis"""
        prompt = f"""You are an expert fraud analyst at a major financial institution. Analyze this transaction for potential fraud using advanced pattern recognition and behavioral analysis.

TRANSACTION DETAILS:
- Transaction ID: {transaction.get('transaction_id', 'N/A')}
- Customer: {transaction.get('customer_name', 'N/A')} ({transaction.get('customer_id', 'N/A')})
- Amount: ${transaction.get('amount', 0):,.2f}
- Merchant: {transaction.get('merchant', 'N/A')}
- Category: {transaction.get('merchant_category', 'N/A')}
- Type: {transaction.get('transaction_type', 'N/A')}
- Location: {transaction.get('location', 'N/A')}
- Timestamp: {transaction.get('timestamp', 'N/A')}
- Account Type: {transaction.get('account_type', 'N/A')}

RULE-BASED ANALYSIS RESULTS:
- Fraud Score: {rule_result.get('fraud_score', 0):.1f}/100
- Risk Level: {rule_result.get('risk_level', 'unknown').upper()}
- Detected Indicators: {', '.join(rule_result.get('fraud_indicators', []))}
- Risk Factors: {'; '.join(rule_result.get('risk_factors', []))}

ANALYSIS REQUIREMENTS:
1. Evaluate transaction legitimacy using behavioral analysis
2. Consider customer profile and typical spending patterns
3. Assess geographic and temporal risk factors
4. Identify potential fraud typologies (card fraud, identity theft, money laundering, etc.)
5. Analyze merchant and transaction type risk
6. Consider velocity and pattern anomalies
7. Provide confidence assessment and recommendations

KNOWN FRAUD PATTERNS TO CONSIDER:
- Card Testing: Multiple small transactions
- Account Takeover: Unusual location + high value
- Synthetic Identity: New account + immediate high spending
- Money Laundering: Structured amounts, frequent transfers
- Skimming: ATM transactions in high-risk areas
- Online Fraud: E-commerce with shipping mismatches

Respond ONLY with a JSON object containing your analysis:

{{
    "is_fraud": true/false,
    "fraud_score": 0-100,
    "risk_level": "very_low"/"low"/"medium"/"high"/"critical",
    "confidence": 0-100,
    "fraud_type": "card_fraud"/"identity_theft"/"money_laundering"/"account_takeover"/"legitimate"/"other",
    "fraud_indicators": ["list of specific fraud indicators found"],
    "behavioral_anomalies": ["list of behavioral red flags"],
    "risk_factors": ["list of risk factors"],
    "legitimacy_factors": ["list of factors supporting legitimacy"],
    "explanation": "detailed explanation of the analysis",
    "recommendations": ["list of recommended actions"],
    "investigation_priority": "low"/"medium"/"high"/"urgent"
}}

Do not include any text outside the JSON object."""
        
        return prompt
    
    def _get_ai_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get AI fraud analysis from the language model"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to call AI fraud analysis API")
                
                response = requests.post(
                    self.api_base,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=45  # Timeout for fraud analysis
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
                logger.error(f"Unexpected error in AI fraud analysis (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error("All AI fraud analysis attempts failed")
        return None
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse the AI response JSON"""
        try:
            logger.debug(f"Parsing AI fraud response: {response_text[:500]}...")  # Log first 500 chars
            
            # Clean up the response text
            json_str = response_text.strip()
            if not json_str.startswith('{'):
                json_str = json_str[json_str.find('{'):]
            if not json_str.endswith('}'):
                json_str = json_str[:json_str.rfind('}')+1]
            
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['is_fraud', 'fraud_score', 'risk_level', 'explanation']
            if not all(field in result for field in required_fields):
                logger.error(f"Missing required fields in AI response. Required: {required_fields}, Got: {list(result.keys())}")
                return None
            
            # Validate and normalize field values
            result['is_fraud'] = bool(result.get('is_fraud', False))
            
            # Ensure fraud score is within range
            result['fraud_score'] = max(0, min(100, float(result.get('fraud_score', 0))))
            
            # Validate risk level
            valid_risk_levels = ['very_low', 'low', 'medium', 'high', 'critical']
            if result['risk_level'] not in valid_risk_levels:
                result['risk_level'] = 'medium'  # Default to medium if invalid
            
            # Ensure confidence is within range
            if 'confidence' in result:
                result['confidence'] = max(0, min(100, float(result.get('confidence', 0))))
            
            # Ensure lists are actually lists
            list_fields = ['fraud_indicators', 'behavioral_anomalies', 'risk_factors', 'legitimacy_factors', 'recommendations']
            for field in list_fields:
                if field in result and not isinstance(result[field], list):
                    result[field] = [str(result[field])] if result[field] else []
            
            logger.debug(f"Successfully parsed AI fraud response: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}\nResponse text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI fraud response: {str(e)}\nResponse text: {response_text}")
            return None
    
    def _combine_ai_and_rules(self, ai_result: Dict[str, Any], rule_result: Dict[str, Any], transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Combine AI insights with rule-based analysis"""
        try:
            # Start with AI result as base
            combined_result = ai_result.copy()
            
            # Combine fraud indicators
            ai_indicators = ai_result.get('fraud_indicators', [])
            rule_indicators = rule_result.get('fraud_indicators', [])
            combined_indicators = list(set(ai_indicators + rule_indicators))
            
            # Combine risk factors
            ai_risk_factors = ai_result.get('risk_factors', [])
            rule_risk_factors = rule_result.get('risk_factors', [])
            combined_risk_factors = list(set(ai_risk_factors + rule_risk_factors))
            
            # Calculate weighted fraud score (AI: 60%, Rules: 40%)
            ai_score = ai_result.get('fraud_score', 0)
            rule_score = rule_result.get('fraud_score', 0)
            combined_score = (ai_score * 0.6) + (rule_score * 0.4)
            
            # Determine final risk level based on combined score
            if combined_score >= 85:
                final_risk_level = 'critical'
            elif combined_score >= 70:
                final_risk_level = 'high'
            elif combined_score >= 50:
                final_risk_level = 'medium'
            elif combined_score >= 30:
                final_risk_level = 'low'
            else:
                final_risk_level = 'very_low'
            
            # Determine if fraud based on combined analysis
            is_fraud = combined_score >= 50 or (ai_result.get('is_fraud', False) and rule_score >= 30)
            
            # Calculate confidence (average of AI confidence and rule confidence)
            ai_confidence = ai_result.get('confidence', 0)
            rule_confidence = rule_result.get('confidence', 0)
            combined_confidence = (ai_confidence + rule_confidence) / 2
            
            # Update combined result
            combined_result.update({
                'fraud_score': combined_score,
                'risk_level': final_risk_level,
                'is_fraud': is_fraud,
                'fraud_indicators': combined_indicators,
                'risk_factors': combined_risk_factors,
                'ai_confidence': ai_confidence,
                'rule_confidence': rule_confidence,
                'combined_confidence': combined_confidence,
                'analysis_method': 'ai_enhanced',
                'ai_score': ai_score,
                'rule_score': rule_score,
                'score_weights': {'ai': 0.6, 'rules': 0.4}
            })
            
            # Enhance explanation
            ai_explanation = ai_result.get('explanation', '')
            rule_explanation = rule_result.get('explanation', '')
            combined_explanation = f"AI-Enhanced Analysis: {ai_explanation} Rule-based validation: {rule_explanation}"
            combined_result['explanation'] = combined_explanation
            
            logger.debug(f"Combined AI and rule analysis: Score={combined_score:.1f}, Risk={final_risk_level}")
            return combined_result
            
        except Exception as e:
            logger.error(f"Error combining AI and rule analysis: {str(e)}")
            # Fallback to rule-based result
            rule_result['analysis_method'] = 'rule_based_fallback'
            return rule_result
    
    def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud detection statistics"""
        # In a real system, this would query the database for statistics
        # For simulation, return mock statistics
        return {
            'total_transactions_analyzed': random.randint(1000, 5000),
            'fraud_detected': random.randint(50, 200),
            'false_positives': random.randint(10, 50),
            'detection_accuracy': random.uniform(85, 95),
            'average_analysis_time': random.uniform(0.5, 2.0),
            'high_risk_transactions': random.randint(20, 100),
            'patterns_detected': {
                'card_testing': random.randint(5, 20),
                'account_takeover': random.randint(3, 15),
                'money_laundering': random.randint(2, 10),
                'synthetic_identity': random.randint(1, 8)
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the fraud analyzer
    analyzer = FraudAnalyzer()
    
    # Test transaction data
    test_transactions = [
        {
            'transaction_id': 'TXN001',
            'customer_id': 'CUST001',
            'customer_name': 'John Doe',
            'amount': 50.0,
            'merchant': 'Local Grocery',
            'merchant_category': 'grocery',
            'transaction_type': 'purchase',
            'location': 'New York',
            'timestamp': datetime.now().isoformat(),
            'account_type': 'standard',
            'customer_risk_profile': 'low'
        },
        {
            'transaction_id': 'TXN002',
            'customer_id': 'CUST002',
            'customer_name': 'Jane Smith',
            'amount': 8500.0,
            'merchant': 'Luxury Electronics',
            'merchant_category': 'electronics',
            'transaction_type': 'purchase',
            'location': 'Tokyo, Japan',
            'timestamp': datetime.now().isoformat(),
            'account_type': 'premium',
            'customer_risk_profile': 'medium',
            'is_suspicious_template': True
        }
    ]
    
    for transaction in test_transactions:
        try:
            print(f"\nAnalyzing transaction {transaction['transaction_id']}:")
            result = analyzer.analyze_transaction(transaction)
            
            print(f"Fraud Score: {result.get('fraud_score', 0):.1f}/100")
            print(f"Risk Level: {result.get('risk_level', 'unknown').upper()}")
            print(f"Is Fraud: {result.get('is_fraud', False)}")
            print(f"Analysis Method: {result.get('analysis_method', 'unknown')}")
            print(f"Confidence: {result.get('combined_confidence', result.get('confidence', 0)):.1f}%")
            
            if result.get('fraud_indicators'):
                print(f"Fraud Indicators: {', '.join(result['fraud_indicators'])}")
            
            if result.get('risk_factors'):
                print(f"Risk Factors: {'; '.join(result['risk_factors'][:3])}")  # Show top 3
            
            print(f"Explanation: {result.get('explanation', 'No explanation provided')[:200]}...")  # First 200 chars
            
        except Exception as e:
            print(f"Error analyzing transaction {transaction['transaction_id']}: {e}")
    
    # Test statistics
    print("\nFraud Detection Statistics:")
    stats = analyzer.get_fraud_statistics()
    print(f"Total Analyzed: {stats['total_transactions_analyzed']}")
    print(f"Fraud Detected: {stats['fraud_detected']}")
    print(f"Detection Accuracy: {stats['detection_accuracy']:.1f}%")
    
    print("Fraud analyzer test completed")