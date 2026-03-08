import os
import re
import logging
from typing import Dict, Any, List, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticFieldMapper:
    """Map template fields to extracted data using semantic similarity"""
    
    def __init__(self):
        # Load sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Common field mappings for quick lookup
        self.field_synonyms = {
            "name": ["full name", "applicant name", "person name", "individual name", "customer name"],
            "first_name": ["given name", "forename", "first name"],
            "last_name": ["surname", "family name", "last name"],
            "date_of_birth": ["dob", "birth date", "birthdate", "born on"],
            "address": ["street address", "residential address", "home address", "mailing address"],
            "phone": ["phone number", "telephone", "mobile", "contact number", "cell phone"],
            "email": ["email address", "mail", "electronic mail", "email id"],
            "pan": ["pan number", "permanent account number", "pan card"],
            "aadhar": ["aadhaar number", "uid", "aadhar card", "unique identification"],
            "passport": ["passport number", "passport no", "travel document"],
            "company": ["organization", "employer", "firm", "business name"],
            "position": ["job title", "designation", "role", "employment title"],
            "salary": ["income", "annual income", "earnings", "compensation"],
            "account": ["account number", "bank account", "account no"],
            "ifsc": ["ifsc code", "bank code", "branch code"],
            "policy": ["policy number", "policy no", "insurance policy"],
            "invoice": ["invoice number", "invoice no", "bill number"]
        }
        
        # Cache for embeddings
        self.embedding_cache = {}
    
    def map_fields(self, template_path: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map template fields to extracted data"""
        try:
            logger.info(f"Mapping fields for template: {template_path}")
            
            # Get template fields
            template_fields = self._extract_template_fields(template_path)
            
            if not template_fields:
                logger.warning("No template fields found")
                return {}
            
            # Create mappings
            mapped_data = {}
            extracted_keys = list(extracted_data.keys())
            
            for template_field in template_fields:
                best_match = self._find_best_match(template_field, extracted_keys)
                
                if best_match and best_match[1] > 0.6:  # Confidence threshold
                    mapped_data[template_field] = extracted_data[best_match[0]]
                    logger.info(f"Mapped '{template_field}' -> '{best_match[0]}' (confidence: {best_match[1]:.2f})")
                else:
                    logger.warning(f"No good match found for template field: '{template_field}'")
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"Field mapping failed: {e}")
            return {}
    
    def _extract_template_fields(self, template_path: str) -> List[str]:
        """Extract field names from template"""
        template_path = template_path.lower()
        
        if template_path.endswith('.pdf'):
            return self._extract_pdf_fields(template_path)
        elif template_path.endswith(('.xlsx', '.xls')):
            return self._extract_excel_fields(template_path)
        else:
            logger.warning(f"Unsupported template format: {template_path}")
            return []
    
    def _extract_pdf_fields(self, pdf_path: str) -> List[str]:
        """Extract field names from PDF form"""
        try:
            import pypdf
            
            fields = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Try to get form fields
                if '/AcroForm' in pdf_reader.trailer['/Root']:
                    form_fields = pdf_reader.get_fields()
                    if form_fields:
                        fields = list(form_fields.keys())
                else:
                    # Fallback: extract text and look for field-like patterns
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        fields.extend(self._extract_fields_from_text(text))
            
            return list(set(fields))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Failed to extract PDF fields: {e}")
            return []
    
    def _extract_excel_fields(self, excel_path: str) -> List[str]:
        """Extract field names from Excel template"""
        try:
            import openpyxl
            
            fields = []
            workbook = openpyxl.load_workbook(excel_path, read_only=True)
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                
                # Look for field labels in first row
                for cell in sheet[1]:  # First row
                    if cell.value and str(cell.value).strip():
                        field_name = str(cell.value).strip()
                        if self._is_field_like(field_name):
                            fields.append(field_name)
            
            workbook.close()
            return list(set(fields))
            
        except Exception as e:
            logger.error(f"Failed to extract Excel fields: {e}")
            return []
    
    def _extract_fields_from_text(self, text: str) -> List[str]:
        """Extract field-like patterns from text"""
        import re
        
        fields = []
        
        # Common field patterns
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[:\-]',
            r'([A-Z_]+)\s*[:\-]',
            r'(\b(?:Name|Address|Phone|Email|Date|Signature)\b)\s*[:\-]',
            r'(\b\w+\s+\w+\s*\w*)\s*[:\-]'  # Multi-word fields
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            fields.extend(matches)
        
        return fields
    
    def _is_field_like(self, text: str) -> bool:
        """Check if text looks like a field name"""
        field_indicators = [
            'name', 'address', 'phone', 'email', 'date', 'signature',
            'number', 'id', 'code', 'amount', 'total', 'balance',
            'account', 'policy', 'invoice', 'receipt', 'reference'
        ]
        
        text_lower = text.lower()
        
        # Check if contains field indicators
        for indicator in field_indicators:
            if indicator in text_lower:
                return True
        
        # Check if ends with common field suffixes
        field_suffixes = ['no', 'num', 'number', 'code', 'id', 'date']
        for suffix in field_suffixes:
            if text_lower.endswith(suffix):
                return True
        
        # Check if it's all caps or title case (common for field names)
        if text.isupper() or text.istitle():
            return True
        
        return False
    
    def _find_best_match(self, template_field: str, extracted_keys: List[str]) -> Tuple[str, float]:
        """Find the best matching extracted field for a template field"""
        if not extracted_keys:
            return None, 0.0
        
        # Quick synonym lookup first
        for extracted_key in extracted_keys:
            if self._are_synonyms(template_field, extracted_key):
                return extracted_key, 0.95
        
        # Semantic similarity matching
        template_embedding = self._get_embedding(template_field)
        extracted_embeddings = [self._get_embedding(key) for key in extracted_keys]
        
        similarities = cosine_similarity(
            [template_embedding],
            extracted_embeddings
        )[0]
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        if best_score > 0.6:  # Threshold for semantic matching
            return extracted_keys[best_idx], float(best_score)
        
        return None, 0.0
    
    def _are_synonyms(self, field1: str, field2: str) -> bool:
        """Check if two fields are synonyms"""
        field1_lower = field1.lower()
        field2_lower = field2.lower()
        
        # Exact match
        if field1_lower == field2_lower:
            return True
        
        # Check synonym dictionary
        for canonical, synonyms in self.field_synonyms.items():
            if field1_lower in [canonical] + synonyms and field2_lower in [canonical] + synonyms:
                return True
        
        # Check if one contains the other
        if field1_lower in field2_lower or field2_lower in field1_lower:
            return True
        
        return False
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text (with caching)"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        embedding = self.model.encode(text)
        self.embedding_cache[text] = embedding
        return embedding
    
    def get_field_mapping_confidence(self, template_field: str, extracted_field: str) -> float:
        """Get confidence score for a specific field mapping"""
        # Synonym check
        if self._are_synonyms(template_field, extracted_field):
            return 0.95
        
        # Semantic similarity
        template_embedding = self._get_embedding(template_field)
        extracted_embedding = self._get_embedding(extracted_field)
        
        similarity = cosine_similarity(
            [template_embedding],
            [extracted_embedding]
        )[0][0]
        
        return float(similarity)
    
    def suggest_field_corrections(self, template_field: str, extracted_keys: List[str]) -> List[Tuple[str, float]]:
        """Suggest possible field corrections with confidence scores"""
        suggestions = []
        
        for extracted_key in extracted_keys:
            confidence = self.get_field_mapping_confidence(template_field, extracted_key)
            if confidence > 0.3:  # Only include reasonable matches
                suggestions.append((extracted_key, confidence))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:5]  # Top 5 suggestions
