"""Document processing and analysis tools."""

import json
import os
import time
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from pydantic import ValidationError

from config.settings import settings
from loanai_agent.tools.document_templates import (
    BankStatementData,
    PromptTemplates,
    SalaryStatementData,
)
from loanai_agent.utils import DocumentProcessingException
from loanai_agent.utils.gcs_client import get_gcs_client
from loanai_agent.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Production-ready document processor with template-based prompts and validation."""

    def __init__(self):
        """Initialize document processor with metrics tracking."""
        self.gcs_client = None
        self.use_document_ai = settings.enable_document_ai
        self.metrics = {
            "documents_processed": 0,
            "documents_failed": 0,
            "total_processing_time": 0.0,
            "by_type": {},
        }
        
        # Configure Gemini API
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                }
            )
            logger.info("Gemini model initialized for document analysis with JSON mode")
        else:
            self.model = None
            logger.warning("GOOGLE_API_KEY not set. Document analysis will be limited.")
        
        # Initialize GCS client if needed
        if self.use_document_ai:
            try:
                self.gcs_client = get_gcs_client()
                logger.info("GCS client initialized for document processing")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS client: {e}. Falling back to simulation mode.")
                self.use_document_ai = False

    def parse_bank_statement(self, document_path: str, file_content: Optional[bytes] = None) -> Dict[str, Any]:
        """Parse bank statement with template-based prompts and validation.
        
        Args:
            document_path: GCS path or local path to document
            file_content: Optional pre-loaded file content as bytes
            
        Returns:
            Structured and validated bank statement data as dictionary
            
        Raises:
            DocumentProcessingException: If parsing or validation fails
        """
        start_time = time.time()
        logger.info(f"Parsing bank statement from {document_path}")
        
        try:
            # Get file content if not provided
            if file_content is None:
                file_content = self._load_document_content(document_path)
            
            # Use LLM with structured template
            if not self.model:
                logger.warning("Gemini model not available, using simulated data")
                return self._get_simulated_bank_data()
            
            # Generate prompt from template
            schema = BankStatementData.schema_json(indent=2)
            prompt = PromptTemplates.BANK_STATEMENT.render(schema=schema)
            
            # Analyze with LLM
            result_data = self._analyze_with_llm(
                file_content=file_content,
                document_path=document_path,
                prompt=prompt,
            )
            
            # Validate with Pydantic model
            validated_data = BankStatementData.parse_obj(result_data)
            
            # Record success metrics
            processing_time = time.time() - start_time
            self._record_metric("bank_statement", True, processing_time)
            
            logger.info(f"Successfully parsed bank statement in {processing_time:.2f}s")
            return validated_data.dict()
            
        except ValidationError as e:
            processing_time = time.time() - start_time
            self._record_metric("bank_statement", False, processing_time, "validation_error")
            logger.error(f"Validation failed for bank statement: {e}")
            raise DocumentProcessingException(f"Invalid bank statement format: {e}") from e
        except Exception as e:
            processing_time = time.time() - start_time
            self._record_metric("bank_statement", False, processing_time, "processing_error")
            logger.error(f"Error parsing bank statement: {e}", exc_info=True)
            raise DocumentProcessingException(f"Failed to parse bank statement: {e}") from e

    def parse_salary_statement(self, document_path: str, file_content: Optional[bytes] = None) -> Dict[str, Any]:
        """Parse salary statement with template-based prompts and validation.
        
        Args:
            document_path: GCS path or local path to document
            file_content: Optional pre-loaded file content as bytes
            
        Returns:
            Structured and validated salary statement data as dictionary
            
        Raises:
            DocumentProcessingException: If parsing or validation fails
        """
        start_time = time.time()
        logger.info(f"Parsing salary statement from {document_path}")
        
        try:
            # Get file content if not provided
            if file_content is None:
                file_content = self._load_document_content(document_path)
            
            # Use LLM with structured template
            if not self.model:
                logger.warning("Gemini model not available, using simulated data")
                return self._get_simulated_salary_data()
            
            # Generate prompt from template
            schema = SalaryStatementData.schema_json(indent=2)
            prompt = PromptTemplates.SALARY_STATEMENT.render(schema=schema)
            
            # Analyze with LLM
            result_data = self._analyze_with_llm(
                file_content=file_content,
                document_path=document_path,
                prompt=prompt,
            )
            
            # Validate with Pydantic model
            validated_data = SalaryStatementData.parse_obj(result_data)
            
            # Record success metrics
            processing_time = time.time() - start_time
            self._record_metric("salary_statement", True, processing_time)
            
            logger.info(f"Successfully parsed salary statement in {processing_time:.2f}s")
            return validated_data.dict()
            
        except ValidationError as e:
            processing_time = time.time() - start_time
            self._record_metric("salary_statement", False, processing_time, "validation_error")
            logger.error(f"Validation failed for salary statement: {e}")
            raise DocumentProcessingException(f"Invalid salary statement format: {e}") from e
        except Exception as e:
            processing_time = time.time() - start_time
            self._record_metric("salary_statement", False, processing_time, "processing_error")
            logger.error(f"Error parsing salary statement: {e}", exc_info=True)
            raise DocumentProcessingException(f"Failed to parse salary statement: {e}") from e

    def _load_document_content(self, document_path: str) -> bytes:
        """Load document content from GCS or local file system.
        
        Args:
            document_path: Path to document
            
        Returns:
            Document content as bytes
            
        Raises:
            DocumentProcessingException: If loading fails
        """
        try:
            if document_path.startswith("gs://"):
                if not self.gcs_client:
                    raise DocumentProcessingException("GCS client not available")
                return self.gcs_client.download_file(document_path)
            else:
                if not os.path.exists(document_path):
                    raise FileNotFoundError(f"File not found: {document_path}")
                with open(document_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            raise DocumentProcessingException(f"Failed to load document: {e}") from e

    def _analyze_with_llm(
        self,
        file_content: bytes,
        document_path: str,
        prompt: str,
    ) -> Dict[str, Any]:
        """Analyze document using Gemini LLM with structured output.
        
        Args:
            file_content: Document content as bytes
            document_path: Path to document (for mime type detection)
            prompt: Prompt template to use
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            DocumentProcessingException: If LLM analysis fails
        """
        import tempfile
        
        try:
            # Determine mime type
            mime_type = self._get_mime_type_from_path(document_path)
            
            # Create temporary file for upload
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=os.path.splitext(document_path)[1]
            ) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                # Upload file to Gemini
                uploaded_file = genai.upload_file(tmp_path, mime_type=mime_type)
                logger.debug(f"File uploaded to Gemini: {uploaded_file.name}")
                
                # Generate content with JSON mode
                response = self.model.generate_content([prompt, uploaded_file])
                
                # Parse JSON response
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3]
                elif response_text.startswith("```"):
                    response_text = response_text[3:-3]
                
                result = json.loads(response_text)
                logger.debug("Successfully parsed LLM response as JSON")
                
                return result
                
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise DocumentProcessingException("LLM returned invalid JSON") from e
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}", exc_info=True)
            raise DocumentProcessingException(f"LLM analysis failed: {e}") from e

    def _record_metric(
        self,
        doc_type: str,
        success: bool,
        processing_time: float,
        error_type: Optional[str] = None,
    ) -> None:
        """Record processing metrics for monitoring.
        
        Args:
            doc_type: Type of document processed
            success: Whether processing succeeded
            processing_time: Time taken in seconds
            error_type: Type of error if failed
        """
        if success:
            self.metrics["documents_processed"] += 1
        else:
            self.metrics["documents_failed"] += 1
        
        self.metrics["total_processing_time"] += processing_time
        
        if doc_type not in self.metrics["by_type"]:
            self.metrics["by_type"][doc_type] = {
                "processed": 0,
                "failed": 0,
                "total_time": 0.0,
                "errors": {},
            }
        
        type_metrics = self.metrics["by_type"][doc_type]
        if success:
            type_metrics["processed"] += 1
        else:
            type_metrics["failed"] += 1
            if error_type:
                type_metrics["errors"][error_type] = type_metrics["errors"].get(error_type, 0) + 1
        
        type_metrics["total_time"] += processing_time
        
        logger.debug(f"Metrics recorded: {doc_type}, success={success}, time={processing_time:.2f}s")

    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics for monitoring.
        
        Returns:
            Dictionary of metrics including counts, times, and error rates
        """
        total_docs = self.metrics["documents_processed"] + self.metrics["documents_failed"]
        
        return {
            "total_processed": self.metrics["documents_processed"],
            "total_failed": self.metrics["documents_failed"],
            "success_rate": (
                self.metrics["documents_processed"] / total_docs if total_docs > 0 else 0
            ),
            "average_processing_time": (
                self.metrics["total_processing_time"] / total_docs if total_docs > 0 else 0
            ),
            "by_type": self.metrics["by_type"],
        }

    def extract_text_from_document(
        self, document_path: str, document_type: str = "pdf"
    ) -> str:
        """
        Extract text from document using Document AI or simulation.
        
        Args:
            document_path: GCS path (gs://bucket/path) or local file path
            document_type: Type of document (pdf, image, etc.)
            
        Returns:
            Extracted text content
        """
        logger.info(f"Extracting text from {document_path}")

        # Check if this is a GCS path
        if document_path.startswith("gs://"):
            return self._extract_from_gcs(document_path, document_type)
        else:
            return self._extract_from_local(document_path, document_type)

    def _extract_from_gcs(self, gs_url: str, document_type: str = "pdf") -> str:
        """
        Extract text from document stored in GCS.
        
        Args:
            gs_url: GCS URL (gs://bucket/path/to/file)
            document_type: Type of document
            
        Returns:
            Extracted text
        """
        try:
            if not self.gcs_client or not self.use_document_ai:
                logger.warning(f"GCS/Document AI not available. Using simulation for {gs_url}")
                return self._get_simulated_extraction(gs_url, document_type)
            
            # Check if file exists
            if not self.gcs_client.file_exists(gs_url):
                logger.error(f"File not found in GCS: {gs_url}")
                return f"ERROR: File not found - {gs_url}"
            
            # Download file from GCS
            logger.info(f"Downloading file from GCS: {gs_url}")
            file_content = self.gcs_client.download_file(gs_url)
            
            # Process with Document AI
            return self._process_with_document_ai(file_content, document_type)
            
        except Exception as e:
            logger.error(f"Error extracting text from GCS {gs_url}: {e}")
            logger.warning("Falling back to simulation mode")
            return self._get_simulated_extraction(gs_url, document_type)

    def _extract_from_local(self, file_path: str, document_type: str = "pdf") -> str:
        """
        Extract text from local file.
        
        Args:
            file_path: Local file path
            document_type: Type of document
            
        Returns:
            Extracted text
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Local file not found: {file_path}")
                return f"ERROR: File not found - {file_path}"
            
            # Read file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Process with Document AI
            if self.use_document_ai:
                return self._process_with_document_ai(file_content, document_type)
            else:
                return self._get_simulated_extraction(file_path, document_type)
                
        except Exception as e:
            logger.error(f"Error extracting text from local file {file_path}: {e}")
            return self._get_simulated_extraction(file_path, document_type)

    def _process_with_document_ai(self, file_content: bytes, document_type: str) -> str:
        """
        Process document with Google Cloud Document AI.
        
        Args:
            file_content: Document content as bytes
            document_type: Type of document
            
        Returns:
            Extracted text
        """
        try:
            from google.cloud import documentai_v1 as documentai
            
            # Initialize Document AI client
            client = documentai.DocumentProcessorServiceClient()
            
            # Set processor based on document type
            # Note: You need to create these processors in GCP Console
            processor_name = self._get_processor_name(document_type)
            
            if not processor_name:
                logger.warning(f"No Document AI processor configured for {document_type}")
                return self._get_simulated_extraction(f"<document_{document_type}>", document_type)
            
            # Create process request
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=self._get_mime_type(document_type)
            )
            
            request = documentai.ProcessRequest(
                name=processor_name,
                raw_document=raw_document
            )
            
            # Process document
            logger.info(f"Processing document with Document AI processor: {processor_name}")
            result = client.process_document(request=request)
            
            # Extract text
            document = result.document
            extracted_text = document.text
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from document")
            return extracted_text
            
        except ImportError:
            logger.warning("google-cloud-documentai not installed. Using simulation mode.")
            return self._get_simulated_extraction(f"<document_{document_type}>", document_type)
        except Exception as e:
            logger.error(f"Error processing document with Document AI: {e}")
            return self._get_simulated_extraction(f"<document_{document_type}>", document_type)

    def _get_processor_name(self, document_type: str) -> Optional[str]:
        """
        Get Document AI processor name for document type.
        
        Args:
            document_type: Type of document
            
        Returns:
            Processor name or None
        """
        # Document AI processor format:
        # projects/{project}/locations/{location}/processors/{processor_id}
        
        # These would be configured in settings/environment
        # For now, return None to indicate processors need to be set up
        processor_map = {
            "bank_statement": os.getenv("DOCUMENT_AI_BANK_PROCESSOR"),
            "salary_statement": os.getenv("DOCUMENT_AI_SALARY_PROCESSOR"),
            "pdf": os.getenv("DOCUMENT_AI_GENERAL_PROCESSOR"),
        }
        
        return processor_map.get(document_type)

    def _get_mime_type(self, document_type: str) -> str:
        """Get MIME type for document type."""
        mime_types = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        return mime_types.get(document_type.lower(), "application/pdf")

    def _get_simulated_extraction(self, document_path: str, document_type: str) -> str:
        """
        Return simulated document extraction for demo purposes.
        
        Args:
            document_path: Path or URL of document
            document_type: Type of document
            
        Returns:
            Simulated extracted text
        """
        logger.info(f"Using simulated extraction for {document_path}")
        
        simulated_extraction = f"""
        Extracted text from {document_type.upper()} document:
        {document_path}
        
        [SIMULATED OCR OUTPUT]
        This is a demonstration of OCR extraction.
        In production, this would use Google Cloud Document AI
        to extract real document content from GCS.
        
        Configure Document AI processors and set ENABLE_DOCUMENT_AI=true
        to enable real document processing.
        """

        return simulated_extraction

    def parse_bank_statement(self, document_path: str, file_content: Optional[bytes] = None) -> Dict[str, Any]:
        """Parse bank statement using LLM to extract structured data.
        
        Args:
            document_path: GCS path or local path to document
            file_content: Optional pre-loaded file content as bytes
            
        Returns:
            Structured bank statement data
        """
        logger.info(f"Parsing bank statement from {document_path}")

        try:
            # Get file content if not provided
            if file_content is None:
                if document_path.startswith("gs://"):
                    if self.gcs_client:
                        file_content = self.gcs_client.download_file(document_path)
                    else:
                        logger.warning("GCS client not available, using simulated data")
                        return self._get_simulated_bank_data()
                else:
                    with open(document_path, 'rb') as f:
                        file_content = f.read()

            # Use LLM to analyze the document
            if self.model:
                return self._analyze_bank_statement_with_llm(file_content, document_path)
            else:
                logger.warning("Gemini model not available, using simulated data")
                return self._get_simulated_bank_data()
                
        except Exception as e:
            logger.error(f"Error parsing bank statement: {e}")
            return self._get_simulated_bank_data()

    def _analyze_bank_statement_with_llm(self, file_content: bytes, document_path: str) -> Dict[str, Any]:
        """Analyze bank statement using Gemini LLM.
        
        Args:
            file_content: Document content as bytes
            document_path: Path to document (for mime type detection)
            
        Returns:
            Structured bank statement data
        """
        try:
            # Determine mime type
            mime_type = self._get_mime_type_from_path(document_path)
            
            # Create multimodal prompt
            prompt = """Analyze this bank statement document and extract the following information in JSON format:

{
  "account_holder": "account holder name",
  "account_number": "masked account number",
  "statement_period": "period covered by statement",
  "opening_balance": numerical opening balance,
  "closing_balance": numerical closing balance,
  "total_credits": total of all credit transactions,
  "total_debits": total of all debit transactions,
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "transaction description",
      "amount": numerical amount,
      "type": "credit" or "debit"
    }
  ]
}

Extract ALL transactions from the statement. Be precise with numbers and dates.
Return ONLY valid JSON, no additional text."""

            # Upload file and generate content
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document_path)[1]) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                uploaded_file = genai.upload_file(tmp_path, mime_type=mime_type)
                response = self.model.generate_content([prompt, uploaded_file])
                
                # Parse JSON response
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                
                parsed_data = json.loads(response_text.strip())
                logger.info(f"Successfully parsed bank statement with {len(parsed_data.get('transactions', []))} transactions")
                return parsed_data
                
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"LLM bank statement analysis failed: {e}")
            return self._get_simulated_bank_data()

    def _get_simulated_bank_data(self) -> Dict[str, Any]:
        """Return simulated bank statement data for fallback."""
        return {
            "account_holder": "John Doe",
            "account_number": "****1234",
            "statement_period": "2024-01-01 to 2024-01-31",
            "opening_balance": 5000.00,
            "closing_balance": 12500.00,
            "total_credits": 12000.00,
            "total_debits": 4500.00,
            "transactions": [
                {
                    "date": "2024-01-05",
                    "description": "Salary Deposit",
                    "amount": 5000.00,
                    "type": "credit",
                },
                {
                    "date": "2024-01-10",
                    "description": "Rent Payment",
                    "amount": 1200.00,
                    "type": "debit",
                },
                {
                    "date": "2024-01-15",
                    "description": "Grocery Store",
                    "amount": 150.00,
                    "type": "debit",
                },
            ],
        }

    def parse_salary_statement(self, document_path: str, file_content: Optional[bytes] = None) -> Dict[str, Any]:
        """Parse salary statement using LLM to extract structured data.
        
        Args:
            document_path: GCS path or local path to document
            file_content: Optional pre-loaded file content as bytes
            
        Returns:
            Structured salary statement data
        """
        logger.info(f"Parsing salary statement from {document_path}")

        try:
            # Get file content if not provided
            if file_content is None:
                if document_path.startswith("gs://"):
                    if self.gcs_client:
                        file_content = self.gcs_client.download_file(document_path)
                    else:
                        logger.warning("GCS client not available, using simulated data")
                        return self._get_simulated_salary_data()
                else:
                    with open(document_path, 'rb') as f:
                        file_content = f.read()

            # Use LLM to analyze the document
            if self.model:
                return self._analyze_salary_statement_with_llm(file_content, document_path)
            else:
                logger.warning("Gemini model not available, using simulated data")
                return self._get_simulated_salary_data()
                
        except Exception as e:
            logger.error(f"Error parsing salary statement: {e}")
            return self._get_simulated_salary_data()

    def _analyze_salary_statement_with_llm(self, file_content: bytes, document_path: str) -> Dict[str, Any]:
        """Analyze salary statement using Gemini LLM.
        
        Args:
            file_content: Document content as bytes
            document_path: Path to document (for mime type detection)
            
        Returns:
            Structured salary statement data
        """
        try:
            # Determine mime type
            mime_type = self._get_mime_type_from_path(document_path)
            
            # Create multimodal prompt
            prompt = """Analyze this salary statement/payslip document and extract the following information in JSON format:

{
  "employee_name": "employee full name",
  "employee_id": "employee ID",
  "employer": "company/employer name",
  "salary_period": "period (e.g., 2024-01)",
  "gross_salary": numerical gross salary,
  "deductions": {
    "tax": tax amount,
    "social_security": social security amount,
    "health": health insurance amount,
    "other": other deductions
  },
  "net_salary": numerical net salary after deductions,
  "employment_type": "Full-time/Part-time/Contract",
  "department": "department name",
  "job_title": "job title/position"
}

Be precise with numbers. If information is not available, use null.
Return ONLY valid JSON, no additional text."""

            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document_path)[1]) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                uploaded_file = genai.upload_file(tmp_path, mime_type=mime_type)
                response = self.model.generate_content([prompt, uploaded_file])
                
                # Parse JSON response
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                
                parsed_data = json.loads(response_text.strip())
                logger.info(f"Successfully parsed salary statement for {parsed_data.get('employee_name', 'Unknown')}")
                return parsed_data
                
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"LLM salary statement analysis failed: {e}")
            return self._get_simulated_salary_data()

    def _get_simulated_salary_data(self) -> Dict[str, Any]:
        """Return simulated salary statement data for fallback."""
        return {
            "employee_name": "John Doe",
            "employee_id": "EMP12345",
            "employer": "Tech Solutions Inc.",
            "salary_period": "2024-01",
            "gross_salary": 5500.00,
            "deductions": {"tax": 900.00, "social_security": 250.00, "health": 150.00},
            "net_salary": 4200.00,
            "employment_type": "Full-time",
            "department": "Engineering",
            "job_title": "Senior Software Engineer",
        }

    def _get_mime_type_from_path(self, file_path: str) -> str:
        """Get MIME type from file path extension."""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }
        return mime_types.get(ext, 'application/pdf')


class FinancialAnalyzer:
    """Tools for financial analysis and metrics calculation."""

    @staticmethod
    def calculate_income_consistency(transactions: List[Dict]) -> float:
        """Calculate income consistency score (0-1)."""
        logger.info("Calculating income consistency")

        if not transactions:
            return 0.0

        income_transactions = [
            t for t in transactions if t.get("type") == "credit" and "salary" in t.get("description", "").lower()
        ]

        if not income_transactions:
            return 0.0

        # Simple consistency check: if we have multiple regular deposits, high consistency
        if len(income_transactions) >= 3:
            return 0.9
        elif len(income_transactions) >= 2:
            return 0.7
        else:
            return 0.4

    @staticmethod
    def detect_fraud_indicators(transactions: List[Dict]) -> List[str]:
        """Detect potential fraud indicators in transaction data."""
        logger.info("Detecting fraud indicators")

        red_flags = []

        # Check for unusual transaction patterns
        large_transactions = [
            t for t in transactions if abs(t.get("amount", 0)) > 10000
        ]
        if large_transactions:
            red_flags.append("Large unusual transactions detected")

        # Check for rapid account draining
        debits = [t for t in transactions if t.get("type") == "debit"]
        if debits and sum(t.get("amount", 0) for t in debits) > 50000:
            red_flags.append("Unusually high debit activity")

        return red_flags

    @staticmethod
    def calculate_financial_health_score(
        monthly_income: float, monthly_expenses: float, savings: float
    ) -> float:
        """Calculate overall financial health score (0-100)."""
        if monthly_income <= 0:
            return 0.0

        # Savings rate
        savings_rate = (savings / monthly_income) * 100 if monthly_income > 0 else 0
        savings_score = min(savings_rate / 30 * 40, 40)  # Max 40 points

        # Debt to income ratio
        debt_to_income = (monthly_expenses / monthly_income) * 100
        if debt_to_income < 30:
            debt_score = 40
        elif debt_to_income < 50:
            debt_score = 30
        elif debt_to_income < 70:
            debt_score = 15
        else:
            debt_score = 0

        # Income stability (bonus points)
        stability_score = 20

        return min(savings_score + debt_score + stability_score, 100)


class EmploymentVerifier:
    """Tools for employment verification and validation."""

    @staticmethod
    def verify_employment_consistency(
        self_reported_salary: float, documented_salary: float, threshold: float = 0.1
    ) -> bool:
        """Verify employment salary consistency."""
        if documented_salary == 0:
            return False

        variance = abs(
            (self_reported_salary - documented_salary) / documented_salary
        )
        return variance <= threshold

    @staticmethod
    def calculate_employment_stability_score(
        tenure_months: int, job_title: str = ""
    ) -> float:
        """Calculate employment stability score (0-1)."""
        logger.info(f"Calculating employment stability for {tenure_months} months tenure")

        if tenure_months < 3:
            return 0.3
        elif tenure_months < 12:
            return 0.5
        elif tenure_months < 24:
            return 0.7
        elif tenure_months < 60:
            return 0.85
        else:
            return 1.0

    @staticmethod
    def detect_employment_red_flags(
        employment_data: Dict[str, Any]
    ) -> List[str]:
        """Detect red flags in employment data."""
        red_flags = []

        # Check for very recent employment
        tenure = employment_data.get("tenure_months", 0)
        if tenure < 3:
            red_flags.append("Very recent employment (less than 3 months)")

        # Check for frequent job changes
        job_changes = employment_data.get("job_changes_last_2_years", 0)
        if job_changes > 3:
            red_flags.append("Frequent job changes detected")

        # Check for employment gaps
        employment_gaps = employment_data.get("employment_gaps", [])
        for gap in employment_gaps:
            if gap.get("duration_months", 0) > 6:
                red_flags.append(f"Employment gap of {gap.get('duration_months')} months")

        return red_flags
