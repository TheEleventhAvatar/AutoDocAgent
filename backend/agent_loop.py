import os
import logging
from typing import Dict, Any, List, Set, Tuple
from pathlib import Path
import json
from datetime import datetime

from extractor import DocumentExtractor
from ai_agent import AIDataExtractor
from field_mapper import SemanticFieldMapper
from form_filler import FormFiller
from document_classifier import DocumentClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousAgent:
    """Autonomous agent that processes multiple documents and fills available templates"""
    
    def __init__(self):
        self.extractor = DocumentExtractor()
        self.ai_extractor = AIDataExtractor()
        self.field_mapper = SemanticFieldMapper()
        self.form_filler = FormFiller()
        self.doc_classifier = DocumentClassifier()
        
        # Common required fields for different form types
        self.form_requirements = {
            "kyc_form": {
                "required": ["name", "date_of_birth", "address", "pan", "aadhar"],
                "optional": ["phone", "email"]
            },
            "hr_onboarding": {
                "required": ["name", "address", "phone", "email", "date_of_birth"],
                "optional": ["company", "position", "salary"]
            },
            "tax_form": {
                "required": ["name", "pan", "address"],
                "optional": ["phone", "email", "income"]
            },
            "bank_account": {
                "required": ["name", "address", "phone"],
                "optional": ["email", "account_number", "ifsc_code"]
            }
        }
    
    def run_autonomous_workflow(self, file_paths: List[str], template_directory: str) -> Dict[str, Any]:
        """Run the complete autonomous workflow"""
        try:
            logger.info(f"Starting autonomous workflow with {len(file_paths)} documents")
            
            # Step 1: Extract and analyze all documents
            document_data = self._process_all_documents(file_paths)
            
            # Step 2: Get available templates
            templates = self._get_available_templates(template_directory)
            
            # Step 3: Determine which templates can be filled
            fillable_templates = self._identify_fillable_templates(document_data, templates)
            
            # Step 4: Fill the templates
            filled_documents = self._fill_templates(fillable_templates, document_data)
            
            # Step 5: Generate missing fields report
            missing_fields_report = self._generate_missing_fields_report(fillable_templates, document_data)
            
            result = {
                "status": "completed",
                "processed_documents": len(file_paths),
                "extracted_data": document_data,
                "available_templates": len(templates),
                "filled_templates": len(filled_documents),
                "filled_documents": filled_documents,
                "missing_fields": missing_fields_report,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Autonomous workflow completed. Filled {len(filled_documents)} templates.")
            return result
            
        except Exception as e:
            logger.error(f"Autonomous workflow failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_all_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Process all documents and merge extracted data"""
        logger.info("Processing all documents...")
        
        merged_data = {}
        document_info = []
        
        for file_path in file_paths:
            try:
                # Extract text
                text = self.extractor.extract_text(file_path)
                
                # Classify document
                doc_type = self.doc_classifier.classify(text)
                
                # Extract structured data
                structured_data = self.ai_extractor.extract_structured_data(text, doc_type)
                
                # Merge data (later documents override earlier ones)
                merged_data.update(structured_data)
                
                # Track document info
                document_info.append({
                    "file_path": file_path,
                    "type": doc_type,
                    "extracted_fields": list(structured_data.keys()),
                    "text_length": len(text)
                })
                
                logger.info(f"Processed {file_path}: {doc_type}, {len(structured_data)} fields")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                document_info.append({
                    "file_path": file_path,
                    "type": "error",
                    "error": str(e)
                })
        
        # Clean and validate merged data
        cleaned_data = self.ai_extractor.validate_extracted_data(merged_data)
        
        return {
            "merged_fields": cleaned_data,
            "document_count": len(file_paths),
            "document_info": document_info,
            "total_fields_extracted": len(cleaned_data)
        }
    
    def _get_available_templates(self, template_directory: str) -> List[Dict[str, Any]]:
        """Get list of available templates"""
        logger.info(f"Scanning templates in {template_directory}")
        
        templates = []
        template_dir = Path(template_directory)
        
        if not template_dir.exists():
            logger.warning(f"Template directory not found: {template_directory}")
            return templates
        
        for file_path in template_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.xlsx', '.xls']:
                try:
                    template_info = self.form_filler.get_template_info(str(file_path))
                    template_info["file_path"] = str(file_path)
                    templates.append(template_info)
                    logger.info(f"Found template: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to analyze template {file_path}: {e}")
        
        return templates
    
    def _identify_fillable_templates(self, document_data: Dict[str, Any], templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify which templates can be filled with available data"""
        logger.info("Identifying fillable templates...")
        
        fillable_templates = []
        available_fields = set(document_data["merged_fields"].keys())
        
        for template in templates:
            template_name = template["name"].lower()
            
            # Determine template type based on filename
            template_type = self._classify_template_type(template_name)
            
            if template_type in self.form_requirements:
                requirements = self.form_requirements[template_type]
                required_fields = set(requirements["required"])
                optional_fields = set(requirements["optional"])
                
                # Check if required fields are available
                missing_required = required_fields - available_fields
                
                if not missing_required:
                    # Template can be filled
                    fillability_score = len(available_fields & (required_fields | optional_fields)) / len(required_fields | optional_fields)
                    
                    fillable_templates.append({
                        "template": template,
                        "type": template_type,
                        "fillability_score": fillability_score,
                        "missing_required": [],
                        "missing_optional": list(optional_fields - available_fields),
                        "can_fill": True
                    })
                    
                    logger.info(f"Template {template_name} can be filled (score: {fillability_score:.2f})")
                else:
                    # Template cannot be filled completely
                    fillable_templates.append({
                        "template": template,
                        "type": template_type,
                        "fillability_score": 0.0,
                        "missing_required": list(missing_required),
                        "missing_optional": list(set(requirements["optional"]) - available_fields),
                        "can_fill": False
                    })
                    
                    logger.warning(f"Template {template_name} missing required fields: {missing_required}")
            else:
                # Unknown template type - try to fill anyway
                fillable_templates.append({
                    "template": template,
                    "type": "unknown",
                    "fillability_score": 0.5,
                    "missing_required": [],
                    "missing_optional": [],
                    "can_fill": True
                })
        
        return fillable_templates
    
    def _classify_template_type(self, template_name: str) -> str:
        """Classify template type based on filename"""
        name_lower = template_name.lower()
        
        if "kyc" in name_lower:
            return "kyc_form"
        elif "hr" in name_lower or "onboarding" in name_lower or "employee" in name_lower:
            return "hr_onboarding"
        elif "tax" in name_lower or "income" in name_lower:
            return "tax_form"
        elif "bank" in name_lower or "account" in name_lower:
            return "bank_account"
        else:
            return "unknown"
    
    def _fill_templates(self, fillable_templates: List[Dict[str, Any]], document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fill the templates that can be completed"""
        logger.info("Filling templates...")
        
        filled_documents = []
        extracted_data = document_data["merged_fields"]
        
        for template_info in fillable_templates:
            if not template_info["can_fill"]:
                continue
            
            template = template_info["template"]
            template_path = template["file_path"]
            
            try:
                # Fill the template
                output_path = self.form_filler.fill_template(template_path, extracted_data)
                
                filled_documents.append({
                    "template_name": template["name"],
                    "template_type": template_info["type"],
                    "output_path": output_path,
                    "fields_filled": len(template_info["template"].get("fields", [])),
                    "fillability_score": template_info["fillability_score"]
                })
                
                logger.info(f"Successfully filled template: {template['name']}")
                
            except Exception as e:
                logger.error(f"Failed to fill template {template['name']}: {e}")
                filled_documents.append({
                    "template_name": template["name"],
                    "template_type": template_info["type"],
                    "output_path": None,
                    "error": str(e),
                    "fields_filled": 0
                })
        
        return filled_documents
    
    def _generate_missing_fields_report(self, fillable_templates: List[Dict[str, Any]], document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a report of missing fields across all templates"""
        logger.info("Generating missing fields report...")
        
        all_missing_required = set()
        all_missing_optional = set()
        template_gaps = []
        
        for template_info in fillable_templates:
            if template_info["missing_required"] or template_info["missing_optional"]:
                template_gaps.append({
                    "template_name": template_info["template"]["name"],
                    "type": template_info["type"],
                    "missing_required": template_info["missing_required"],
                    "missing_optional": template_info["missing_optional"],
                    "can_fill": template_info["can_fill"]
                })
                
                all_missing_required.update(template_info["missing_required"])
                all_missing_optional.update(template_info["missing_optional"])
        
        # Prioritize missing fields by frequency
        missing_field_priority = {}
        for field in all_missing_required:
            count = sum(1 for t in template_gaps if field in t["missing_required"])
            missing_field_priority[field] = count
        
        # Sort by priority (most frequently missing first)
        prioritized_missing = sorted(missing_field_priority.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "summary": {
                "total_templates": len(fillable_templates),
                "fully_fillable": len([t for t in fillable_templates if t["can_fill"]]),
                "partially_fillable": len([t for t in fillable_templates if not t["can_fill"]]),
                "total_missing_required": len(all_missing_required),
                "total_missing_optional": len(all_missing_optional)
            },
            "prioritized_missing_fields": prioritized_missing,
            "template_details": template_gaps,
            "suggestions": self._generate_field_suggestions(prioritized_missing)
        }
    
    def _generate_field_suggestions(self, missing_fields: List[Tuple[str, int]]) -> List[str]:
        """Generate suggestions for obtaining missing fields"""
        suggestions = []
        
        if not missing_fields:
            suggestions.append("All required fields are available!")
            return suggestions
        
        suggestions.append(f"Missing {len(missing_fields)} critical fields. Consider:")
        
        for field, count in missing_fields[:5]:  # Top 5
            if field in ["pan", "aadhar", "passport_number"]:
                suggestions.append(f"• Upload ID document for {field}")
            elif field in ["date_of_birth", "birth_date"]:
                suggestions.append(f"• Look for birth certificate or ID card with {field}")
            elif field in ["address", "street_address"]:
                suggestions.append(f"• Check utility bills or ID documents for {field}")
            elif field in ["salary", "income"]:
                suggestions.append(f"• Upload salary slip or income statement for {field}")
            else:
                suggestions.append(f"• Upload document containing {field}")
        
        return suggestions
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow (for async processing)"""
        # This would be implemented with a database or cache for production
        return {"status": "not_implemented"}
    
    def retry_failed_templates(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Retry filling templates that failed"""
        if workflow_result.get("status") != "completed":
            return workflow_result
        
        # Find failed templates and retry
        retried = []
        for doc in workflow_result.get("filled_documents", []):
            if doc.get("error"):
                # Retry logic here
                pass
        
        return workflow_result
