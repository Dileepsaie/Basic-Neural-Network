"""Financial Summary Data Model"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class FinancialMetrics(BaseModel):
    """Key financial metrics extracted from documents"""
    
    revenue: Optional[float] = Field(None, description="Total revenue")
    expenses: Optional[float] = Field(None, description="Total expenses")
    net_income: Optional[float] = Field(None, description="Net income/profit")
    gross_margin: Optional[float] = Field(None, description="Gross margin percentage")
    operating_income: Optional[float] = Field(None, description="Operating income")
    
    # Growth metrics
    revenue_growth: Optional[float] = Field(None, description="Revenue growth rate")
    expense_growth: Optional[float] = Field(None, description="Expense growth rate")
    
    # Additional metrics
    custom_metrics: Dict[str, float] = Field(default_factory=dict, description="Custom metrics")


class FinancialSummary(BaseModel):
    """Represents a standardized financial summary"""
    
    summary_id: str = Field(..., description="Unique identifier for the summary")
    source_document_ids: List[str] = Field(..., description="IDs of source documents")
    
    # Summary content
    executive_summary: str = Field(..., description="High-level executive summary")
    key_insights: List[str] = Field(default_factory=list, description="Key insights and findings")
    
    # Financial metrics
    metrics: FinancialMetrics = Field(..., description="Extracted financial metrics")
    
    # Period information
    period_start: Optional[datetime] = Field(None, description="Start of reporting period")
    period_end: Optional[datetime] = Field(None, description="End of reporting period")
    department: Optional[str] = Field(None, description="Department or business unit")
    
    # Trends and analysis
    trends: List[str] = Field(default_factory=list, description="Identified trends")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    opportunities: List[str] = Field(default_factory=list, description="Identified opportunities")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now, description="When summary was generated")
    confidence_score: Optional[float] = Field(None, description="Confidence in summary accuracy (0-1)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return self.model_dump()
