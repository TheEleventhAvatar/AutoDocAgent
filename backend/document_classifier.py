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

class DocumentClassifier:
    """Classify documents into categories using AI and patterns"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Document type patterns for quick classification
        self.patterns = {
            "invoice": [
                r"invoice\s*#?", r"bill\s*to", r"amount\s*due", r"total\s*due",
                r"tax\s*invoice", r"invoice\s*date", r"payment\s*terms"
            ],
            "resume": [
                r"resume", r"curriculum\s*vitae", r"work\s*experience", r"education",
                r"skills", r"objective", r"employment\s*history"
            ],
            "kyc": [
                r"kyc", r"know\s*your\s*customer", r"identity\s*verification",
                r"proof\s*of\s*identity", r"address\s*proof", r"pan\s*card", r"aadhaar"
            ],
            "bank_statement": [
                r"bank\s*statement", r"account\s*statement", r"transaction\s*history",
                r"balance", r"debit", r"credit", r"withdrawal", r"deposit"
            ],
            "id_card": [
                r"driver\s*license", r"passport", r"national\s*id", r"identity\s*card",
                r"date\s*of\s*birth", r"place\s*of\s*birth", r"issuing\s*authority"
            ],
            "passport": [
                r"passport", r"passport\s*no", r"place\s*of\s*birth", r"nationality",
                r"date\s*of\s*issue", r"date\s*of\s*expiry"
            ],
            "pan_card": [
                r"permanent\s*account\s*number", r"pan\s*card", r"income\s*tax",
                r"[A-Z]{5}[0-9]{4}[A-Z]{1}"  # PAN format
            ],
            "aadhaar_card": [
                r"aadhaar", r"uidai", r"unique\s*identification", r"12\s*digit",
                r"\d{4}\s\d{4}\s\d{4}"  # Aadhaar format
            ]
        }
        
        # Keywords for each document type
        self.keywords = {
            "invoice": ["invoice", "bill", "amount", "total", "tax", "due", "payment"],
            "resume": ["resume", "experience", "education", "skills", "employment", "career"],
            "kyc": ["kyc", "verification", "identity", "proof", "document"],
            "bank_statement": ["bank", "account", "statement", "balance", "transaction"],
            "id_card": ["license", "passport", "identification", "identity", "card"],
            "passport": ["passport", "travel", "nationality", "immigration"],
            "pan_card": ["pan", "income", "tax", "permanent", "account"],
            "aadhaar_card": ["aadhaar", "uid", "unique", "identification", "government"]
        }
    
    def classify(self, text: str) -> str:
        """Classify document type from text"""
        try:
            logger.info("Classifying document type")
            
            # Quick pattern-based classification first
            pattern_result = self._classify_by_patterns(text)
            if pattern_result and pattern_result != "general":
                logger.info(f"Pattern-based classification: {pattern_result}")
                return pattern_result
            
            # AI-based classification for more complex cases
            ai_result = self._classify_by_ai(text)
            logger.info(f"AI-based classification: {ai_result}")
            return ai_result
            
        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return "general"
    
    def _classify_by_patterns(self, text: str) -> str:
        """Classify document using regex patterns"""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                scores[doc_type] = score
        
        if scores:
            # Return the type with highest score
            best_type = max(scores, key=scores.get)
            if scores[best_type] >= 2:  # Minimum threshold
                return best_type
        
        return "general"
    
    def _classify_by_ai(self, text: str) -> str:
        """Classify document using AI"""
        try:
            prompt = f"""
Analyze the following document text and classify it into one of these categories:
- invoice
- resume
- kyc
- bank_statement
- id_card
- passport
- pan_card
- aadhaar_card
- general

Document Text:
{text[:3000]}  # Limit text length

Respond with only the category name.
"""
            
            messages = [
                SystemMessage(content="You are an expert document classifier. Identify the document type accurately."),
                HumanMessage(content=prompt)
            ]
            
            response = self.chat_model(messages)
            classification = response.content.strip().lower()
            
            # Validate classification
            valid_types = list(self.patterns.keys()) + ["general"]
            if classification in valid_types:
                return classification
            else:
                logger.warning(f"Invalid AI classification: {classification}")
                return "general"
                
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return "general"
    
    def get_classification_confidence(self, text: str, doc_type: str) -> float:
        """Get confidence score for document classification"""
        text_lower = text.lower()
        doc_type_lower = doc_type.lower()
        
        # Pattern-based confidence
        pattern_score = 0
        if doc_type_lower in self.patterns:
            patterns = self.patterns[doc_type_lower]
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                pattern_score += len(matches)
        
        # Keyword-based confidence
        keyword_score = 0
        if doc_type_lower in self.keywords:
            keywords = self.keywords[doc_type_lower]
            for keyword in keywords:
                keyword_count = text_lower.count(keyword)
                keyword_score += keyword_count
        
        # Calculate normalized confidence
        total_score = pattern_score * 2 + keyword_score  # Give more weight to patterns
        max_possible = len(self.patterns.get(doc_type_lower, [])) * 2 + len(self.keywords.get(doc_type_lower, []))
        
        if max_possible > 0:
            confidence = min(total_score / max_possible, 1.0)
        else:
            confidence = 0.0
        
        return confidence
    
    def get_all_classifications(self, text: str) -> List[Dict[str, Any]]:
        """Get all possible classifications with confidence scores"""
        text_lower = text.lower()
        classifications = []
        
        for doc_type in self.patterns.keys():
            confidence = self.get_classification_confidence(text, doc_type)
            if confidence > 0.1:  # Minimum threshold
                classifications.append({
                    "type": doc_type,
                    "confidence": confidence
                })
        
        # Sort by confidence
        classifications.sort(key=lambda x: x["confidence"], reverse=True)
        return classifications
    
    def extract_document_metadata(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract metadata specific to document type"""
        metadata = {
            "document_type": doc_type,
            "confidence": self.get_classification_confidence(text, doc_type)
        }
        
        # Type-specific metadata extraction
        if doc_type.lower() == "invoice":
            metadata.update(self._extract_invoice_metadata(text))
        elif doc_type.lower() == "resume":
            metadata.update(self._extract_resume_metadata(text))
        elif doc_type.lower() == "kyc":
            metadata.update(self._extract_kyc_metadata(text))
        elif doc_type.lower() == "bank_statement":
            metadata.update(self._extract_bank_statement_metadata(text))
        
        return metadata
    
    def _extract_invoice_metadata(self, text: str) -> Dict[str, Any]:
        """Extract invoice-specific metadata"""
        metadata = {}
        
        # Invoice number
        invoice_patterns = [
            r"invoice\s*#?\s*([A-Z0-9-]+)",
            r"bill\s*#?\s*([A-Z0-9-]+)",
            r"invoice\s*no\s*[:\-]?\s*([A-Z0-9-]+)"
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["invoice_number"] = match.group(1)
                break
        
        # Amount patterns
        amount_patterns = [
            r"total\s*[:\-]?\s*[$₹€£]?\s*([\d,]+\.?\d*)",
            r"amount\s*due\s*[:\-]?\s*[$₹€£]?\s*([\d,]+\.?\d*)",
            r"grand\s*total\s*[:\-]?\s*[$₹€£]?\s*([\d,]+\.?\d*)"
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    metadata["total_amount"] = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    continue
        
        return metadata
    
    def _extract_resume_metadata(self, text: str) -> Dict[str, Any]:
        """Extract resume-specific metadata"""
        metadata = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            metadata["email"] = emails[0]
        
        # Phone
        phone_patterns = [
            r'\+?\d{10,15}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                metadata["phone"] = phones[0]
                break
        
        return metadata
    
    def _extract_kyc_metadata(self, text: str) -> Dict[str, Any]:
        """Extract KYC-specific metadata"""
        metadata = {}
        
        # PAN number
        pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        pans = re.findall(pan_pattern, text)
        if pans:
            metadata["pan_number"] = pans[0]
        
        # Aadhaar number
        aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        aadhaars = re.findall(aadhaar_pattern, text)
        if aadhaars:
            metadata["aadhaar_number"] = aadhaars[0].replace(' ', '')
        
        return metadata
    
    def _extract_bank_statement_metadata(self, text: str) -> Dict[str, Any]:
        """Extract bank statement-specific metadata"""
        metadata = {}
        
        # Account number
        account_patterns = [
            r"account\s*no\s*[:\-]?\s*(\d+)",
            r"account\s*number\s*[:\-]?\s*(\d+)",
            r"a/c\s*no\s*[:\-]?\s*(\d+)"
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["account_number"] = match.group(1)
                break
        
        # IFSC code
        ifsc_pattern = r"ifsc\s*code\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})"
        match = re.search(ifsc_pattern, text, re.IGNORECASE)
        if match:
            metadata["ifsc_code"] = match.group(1)
        
        return metadata
