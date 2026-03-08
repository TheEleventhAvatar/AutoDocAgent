import os
import re
import logging
from typing import Dict, Any, List
from openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDataExtractor:
    """Use AI to extract structured data from document text"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Common fields to extract
        self.common_fields = [
            "name", "full_name", "first_name", "last_name",
            "date_of_birth", "dob", "birth_date",
            "address", "street_address", "city", "state", "postal_code", "zip_code",
            "phone", "phone_number", "mobile", "telephone",
            "email", "email_address",
            "pan", "pan_number",
            "aadhar", "aadhaar", "aadhar_number",
            "passport_number", "passport_no",
            "company", "organization", "employer",
            "position", "job_title", "designation",
            "salary", "income", "annual_income",
            "account_number", "bank_account",
            "ifsc_code", "bank_name",
            "policy_number", "policy_no",
            "invoice_number", "invoice_no",
            "amount", "total", "price"
        ]
    
    def extract_structured_data(self, text: str, document_type: str = "general") -> Dict[str, Any]:
        """Extract structured data from text using AI"""
        try:
            logger.info(f"Extracting structured data from {document_type} document")
            
            # Create prompt based on document type
            prompt = self._create_extraction_prompt(text, document_type)
            
            # Use LangChain for structured extraction
            messages = [
                SystemMessage(content="You are an expert data extraction assistant. Extract structured information from documents accurately."),
                HumanMessage(content=prompt)
            ]
            
            response = self.chat_model(messages)
            extracted_data = self._parse_ai_response(response.content)
            
            logger.info(f"Extracted {len(extracted_data)} fields")
            return extracted_data
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            # Fallback to basic pattern matching
            return self._fallback_extraction(text)
    
    def _create_extraction_prompt(self, text: str, document_type: str) -> str:
        """Create a prompt for AI extraction based on document type"""
        
        base_prompt = f"""
Extract structured information from the following {document_type} document text.

Document Text:
{text[:4000]}  # Limit text length for API

Please extract the following fields if present:
{', '.join(self.common_fields)}

Return the response as a valid JSON object with field names as keys and extracted values as values.
If a field is not found, omit it from the JSON.
"""
        
        # Add document-type specific instructions
        if document_type.lower() == "resume":
            base_prompt += "\nFocus on extracting personal details, contact information, and professional information."
        elif document_type.lower() == "invoice":
            base_prompt += "\nFocus on extracting invoice details, amounts, dates, and vendor information."
        elif document_type.lower() == "kyc":
            base_prompt += "\nFocus on extracting identity verification details like name, DOB, ID numbers, and address."
        elif document_type.lower() == "bank_statement":
            base_prompt += "\nFocus on extracting account details, bank information, and transaction summaries."
        
        base_prompt += "\n\nJSON Response:"
        return base_prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response to extract JSON data"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in AI response")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {}
    
    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback extraction using basic patterns"""
        import re
        
        extracted = {}
        text_lower = text.lower()
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            extracted["email"] = emails[0]
        
        # Phone extraction (basic patterns)
        phone_patterns = [
            r'\+?\d{10,15}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                extracted["phone"] = phones[0]
                break
        
        # PAN number pattern
        pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        pans = re.findall(pan_pattern, text)
        if pans:
            extracted["pan"] = pans[0]
        
        # Aadhaar pattern
        aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        aadhaars = re.findall(aadhaar_pattern, text)
        if aadhaars:
            extracted["aadhar"] = aadhaars[0].replace(' ', '')
        
        logger.info(f"Fallback extraction found {len(extracted)} fields")
        return extracted
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data"""
        validated = {}
        
        for key, value in data.items():
            if value and str(value).strip():
                # Basic validation
                if key == "email" and "@" in str(value):
                    validated[key] = str(value).strip().lower()
                elif key == "phone":
                    # Clean phone number
                    phone = re.sub(r'[^\d+]', '', str(value))
                    if len(phone) >= 10:
                        validated[key] = phone
                elif key == "pan":
                    # Validate PAN format
                    pan = str(value).upper().strip()
                    if len(pan) == 10 and re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan):
                        validated[key] = pan
                elif key == "aadhar":
                    # Validate Aadhaar format
                    aadhar = re.sub(r'\D', '', str(value))
                    if len(aadhar) == 12:
                        validated[key] = aadhar
                else:
                    validated[key] = str(value).strip()
        
        return validated
    
    def extract_field_confidence(self, text: str, field_name: str) -> float:
        """Get confidence score for a specific field extraction"""
        # This is a simplified confidence calculation
        # In production, you'd use more sophisticated methods
        
        text_lower = text.lower()
        field_lower = field_name.lower()
        
        # Check for exact field name mentions
        if field_lower in text_lower:
            return 0.8
        
        # Check for related keywords
        keyword_map = {
            "name": ["name", "full name", "applicant", "person"],
            "email": ["email", "mail", "contact"],
            "phone": ["phone", "mobile", "telephone", "contact"],
            "address": ["address", "location", "residence"],
            "pan": ["pan", "permanent account"],
            "aadhar": ["aadhar", "aadhaar", "uid"]
        }
        
        if field_lower in keyword_map:
            for keyword in keyword_map[field_lower]:
                if keyword in text_lower:
                    return 0.6
        
        return 0.3
