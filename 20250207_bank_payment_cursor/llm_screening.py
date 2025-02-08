import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMScreening:
    def __init__(self):
        self.api_base = "http://localhost:11434/api/generate"
        self.model = "llama3.2:1b"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        logger.info(f"LLMScreening initialized with model: {self.model}")
    
    def screen_payment(self, payment_data):
        logger.info(f"Starting payment screening for reference: {payment_data.get('reference', 'N/A')}")
        prompt = self._create_screening_prompt(payment_data)
        logger.debug(f"Generated prompt: {prompt}")
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} to call Ollama API")
                response = requests.post(
                    self.api_base,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=30
                )
                
                logger.debug(f"API Response status: {response.status_code}")
                logger.debug(f"API Response content: {response.text[:500]}...")  # Log first 500 chars
                
                if response.status_code == 200:
                    result = response.json()
                    parsed_result = self._parse_screening_result(result['response'])
                    logger.info(f"Screening completed with risk level: {parsed_result['risk_level']}")
                    return parsed_result
                else:
                    logger.error(f"API error (attempt {attempt + 1}/{self.max_retries}): {response.status_code}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return {
                        'allowed': False,
                        'risk_level': 'high',
                        'reason': f'LLM service error: {response.status_code}. Response: {response.text}'
                    }
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {
                    'allowed': False,
                    'risk_level': 'high',
                    'reason': f'LLM service connection error: {str(e)}'
                }
            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {
                    'allowed': False,
                    'risk_level': 'high',
                    'reason': f'Unexpected error: {str(e)}'
                }
    
    def _create_screening_prompt(self, payment_data):
        prompt = f"""You are a bank's payment screening system. Analyze this payment for potential risks and compliance issues.
Respond ONLY with a JSON object containing your analysis.

Payment Details:
- Sender: {payment_data['sender_name']} (Account: {payment_data['sender_account']})
- Receiver: {payment_data['receiver_name']} (Account: {payment_data['receiver_account']})
- Amount: {payment_data['amount']} {payment_data['currency']}
- Purpose: {payment_data['purpose']}

Analyze for:
1. Money laundering risks
2. Unusual patterns
3. Suspicious activity indicators
4. Compliance with banking regulations

Your response must be a valid JSON object with this exact structure:
{{
    "allowed": true/false,
    "risk_level": "low"/"medium"/"high",
    "reason": "detailed explanation"
}}

Do not include any other text outside the JSON object."""
        return prompt

    def _parse_screening_result(self, response_text):
        try:
            logger.debug(f"Parsing LLM response: {response_text[:500]}...")  # Log first 500 chars
            
            # Clean up the response text to ensure it's valid JSON
            json_str = response_text.strip()
            if not json_str.startswith('{'):
                json_str = json_str[json_str.find('{'):]
            if not json_str.endswith('}'):
                json_str = json_str[:json_str.rfind('}')+1]
            
            result = json.loads(json_str)
            logger.debug(f"Parsed JSON result: {result}")
            
            # Validate the required fields
            if not all(key in result for key in ['allowed', 'risk_level', 'reason']):
                raise ValueError("Missing required fields in LLM response")
            
            if result['risk_level'] not in ['low', 'medium', 'high']:
                result['risk_level'] = 'high'  # Default to high if invalid
            
            return {
                'allowed': bool(result.get('allowed', False)),
                'risk_level': result.get('risk_level', 'high'),
                'reason': str(result.get('reason', 'Unable to parse LLM response'))
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}\nResponse text: {response_text}")
            return {
                'allowed': False,
                'risk_level': 'high',
                'reason': f'Invalid JSON response from LLM: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}\nResponse text: {response_text}")
            return {
                'allowed': False,
                'risk_level': 'high',
                'reason': f'Error parsing LLM response: {str(e)}'
            } 