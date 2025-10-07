"""Budget Insights Workflow"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics

from .base import BaseWorkflow
from ..models import (
    FinancialSummary, 
    BudgetInsight, 
    BudgetVariance, 
    Anomaly,
    VarianceType, 
    SeverityLevel
)


class BudgetInsightsWorkflow(BaseWorkflow):
    """
    Workflow for generating budget insights and analysis
    
    Steps:
    1. Compare actual vs. forecasted/budgeted spend
    2. Identify anomalies, overspending, or underutilization
    3. Generate actionable insights and recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.variance_threshold = config.get('variance_threshold', 0.10)  # 10% default
        self.anomaly_detection_enabled = config.get('anomaly_detection', True)
        self.critical_threshold = 0.20  # 20% variance is critical
        self.high_threshold = 0.15  # 15% variance is high
    
    def execute(self, summary: FinancialSummary, budget_data: Dict[str, Any]) -> BudgetInsight:
        """
        Execute budget insights workflow
        
        Args:
            summary: FinancialSummary with actual financial data
            budget_data: Dictionary containing budgeted/forecasted amounts:
                - total_budget: Total budgeted amount
                - department_budgets: Dict of department -> budgeted amount
                - category_budgets: Dict of category -> budgeted amount
                
        Returns:
            BudgetInsight object with analysis and recommendations
        """
        self.logger.info("Starting budget insights workflow")
        
        if not self.validate_input((summary, budget_data)):
            raise ValueError("Invalid input data for budget insights")
        
        # Step 1: Calculate variances between actual and budgeted amounts
        variances = self._calculate_variances(summary, budget_data)
        self.logger.info(f"Calculated {len(variances)} budget variances")
        
        # Step 2: Detect anomalies in spending patterns
        anomalies = []
        if self.anomaly_detection_enabled:
            anomalies = self._detect_anomalies(summary, budget_data, variances)
            self.logger.info(f"Detected {len(anomalies)} anomalies")
        
        # Step 3: Calculate overall budget health
        health_score, health_status = self._calculate_budget_health(variances, anomalies)
        
        # Step 4: Generate key findings
        key_findings = self._generate_key_findings(variances, anomalies, summary)
        
        # Step 5: Generate recommendations
        recommendations = self._generate_recommendations(variances, anomalies, summary)
        
        # Step 6: Create department-level insights
        department_insights = self._create_department_insights(summary, budget_data, variances)
        
        # Step 7: Calculate totals
        total_budget = budget_data.get('total_budget', 0)
        total_actual = summary.metrics.expenses or 0
        total_variance = total_actual - total_budget
        total_variance_pct = (total_variance / total_budget * 100) if total_budget != 0 else 0
        
        # Create BudgetInsight object
        insight = BudgetInsight(
            insight_id=self._generate_insight_id(summary),
            summary_id=summary.summary_id,
            budget_health_score=health_score,
            health_status=health_status,
            variances=variances,
            total_budget=total_budget,
            total_actual=total_actual,
            total_variance=total_variance,
            total_variance_percentage=total_variance_pct,
            anomalies=anomalies,
            key_findings=key_findings,
            recommendations=recommendations,
            department_insights=department_insights,
            period_start=summary.period_start,
            period_end=summary.period_end,
            generated_at=datetime.now()
        )
        
        self.logger.info(f"Budget insights generated with health score: {health_score:.1f}")
        return insight
    
    def _calculate_variances(
        self, 
        summary: FinancialSummary, 
        budget_data: Dict[str, Any]
    ) -> List[BudgetVariance]:
        """
        Calculate variances between actual and budgeted amounts
        
        Args:
            summary: Financial summary with actual data
            budget_data: Budget/forecast data
            
        Returns:
            List of BudgetVariance objects
        """
        variances = []
        
        # Overall budget variance
        total_budget = budget_data.get('total_budget', 0)
        total_actual = summary.metrics.expenses or 0
        
        if total_budget > 0:
            variance = self._create_variance(
                category="Overall Budget",
                budgeted=total_budget,
                actual=total_actual
            )
            variances.append(variance)
        
        # Department-level variances
        department_budgets = budget_data.get('department_budgets', {})
        if summary.department and summary.department in department_budgets:
            budgeted = department_budgets[summary.department]
            variance = self._create_variance(
                category=f"Department: {summary.department}",
                budgeted=budgeted,
                actual=total_actual
            )
            variances.append(variance)
        
        # Category-level variances
        category_budgets = budget_data.get('category_budgets', {})
        for category, budgeted_amount in category_budgets.items():
            # Try to find actual amount for this category
            actual_amount = summary.metrics.custom_metrics.get(category, 0)
            
            if budgeted_amount > 0:
                variance = self._create_variance(
                    category=category,
                    budgeted=budgeted_amount,
                    actual=actual_amount
                )
                variances.append(variance)
        
        return variances
    
    def _create_variance(
        self, 
        category: str, 
        budgeted: float, 
        actual: float
    ) -> BudgetVariance:
        """
        Create a BudgetVariance object
        
        Args:
            category: Category name
            budgeted: Budgeted amount
            actual: Actual amount
            
        Returns:
            BudgetVariance object
        """
        variance_amount = actual - budgeted
        variance_pct = (variance_amount / budgeted * 100) if budgeted != 0 else 0
        
        # Determine variance type
        if abs(variance_pct) <= self.variance_threshold * 100:
            variance_type = VarianceType.ON_TARGET
        elif variance_amount > 0:
            variance_type = VarianceType.OVERSPEND
        else:
            variance_type = VarianceType.UNDERSPEND
        
        # Determine severity
        abs_variance_pct = abs(variance_pct)
        if abs_variance_pct >= self.critical_threshold * 100:
            severity = SeverityLevel.CRITICAL
        elif abs_variance_pct >= self.high_threshold * 100:
            severity = SeverityLevel.HIGH
        elif abs_variance_pct >= self.variance_threshold * 100:
            severity = SeverityLevel.MEDIUM
        else:
            severity = SeverityLevel.LOW
        
        return BudgetVariance(
            category=category,
            budgeted_amount=budgeted,
            actual_amount=actual,
            variance_amount=variance_amount,
            variance_percentage=variance_pct,
            variance_type=variance_type,
            severity=severity
        )
    
    def _detect_anomalies(
        self,
        summary: FinancialSummary,
        budget_data: Dict[str, Any],
        variances: List[BudgetVariance]
    ) -> List[Anomaly]:
        """
        Detect anomalies in spending patterns
        
        Args:
            summary: Financial summary
            budget_data: Budget data
            variances: Calculated variances
            
        Returns:
            List of Anomaly objects
        """
        anomalies = []
        
        # Anomaly 1: Sudden spike in expenses
        if summary.metrics.expense_growth and summary.metrics.expense_growth > 50:
            anomaly = Anomaly(
                anomaly_type="Expense Spike",
                description=f"Expenses increased by {summary.metrics.expense_growth:.1f}% compared to previous period",
                affected_category="Overall Expenses",
                severity=SeverityLevel.HIGH,
                detected_value=summary.metrics.expenses or 0,
                expected_range="Based on historical trends",
                recommendation="Investigate cause of expense increase and implement cost controls"
            )
            anomalies.append(anomaly)
        
        # Anomaly 2: Negative net income with expected profitability
        if summary.metrics.net_income and summary.metrics.net_income < 0:
            if budget_data.get('expected_profit', 0) > 0:
                anomaly = Anomaly(
                    anomaly_type="Unexpected Loss",
                    description="Negative net income despite budgeted profitability",
                    affected_category="Net Income",
                    severity=SeverityLevel.CRITICAL,
                    detected_value=summary.metrics.net_income,
                    expected_range=f"Expected profit: ${budget_data.get('expected_profit', 0):,.2f}",
                    recommendation="Review revenue streams and major expense categories immediately"
                )
                anomalies.append(anomaly)
        
        # Anomaly 3: Significant variances
        for variance in variances:
            if variance.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                if variance.variance_type == VarianceType.OVERSPEND:
                    anomaly = Anomaly(
                        anomaly_type="Budget Overrun",
                        description=f"{variance.category} exceeded budget by {abs(variance.variance_percentage):.1f}%",
                        affected_category=variance.category,
                        severity=variance.severity,
                        detected_value=variance.actual_amount,
                        expected_range=f"Budgeted: ${variance.budgeted_amount:,.2f}",
                        recommendation=f"Review spending controls for {variance.category} and adjust forecasts"
                    )
                    anomalies.append(anomaly)
                elif variance.variance_type == VarianceType.UNDERSPEND:
                    # Significant underspend might indicate missed opportunities
                    if abs(variance.variance_percentage) > 30:
                        anomaly = Anomaly(
                            anomaly_type="Budget Underutilization",
                            description=f"{variance.category} utilized only {(variance.actual_amount/variance.budgeted_amount*100):.1f}% of budget",
                            affected_category=variance.category,
                            severity=SeverityLevel.MEDIUM,
                            detected_value=variance.actual_amount,
                            expected_range=f"Budgeted: ${variance.budgeted_amount:,.2f}",
                            recommendation=f"Assess if resources for {variance.category} are being effectively deployed"
                        )
                        anomalies.append(anomaly)
        
        # Anomaly 4: Low gross margin
        if summary.metrics.gross_margin and summary.metrics.gross_margin < 15:
            anomaly = Anomaly(
                anomaly_type="Low Profitability",
                description=f"Gross margin of {summary.metrics.gross_margin:.1f}% is below healthy threshold",
                affected_category="Profitability",
                severity=SeverityLevel.HIGH,
                detected_value=summary.metrics.gross_margin,
                expected_range="Target: >20%",
                recommendation="Review pricing strategy and cost structure to improve margins"
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_budget_health(
        self,
        variances: List[BudgetVariance],
        anomalies: List[Anomaly]
    ) -> tuple[float, str]:
        """
        Calculate overall budget health score (0-100)
        
        Args:
            variances: List of budget variances
            anomalies: List of detected anomalies
            
        Returns:
            Tuple of (health_score, health_status)
        """
        # Start with perfect score
        score = 100.0
        
        # Deduct points for variances
        for variance in variances:
            if variance.severity == SeverityLevel.CRITICAL:
                score -= 15
            elif variance.severity == SeverityLevel.HIGH:
                score -= 10
            elif variance.severity == SeverityLevel.MEDIUM:
                score -= 5
            elif variance.severity == SeverityLevel.LOW:
                score -= 2
        
        # Deduct points for anomalies
        for anomaly in anomalies:
            if anomaly.severity == SeverityLevel.CRITICAL:
                score -= 10
            elif anomaly.severity == SeverityLevel.HIGH:
                score -= 7
            elif anomaly.severity == SeverityLevel.MEDIUM:
                score -= 4
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        # Determine health status
        if score >= 80:
            status = "Excellent - Budget is well-managed with minimal variances"
        elif score >= 60:
            status = "Good - Budget is generally on track with some areas needing attention"
        elif score >= 40:
            status = "Fair - Significant variances require management action"
        elif score >= 20:
            status = "Poor - Critical budget issues need immediate attention"
        else:
            status = "Critical - Severe budget crisis requiring urgent intervention"
        
        return score, status
    
    def _generate_key_findings(
        self,
        variances: List[BudgetVariance],
        anomalies: List[Anomaly],
        summary: FinancialSummary
    ) -> List[str]:
        """Generate key findings from analysis"""
        findings = []
        
        # Overall variance finding
        overall_variance = next(
            (v for v in variances if v.category == "Overall Budget"),
            None
        )
        
        if overall_variance:
            if overall_variance.variance_type == VarianceType.OVERSPEND:
                findings.append(
                    f"Overall budget exceeded by ${abs(overall_variance.variance_amount):,.2f} "
                    f"({abs(overall_variance.variance_percentage):.1f}%)"
                )
            elif overall_variance.variance_type == VarianceType.UNDERSPEND:
                findings.append(
                    f"Overall spending is ${abs(overall_variance.variance_amount):,.2f} "
                    f"under budget ({abs(overall_variance.variance_percentage):.1f}%)"
                )
            else:
                findings.append(
                    f"Overall budget is on target with variance of only "
                    f"{abs(overall_variance.variance_percentage):.1f}%"
                )
        
        # Critical variance findings
        critical_variances = [v for v in variances if v.severity == SeverityLevel.CRITICAL]
        if critical_variances:
            findings.append(
                f"{len(critical_variances)} critical budget variance(s) identified requiring immediate action"
            )
        
        # Anomaly findings
        critical_anomalies = [a for a in anomalies if a.severity == SeverityLevel.CRITICAL]
        if critical_anomalies:
            for anomaly in critical_anomalies[:3]:  # Top 3
                findings.append(f"{anomaly.anomaly_type}: {anomaly.description}")
        
        # Performance insights
        if summary.metrics.gross_margin:
            findings.append(
                f"Current gross margin of {summary.metrics.gross_margin:.1f}% "
                f"{'indicates healthy profitability' if summary.metrics.gross_margin > 25 else 'suggests margin pressure'}"
            )
        
        return findings
    
    def _generate_recommendations(
        self,
        variances: List[BudgetVariance],
        anomalies: List[Anomaly],
        summary: FinancialSummary
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommendations for critical issues
        critical_items = (
            [v for v in variances if v.severity == SeverityLevel.CRITICAL] +
            [a for a in anomalies if a.severity == SeverityLevel.CRITICAL]
        )
        
        if critical_items:
            recommendations.append(
                "Schedule immediate review meeting with department heads to address critical variances"
            )
        
        # Overspend recommendations
        overspend_variances = [
            v for v in variances 
            if v.variance_type == VarianceType.OVERSPEND and v.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        ]
        
        if overspend_variances:
            categories = [v.category for v in overspend_variances]
            recommendations.append(
                f"Implement spending controls for: {', '.join(categories)}"
            )
            recommendations.append(
                "Review and update budget forecasts based on actual spending patterns"
            )
        
        # Anomaly-specific recommendations
        for anomaly in anomalies:
            if anomaly.recommendation and anomaly.recommendation not in recommendations:
                recommendations.append(anomaly.recommendation)
        
        # Growth recommendations
        if summary.metrics.revenue_growth and summary.metrics.revenue_growth > 10:
            recommendations.append(
                "Leverage positive revenue momentum to invest in growth initiatives"
            )
        
        # Efficiency recommendations
        if summary.metrics.expense_growth and summary.metrics.revenue_growth:
            if summary.metrics.expense_growth > summary.metrics.revenue_growth:
                recommendations.append(
                    "Focus on operational efficiency as expenses are outpacing revenue growth"
                )
        
        # Generic best practices
        recommendations.append(
            "Establish monthly budget review cadence to catch variances early"
        )
        recommendations.append(
            "Implement automated alerts for spending that exceeds threshold percentages"
        )
        
        return recommendations[:10]  # Limit to top 10
    
    def _create_department_insights(
        self,
        summary: FinancialSummary,
        budget_data: Dict[str, Any],
        variances: List[BudgetVariance]
    ) -> Dict[str, Dict[str, Any]]:
        """Create per-department insights"""
        department_insights = {}
        
        department_budgets = budget_data.get('department_budgets', {})
        
        for dept, budgeted_amount in department_budgets.items():
            # Find variance for this department
            dept_variance = next(
                (v for v in variances if dept in v.category),
                None
            )
            
            insight = {
                'budgeted': budgeted_amount,
                'actual': dept_variance.actual_amount if dept_variance else 0,
                'variance': dept_variance.variance_amount if dept_variance else 0,
                'variance_percentage': dept_variance.variance_percentage if dept_variance else 0,
                'status': dept_variance.variance_type.value if dept_variance else 'unknown',
                'severity': dept_variance.severity.value if dept_variance else 'info'
            }
            
            department_insights[dept] = insight
        
        return department_insights
    
    def _generate_insight_id(self, summary: FinancialSummary) -> str:
        """Generate unique insight ID"""
        return f"insight_{summary.summary_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        if not isinstance(input_data, tuple) or len(input_data) != 2:
            return False
        
        summary, budget_data = input_data
        
        if not isinstance(budget_data, dict):
            return False
        
        if 'total_budget' not in budget_data:
            self.logger.warning("No total_budget in budget_data")
            return False
        
        return True
