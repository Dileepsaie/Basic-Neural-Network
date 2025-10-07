"""Financial Document Data Model"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of financial documents"""
    QUARTERLY_REPORT = "quarterly_report"
    ANNUAL_REPORT = "annual_report"
    BUDGET = "budget"
    CONTRACT = "contract"
    INVOICE = "invoice"
    EXPENSE_REPORT = "expense_report"
    OTHER = "other"


class FinancialDocument(BaseModel):
    """Represents a financial document in the system"""
    
    document_id: str = Field(..., description="Unique identifier for the document")
    document_type: DocumentType = Field(..., description="Type of financial document")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Raw text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Financial data
    period_start: Optional[datetime] = Field(None, description="Start date of financial period")
    period_end: Optional[datetime] = Field(None, description="End date of financial period")
    department: Optional[str] = Field(None, description="Department or business unit")
    
    # Extracted structured data
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted tables")
    key_figures: Dict[str, float] = Field(default_factory=dict, description="Key financial figures")
    
    # Processing metadata
    retrieved_at: datetime = Field(default_factory=datetime.now, description="When document was retrieved")
    preprocessed: bool = Field(False, description="Whether document has been preprocessed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return self.model_dump()
