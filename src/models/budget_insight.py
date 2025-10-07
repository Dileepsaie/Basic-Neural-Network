"""Budget Insight Data Model"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class VarianceType(str, Enum):
    """Type of budget variance"""
    OVERSPEND = "overspend"
    UNDERSPEND = "underspend"
    ON_TARGET = "on_target"


class SeverityLevel(str, Enum):
    """Severity level of insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BudgetVariance(BaseModel):
    """Represents a budget variance"""
    
    category: str = Field(..., description="Budget category (e.g., department, project)")
    budgeted_amount: float = Field(..., description="Budgeted/forecasted amount")
    actual_amount: float = Field(..., description="Actual amount spent")
    variance_amount: float = Field(..., description="Difference (actual - budgeted)")
    variance_percentage: float = Field(..., description="Variance as percentage")
    variance_type: VarianceType = Field(..., description="Type of variance")
    severity: SeverityLevel = Field(..., description="Severity of the variance")


class Anomaly(BaseModel):
    """Represents a detected anomaly in financial data"""
    
    anomaly_type: str = Field(..., description="Type of anomaly")
    description: str = Field(..., description="Description of the anomaly")
    affected_category: str = Field(..., description="Category affected by anomaly")
    severity: SeverityLevel = Field(..., description="Severity level")
    detected_value: float = Field(..., description="The anomalous value")
    expected_range: Optional[str] = Field(None, description="Expected value range")
    recommendation: Optional[str] = Field(None, description="Recommended action")


class BudgetInsight(BaseModel):
    """Represents budget insights and analysis"""
    
    insight_id: str = Field(..., description="Unique identifier for the insight")
    summary_id: str = Field(..., description="Related financial summary ID")
    
    # Overall health
    budget_health_score: float = Field(..., description="Overall budget health score (0-100)")
    health_status: str = Field(..., description="Overall health status description")
    
    # Variances
    variances: List[BudgetVariance] = Field(default_factory=list, description="Budget variances")
    total_budget: float = Field(..., description="Total budgeted amount")
    total_actual: float = Field(..., description="Total actual spending")
    total_variance: float = Field(..., description="Total variance amount")
    total_variance_percentage: float = Field(..., description="Total variance percentage")
    
    # Anomalies
    anomalies: List[Anomaly] = Field(default_factory=list, description="Detected anomalies")
    
    # Insights and recommendations
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    
    # Department/category breakdown
    department_insights: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Per-department insights"
    )
    
    # Metadata
    period_start: Optional[datetime] = Field(None, description="Start of analysis period")
    period_end: Optional[datetime] = Field(None, description="End of analysis period")
    generated_at: datetime = Field(default_factory=datetime.now, description="When insight was generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return self.model_dump()
    
    def get_critical_issues(self) -> List[str]:
        """Get list of critical issues that need immediate attention"""
        critical_issues = []
        
        # Check for critical variances
        for variance in self.variances:
            if variance.severity == SeverityLevel.CRITICAL:
                critical_issues.append(
                    f"{variance.category}: {variance.variance_type.value} by "
                    f"{variance.variance_percentage:.1f}% (${variance.variance_amount:,.2f})"
                )
        
        # Check for critical anomalies
        for anomaly in self.anomalies:
            if anomaly.severity == SeverityLevel.CRITICAL:
                critical_issues.append(
                    f"{anomaly.anomaly_type} in {anomaly.affected_category}: {anomaly.description}"
                )
        
        return critical_issues
