"""
Technical due diligence module.

This module analyzes the technical capabilities and codebase of a company, including:
- Code quality and maintainability
- Architecture and scalability
- Test coverage and CI/CD practices
- Technical debt assessment
"""

import os
import json
from typing import Dict, List, Any, Optional

import httpx

from .base import DDModule, Finding


class TechDD(DDModule):
    """
    Technical due diligence module for evaluating a company's technical capabilities.
    """
    
    def __init__(self):
        """Initialize the technical due diligence module."""
        super().__init__("tech")
    
    async def run(self, company_id: str) -> Dict[str, Any]:
        """
        Run technical due diligence for the specified company.
        
        Args:
            company_id: ID of the company to analyze
            
        Returns:
            Dictionary containing the technical due diligence results
        """
        try:
            # Get company technical data from data room
            tech_data = await self._get_company_tech_data(company_id)
            if not tech_data:
                return {
                    "error": f"No technical data found for company {company_id}"
                }
            
            # Analyze code quality
            code_quality_findings = self._analyze_code_quality(tech_data)
            
            # Analyze architecture
            architecture_findings = self._analyze_architecture(tech_data)
            
            # Analyze testing practices
            testing_findings = self._analyze_testing(tech_data)
            
            # Analyze technical debt
            tech_debt_findings = self._analyze_tech_debt(tech_data)
            
            # Combine all findings
            all_findings = code_quality_findings + architecture_findings + testing_findings + tech_debt_findings
            
            # Calculate overall score
            score = self._calculate_score(all_findings)
            
            # Determine overall status
            status = self._determine_status(score)
            
            # Generate summary
            summary = self._generate_summary(score, all_findings)
            
            # Return formatted results
            return self.format_result(
                score=score,
                status=status,
                summary=summary,
                findings=all_findings,
                details={"company_id": company_id, "tech_data": tech_data}
            )
        except Exception as e:
            return {
                "error": f"Technical due diligence failed: {str(e)}"
            }
    
    async def _get_company_tech_data(self, company_id: str) -> Dict[str, Any]:
        """
        Get technical data for the specified company from the data room.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Dictionary containing the company's technical data
        """
        datarooms_dir = os.environ.get("DATAROOMS_DIR", "data/datarooms")
        
        # Try to load from file system first
        try:
            file_path = os.path.join(datarooms_dir, company_id, "company_data.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    return data.get("tech", {})
        except Exception as e:
            print(f"Error loading technical data from file system: {str(e)}")
        
        # Fall back to API if file system access fails
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8000/api/dataroom/{company_id}"
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("tech", {})
        except Exception as e:
            print(f"Error loading technical data from API: {str(e)}")
        
        return {}
    
    def _analyze_code_quality(self, tech_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze code quality metrics.
        
        Args:
            tech_data: Dictionary containing the company's technical data
            
        Returns:
            List of findings related to code quality
        """
        findings = []
        
        # Extract relevant metrics
        static_analysis = tech_data.get("static_analysis", {})
        linting_issues = static_analysis.get("linting_issues", 0)
        code_complexity = static_analysis.get("avg_complexity", 0)
        duplicated_code = static_analysis.get("duplicated_code_percentage", 0)
        
        # Check linting issues
        if linting_issues > 0:
            if linting_issues > 1000:
                findings.append(Finding(
                    title="High Number of Linting Issues",
                    description=f"Found {linting_issues} linting issues, indicating poor code quality and lack of adherence to coding standards.",
                    severity="critical",
                    evidence={"linting_issues": linting_issues},
                    recommendations=[
                        "Implement strict linting in CI/CD pipeline",
                        "Establish a code review process",
                        "Set up pre-commit hooks to enforce standards"
                    ]
                ))
            elif linting_issues > 500:
                findings.append(Finding(
                    title="Moderate Number of Linting Issues",
                    description=f"Found {linting_issues} linting issues, suggesting room for improvement in code quality.",
                    severity="warning",
                    evidence={"linting_issues": linting_issues},
                    recommendations=[
                        "Address high-priority linting issues first",
                        "Add linting to development workflow"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Minor Linting Issues",
                    description=f"Found {linting_issues} linting issues, which is relatively manageable.",
                    severity="info",
                    evidence={"linting_issues": linting_issues}
                ))
        
        # Check code complexity
        if code_complexity > 0:
            if code_complexity > 25:
                findings.append(Finding(
                    title="High Code Complexity",
                    description=f"Average code complexity is {code_complexity:.1f}, indicating difficult-to-maintain code.",
                    severity="critical",
                    evidence={"avg_complexity": code_complexity},
                    recommendations=[
                        "Refactor complex functions into smaller, more manageable pieces",
                        "Implement complexity limits in CI pipeline",
                        "Document complex algorithms thoroughly"
                    ]
                ))
            elif code_complexity > 15:
                findings.append(Finding(
                    title="Moderate Code Complexity",
                    description=f"Average code complexity is {code_complexity:.1f}, which could lead to maintenance issues.",
                    severity="warning",
                    evidence={"avg_complexity": code_complexity},
                    recommendations=[
                        "Review most complex functions for potential refactoring",
                        "Set complexity guidelines for new code"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Manageable Code Complexity",
                    description=f"Average code complexity is {code_complexity:.1f}, which is within acceptable limits.",
                    severity="info",
                    evidence={"avg_complexity": code_complexity}
                ))
        
        # Check duplicated code
        if duplicated_code > 0:
            if duplicated_code > 0.2:  # More than 20% duplicated code
                findings.append(Finding(
                    title="High Code Duplication",
                    description=f"Code duplication is at {duplicated_code:.1%}, indicating poor code reuse and abstraction.",
                    severity="critical",
                    evidence={"duplicated_code_percentage": duplicated_code},
                    recommendations=[
                        "Identify and extract common functionality into shared components",
                        "Implement DRY (Don't Repeat Yourself) principles",
                        "Use code duplication detection tools in CI pipeline"
                    ]
                ))
            elif duplicated_code > 0.1:  # More than 10% duplicated code
                findings.append(Finding(
                    title="Moderate Code Duplication",
                    description=f"Code duplication is at {duplicated_code:.1%}, suggesting opportunities for better code reuse.",
                    severity="warning",
                    evidence={"duplicated_code_percentage": duplicated_code},
                    recommendations=[
                        "Review largest duplicated blocks for refactoring opportunities",
                        "Establish guidelines for code reuse"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Low Code Duplication",
                    description=f"Code duplication is at {duplicated_code:.1%}, which is within acceptable limits.",
                    severity="info",
                    evidence={"duplicated_code_percentage": duplicated_code}
                ))
        
        return findings
    
    def _analyze_architecture(self, tech_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze architecture and scalability.
        
        Args:
            tech_data: Dictionary containing the company's technical data
            
        Returns:
            List of findings related to architecture and scalability
        """
        findings = []
        
        # Extract relevant metrics
        architecture = tech_data.get("architecture", {})
        monolithic = architecture.get("is_monolithic", False)
        microservices = architecture.get("uses_microservices", False)
        scalability_score = architecture.get("scalability_score", 0)
        cloud_native = architecture.get("is_cloud_native", False)
        
        # Check architecture type
        if monolithic and not microservices:
            findings.append(Finding(
                title="Monolithic Architecture",
                description="The system uses a monolithic architecture, which may limit scalability and deployment flexibility.",
                severity="warning",
                evidence={"is_monolithic": monolithic, "uses_microservices": microservices},
                recommendations=[
                    "Consider gradually migrating to microservices for critical components",
                    "Modularize the monolith internally to prepare for future decomposition",
                    "Implement clear boundaries between system components"
                ]
            ))
        elif microservices:
            # Microservices can be good, but also introduce complexity
            findings.append(Finding(
                title="Microservices Architecture",
                description="The system uses a microservices architecture, which can provide good scalability but also introduces operational complexity.",
                severity="info",
                evidence={"uses_microservices": microservices},
                recommendations=[
                    "Ensure proper service discovery and communication patterns",
                    "Implement robust monitoring and observability",
                    "Document service boundaries and responsibilities"
                ]
            ))
        
        # Check scalability
        if scalability_score < 0.5:
            findings.append(Finding(
                title="Scalability Concerns",
                description=f"The system has a scalability score of {scalability_score:.1f}/1.0, suggesting potential issues under load.",
                severity="critical" if scalability_score < 0.3 else "warning",
                evidence={"scalability_score": scalability_score},
                recommendations=[
                    "Identify and address bottlenecks in the system",
                    "Implement caching strategies where appropriate",
                    "Consider horizontal scaling capabilities"
                ]
            ))
        else:
            findings.append(Finding(
                title="Good Scalability",
                description=f"The system has a scalability score of {scalability_score:.1f}/1.0, indicating well-designed scaling capabilities.",
                severity="info",
                evidence={"scalability_score": scalability_score}
            ))
        
        # Check cloud-native status
        if not cloud_native:
            findings.append(Finding(
                title="Not Cloud Native",
                description="The system is not designed as cloud-native, which may limit deployment flexibility and scalability.",
                severity="warning",
                evidence={"is_cloud_native": cloud_native},
                recommendations=[
                    "Migrate to containerized deployment with Kubernetes",
                    "Adopt cloud-native design patterns",
                    "Implement infrastructure as code"
                ]
            ))
        else:
            findings.append(Finding(
                title="Cloud Native Architecture",
                description="The system follows cloud-native design principles, which supports scalability and resilience.",
                severity="info",
                evidence={"is_cloud_native": cloud_native}
            ))
        
        return findings
    
    def _analyze_testing(self, tech_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze testing practices.
        
        Args:
            tech_data: Dictionary containing the company's technical data
            
        Returns:
            List of findings related to testing
        """
        findings = []
        
        # Extract relevant metrics
        testing = tech_data.get("testing", {})
        test_coverage = testing.get("code_coverage", 0)
        has_unit_tests = testing.get("has_unit_tests", False)
        has_integration_tests = testing.get("has_integration_tests", False)
        has_e2e_tests = testing.get("has_e2e_tests", False)
        automated_testing = testing.get("has_automated_testing", False)
        
        # Check test coverage
        if test_coverage < 0.7:  # Less than 70% coverage
            findings.append(Finding(
                title="Low Test Coverage",
                description=f"Test coverage is {test_coverage:.1%}, which may result in undetected bugs and regression issues.",
                severity="critical" if test_coverage < 0.4 else "warning",
                evidence={"code_coverage": test_coverage},
                recommendations=[
                    "Establish minimum coverage requirements for critical components",
                    "Incrementally increase coverage in high-risk areas",
                    "Add coverage reports to CI pipeline"
                ]
            ))
        else:
            findings.append(Finding(
                title="Good Test Coverage",
                description=f"Test coverage is {test_coverage:.1%}, which is a healthy level for detecting issues early.",
                severity="info",
                evidence={"code_coverage": test_coverage}
            ))
        
        # Check testing types
        if not has_unit_tests:
            findings.append(Finding(
                title="Missing Unit Tests",
                description="The codebase lacks unit tests, which are essential for validating individual components.",
                severity="critical",
                evidence={"has_unit_tests": has_unit_tests},
                recommendations=[
                    "Implement unit testing framework",
                    "Start with critical business logic components",
                    "Train developers on test-driven development (TDD)"
                ]
            ))
        
        if not has_integration_tests:
            findings.append(Finding(
                title="Missing Integration Tests",
                description="The codebase lacks integration tests, which are needed to validate component interactions.",
                severity="warning",
                evidence={"has_integration_tests": has_integration_tests},
                recommendations=[
                    "Identify critical integration points",
                    "Implement integration testing framework",
                    "Focus on API contracts and database interactions"
                ]
            ))
        
        if not has_e2e_tests:
            findings.append(Finding(
                title="Missing End-to-End Tests",
                description="The codebase lacks end-to-end tests, which help validate full user workflows.",
                severity="warning",
                evidence={"has_e2e_tests": has_e2e_tests},
                recommendations=[
                    "Implement E2E testing for critical user journeys",
                    "Consider tools like Cypress, Playwright, or Selenium",
                    "Run E2E tests in CI pipeline before deployment"
                ]
            ))
        
        # Check for automated testing
        if not automated_testing:
            findings.append(Finding(
                title="No Automated Testing",
                description="Tests are not automated, reducing their effectiveness and consistency.",
                severity="critical",
                evidence={"has_automated_testing": automated_testing},
                recommendations=[
                    "Set up CI/CD pipeline with automated test execution",
                    "Block deploys that fail tests",
                    "Implement pre-commit hooks for local test execution"
                ]
            ))
        
        return findings
    
    def _analyze_tech_debt(self, tech_data: Dict[str, Any]) -> List[Finding]:
        """
        Analyze technical debt.
        
        Args:
            tech_data: Dictionary containing the company's technical data
            
        Returns:
            List of findings related to technical debt
        """
        findings = []
        
        # Extract relevant metrics
        tech_debt = tech_data.get("tech_debt", {})
        debt_ratio = tech_debt.get("debt_ratio", 0)
        outdated_dependencies = tech_debt.get("outdated_dependencies_count", 0)
        total_dependencies = tech_debt.get("total_dependencies_count", 0)
        has_tech_debt_tracking = tech_debt.get("has_tech_debt_tracking", False)
        
        # Check debt ratio
        if debt_ratio > 0.2:  # More than 20% of effort is technical debt
            findings.append(Finding(
                title="High Technical Debt",
                description=f"Technical debt ratio is {debt_ratio:.1%}, indicating significant ongoing maintenance burden.",
                severity="critical" if debt_ratio > 0.3 else "warning",
                evidence={"debt_ratio": debt_ratio},
                recommendations=[
                    "Implement technical debt reduction plan",
                    "Allocate sprint capacity for debt reduction",
                    "Document and prioritize known debt items"
                ]
            ))
        else:
            findings.append(Finding(
                title="Manageable Technical Debt",
                description=f"Technical debt ratio is {debt_ratio:.1%}, which is within reasonable limits.",
                severity="info",
                evidence={"debt_ratio": debt_ratio}
            ))
        
        # Check outdated dependencies
        if total_dependencies > 0:
            outdated_ratio = outdated_dependencies / total_dependencies
            if outdated_ratio > 0.2:  # More than 20% of dependencies outdated
                findings.append(Finding(
                    title="Outdated Dependencies",
                    description=f"{outdated_dependencies} out of {total_dependencies} dependencies ({outdated_ratio:.1%}) are outdated, potentially exposing security vulnerabilities.",
                    severity="critical" if outdated_ratio > 0.4 else "warning",
                    evidence={
                        "outdated_dependencies_count": outdated_dependencies,
                        "total_dependencies_count": total_dependencies,
                        "outdated_ratio": outdated_ratio
                    },
                    recommendations=[
                        "Implement regular dependency updates",
                        "Set up dependency scanning in CI pipeline",
                        "Prioritize security-related updates"
                    ]
                ))
            else:
                findings.append(Finding(
                    title="Dependencies Well-Maintained",
                    description=f"Only {outdated_dependencies} out of {total_dependencies} dependencies ({outdated_ratio:.1%}) are outdated.",
                    severity="info",
                    evidence={
                        "outdated_dependencies_count": outdated_dependencies,
                        "total_dependencies_count": total_dependencies,
                        "outdated_ratio": outdated_ratio
                    }
                ))
        
        # Check tech debt tracking
        if not has_tech_debt_tracking:
            findings.append(Finding(
                title="No Technical Debt Tracking",
                description="The team does not track technical debt, making it difficult to manage and prioritize.",
                severity="warning",
                evidence={"has_tech_debt_tracking": has_tech_debt_tracking},
                recommendations=[
                    "Implement tech debt tracking in issue management system",
                    "Regularly review and prioritize debt items",
                    "Set clear criteria for when to address debt"
                ]
            ))
        else:
            findings.append(Finding(
                title="Technical Debt Tracking in Place",
                description="The team actively tracks technical debt, which is a good practice for managing it effectively.",
                severity="info",
                evidence={"has_tech_debt_tracking": has_tech_debt_tracking}
            ))
        
        return findings
    
    def _calculate_score(self, findings: List[Finding]) -> float:
        """
        Calculate an overall score based on findings.
        
        Args:
            findings: List of findings
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Count findings by severity
        critical = sum(1 for f in findings if f.severity == "critical")
        warning = sum(1 for f in findings if f.severity == "warning")
        info = sum(1 for f in findings if f.severity == "info")
        
        # Start with a base score
        base_score = 0.7
        
        # Adjust based on findings
        score = base_score - (critical * 0.15) - (warning * 0.05) + (info * 0.025)
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def _determine_status(self, score: float) -> str:
        """
        Determine overall status based on score.
        
        Args:
            score: Score between 0.0 and 1.0
            
        Returns:
            Status (pass, warning, fail)
        """
        if score >= 0.7:
            return "pass"
        elif score >= 0.4:
            return "warning"
        else:
            return "fail"
    
    def _generate_summary(self, score: float, findings: List[Finding]) -> str:
        """
        Generate a summary based on score and findings.
        
        Args:
            score: Score between 0.0 and 1.0
            findings: List of findings
            
        Returns:
            Summary of the technical due diligence
        """
        critical_count = sum(1 for f in findings if f.severity == "critical")
        warning_count = sum(1 for f in findings if f.severity == "warning")
        
        if score >= 0.7:
            return f"The technical foundation of the company is solid with only {critical_count} critical and {warning_count} minor issues identified. The codebase appears well-maintained with good engineering practices."
        elif score >= 0.4:
            return f"The company's technical implementation has several concerning issues with {critical_count} critical and {warning_count} minor problems identified. These should be addressed to ensure long-term maintainability and scalability."
        else:
            return f"The technical due diligence revealed significant issues with {critical_count} critical and {warning_count} minor problems identified. The codebase requires substantial remediation to meet industry standards."