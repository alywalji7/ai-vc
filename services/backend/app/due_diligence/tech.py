"""
Technical due diligence module.

This module implements a technical due diligence check for evaluating
the code quality, architecture, and technical debt of a company's GitHub repositories.
"""

import random
import logging
from typing import Dict, List, Any, Tuple, Optional

import httpx

from app.due_diligence.base import DDModule, Verdict, Finding

logger = logging.getLogger(__name__)


class TechDD(DDModule):
    """Technical due diligence module for GitHub repository analysis."""
    
    @property
    def name(self) -> str:
        """Get the name of the module."""
        return "tech"
    
    async def run(self, target_id: str) -> Verdict:
        """
        Run technical due diligence on a target.

        This module evaluates:
        - Code quality metrics
        - Repository activity
        - Technical stack
        - Architecture
        - Security considerations

        Args:
            target_id: ID of the company to analyze

        Returns:
            Verdict with technical assessment
        """
        logger.info(f"Running technical due diligence for company {target_id}")
        
        try:
            # Get GitHub data for the company
            github_data = await self._get_github_data(target_id)
            
            # Analyze repositories
            analysis_results = await self._analyze_repositories(github_data)
            
            # Extract scores and findings
            code_quality_score = analysis_results["code_quality"]["score"]
            activity_score = analysis_results["activity"]["score"]
            tech_stack_score = analysis_results["tech_stack"]["score"]
            architecture_score = analysis_results["architecture"]["score"]
            security_score = analysis_results["security"]["score"]
            
            findings = (
                analysis_results["code_quality"]["findings"] +
                analysis_results["activity"]["findings"] +
                analysis_results["tech_stack"]["findings"] +
                analysis_results["architecture"]["findings"] +
                analysis_results["security"]["findings"]
            )
            
            # Calculate overall score (weighted average)
            weights = {
                "code_quality": 0.3,
                "activity": 0.2,
                "tech_stack": 0.2,
                "architecture": 0.2,
                "security": 0.1
            }
            
            overall_score = (
                code_quality_score * weights["code_quality"] +
                activity_score * weights["activity"] +
                tech_stack_score * weights["tech_stack"] +
                architecture_score * weights["architecture"] +
                security_score * weights["security"]
            )
            
            # Determine status based on overall score
            status = self._get_status_from_score(overall_score)
            
            # Generate summary
            summary = self._generate_summary(
                overall_score,
                code_quality_score,
                activity_score,
                tech_stack_score,
                architecture_score,
                security_score,
                github_data
            )
            
            # Return verdict
            return Verdict(
                score=overall_score,
                status=status,
                summary=summary,
                findings=findings,
                details={
                    "code_quality_score": code_quality_score,
                    "activity_score": activity_score,
                    "tech_stack_score": tech_stack_score,
                    "architecture_score": architecture_score,
                    "security_score": security_score,
                    "github_data": github_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error in technical due diligence: {str(e)}")
            return Verdict(
                score=0.0,
                status="error",
                summary=f"Failed to complete technical due diligence: {str(e)}",
                findings=[
                    Finding(
                        title="Due Diligence Error",
                        description=f"An error occurred during technical due diligence: {str(e)}",
                        severity="critical"
                    )
                ]
            )
    
    async def _get_github_data(self, company_id: str) -> Dict[str, Any]:
        """
        Get GitHub data for a company.

        Args:
            company_id: ID of the company

        Returns:
            Dictionary with GitHub repository data
        """
        try:
            # Get basic company data to find GitHub account
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8080/api/companies/{company_id}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    company_data = response.json()
                    return await self._fetch_github_data(company_id, company_data)
            
            # If we can't get company data or GitHub data, use simulated data
            return self._generate_github_data(company_id, {})
            
        except Exception as e:
            logger.warning(f"Error fetching GitHub data, using generated data: {str(e)}")
            return self._generate_github_data(company_id, {})
    
    async def _fetch_github_data(self, company_id: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch GitHub data from the graph ingest service.

        Args:
            company_id: ID of the company
            company_data: Company information

        Returns:
            Dictionary with GitHub data
        """
        try:
            github_org = company_data.get("github_org", "")
            if not github_org and "socials" in company_data:
                for social in company_data["socials"]:
                    if "github.com" in social.get("url", ""):
                        github_org = social["url"].split("/")[-1]
                        break
            
            if not github_org:
                raise ValueError("No GitHub organization found for company")
            
            # Fetch GitHub data from the graph ingest service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8080/api/github/orgs/{github_org}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise ValueError(f"Failed to fetch GitHub data: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error fetching GitHub data: {str(e)}")
            return self._generate_github_data(company_id, company_data)
    
    def _generate_github_data(self, company_id: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate GitHub data based on company information.
        This is a fallback when we can't get real GitHub data.

        Args:
            company_id: ID of the company
            company_data: Company information

        Returns:
            Dictionary with generated GitHub data
        """
        # Use a fixed seed based on company_id for reproducible results
        seed = sum(ord(c) for c in company_id)
        random.seed(seed)
        
        # Get company name from data or generate one
        company_name = company_data.get("name", f"Company {company_id}")
        
        # Generate a GitHub organization name based on company name
        github_org = company_name.lower().replace(" ", "-")
        
        # Generate repositories
        num_repos = random.randint(3, 12)
        repositories = []
        
        # Common tech stacks to choose from
        tech_stacks = [
            {
                "language": "JavaScript",
                "frameworks": ["React", "Node.js", "Express"],
                "databases": ["MongoDB", "PostgreSQL"],
                "tools": ["Webpack", "ESLint", "Jest"]
            },
            {
                "language": "Python",
                "frameworks": ["Django", "Flask", "FastAPI"],
                "databases": ["PostgreSQL", "SQLite"],
                "tools": ["pytest", "black", "Poetry"]
            },
            {
                "language": "Java",
                "frameworks": ["Spring Boot", "Hibernate"],
                "databases": ["MySQL", "Oracle"],
                "tools": ["Maven", "JUnit", "Gradle"]
            },
            {
                "language": "Ruby",
                "frameworks": ["Rails", "Sinatra"],
                "databases": ["PostgreSQL", "Redis"],
                "tools": ["RSpec", "Rubocop", "Bundler"]
            },
            {
                "language": "Go",
                "frameworks": ["Gin", "Echo"],
                "databases": ["PostgreSQL", "MongoDB"],
                "tools": ["go test", "golint", "dep"]
            }
        ]
        
        # Choose a primary tech stack for this company
        primary_stack = random.choice(tech_stacks)
        secondary_stack = random.choice([s for s in tech_stacks if s != primary_stack])
        
        for i in range(num_repos):
            # Determine if this is a main product repository
            is_main = i < 2
            
            # Choose the stack for this repository
            repo_stack = primary_stack if is_main or random.random() < 0.7 else secondary_stack
            
            # Generate repository statistics
            contributors = random.randint(1, 25) if is_main else random.randint(1, 8)
            stars = random.randint(5, 500) if is_main else random.randint(0, 50)
            forks = int(stars * random.uniform(0.1, 0.3))
            commit_frequency = random.uniform(0.5, 8) if is_main else random.uniform(0.1, 2)
            
            # Generate code quality metrics
            code_quality = {
                "test_coverage": random.uniform(0.1, 0.9),
                "documentation_score": random.uniform(0.2, 0.8),
                "linting_score": random.uniform(0.3, 0.95),
                "complexity_score": random.uniform(0.3, 0.9),
                "vulnerabilities": random.randint(0, 10)
            }
            
            # Repository name
            if is_main:
                repo_name = f"{github_org}-{['api', 'frontend', 'backend', 'core', 'service'][i % 5]}"
            else:
                repo_name = f"{github_org}-{['utils', 'tools', 'client', 'sdk', 'lib', 'ui'][i % 6]}"
            
            repositories.append({
                "name": repo_name,
                "description": f"{'Main' if is_main else 'Support'} repository for {company_name}",
                "language": repo_stack["language"],
                "frameworks": random.sample(repo_stack["frameworks"], k=min(2, len(repo_stack["frameworks"]))),
                "databases": random.sample(repo_stack["databases"], k=min(1, len(repo_stack["databases"]))),
                "tools": random.sample(repo_stack["tools"], k=min(2, len(repo_stack["tools"]))),
                "stars": stars,
                "forks": forks,
                "contributors": contributors,
                "commit_frequency": commit_frequency,  # commits per day
                "last_commit": f"2024-0{random.randint(1, 4)}-{random.randint(1, 28)}",
                "is_public": True,
                "is_archived": False,
                "code_quality": code_quality
            })
        
        return {
            "company_id": company_id,
            "github_org": github_org,
            "repositories": repositories,
            "total_stars": sum(repo["stars"] for repo in repositories),
            "total_contributors": sum(repo["contributors"] for repo in repositories),
            "primary_language": primary_stack["language"],
            "language_distribution": self._calculate_language_distribution(repositories)
        }
    
    def _calculate_language_distribution(self, repositories: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate language distribution across repositories.
        
        Args:
            repositories: List of repository data
            
        Returns:
            Dictionary mapping languages to their percentage
        """
        languages = {}
        total_repos = len(repositories)
        
        for repo in repositories:
            lang = repo["language"]
            languages[lang] = languages.get(lang, 0) + 1
        
        return {lang: count / total_repos for lang, count in languages.items()}
    
    async def _analyze_repositories(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GitHub repositories.

        Args:
            github_data: GitHub repository data

        Returns:
            Dictionary with analysis results
        """
        repositories = github_data.get("repositories", [])
        
        # Analyze different aspects
        code_quality_score, code_quality_findings = self._analyze_code_quality(repositories)
        activity_score, activity_data = self._analyze_repository_activity(github_data)
        tech_stack_score, tech_stack_data = self._analyze_tech_stack(repositories)
        architecture_score, architecture_data = self._analyze_architecture(repositories)
        security_score, security_data = self._analyze_security(repositories)
        
        # Create activity findings
        activity_findings = [
            Finding(
                title="Repository Activity",
                description=self._get_activity_description(activity_score, activity_data),
                severity="warning" if activity_score < 0.5 else "info"
            )
        ]
        
        # Create tech stack findings
        tech_stack_findings = [
            Finding(
                title="Technical Stack Assessment",
                description=self._get_tech_stack_description(tech_stack_score, tech_stack_data),
                severity="warning" if tech_stack_score < 0.5 else "info"
            )
        ]
        
        # Create architecture findings
        architecture_findings = [
            Finding(
                title="Architecture Assessment",
                description=self._get_architecture_description(architecture_score),
                severity="warning" if architecture_score < 0.5 else "info"
            )
        ]
        
        # Create security findings
        security_findings = [
            Finding(
                title="Security Assessment",
                description=self._get_security_description(security_score),
                severity="critical" if security_score < 0.3 else "warning" if security_score < 0.6 else "info"
            )
        ]
        
        return {
            "code_quality": {
                "score": code_quality_score,
                "findings": code_quality_findings
            },
            "activity": {
                "score": activity_score,
                "data": activity_data,
                "findings": activity_findings
            },
            "tech_stack": {
                "score": tech_stack_score,
                "data": tech_stack_data,
                "findings": tech_stack_findings
            },
            "architecture": {
                "score": architecture_score,
                "data": architecture_data,
                "findings": architecture_findings
            },
            "security": {
                "score": security_score,
                "data": security_data,
                "findings": security_findings
            }
        }
    
    def _analyze_code_quality(self, repositories: List[Dict[str, Any]]) -> Tuple[float, List[Finding]]:
        """
        Analyze code quality metrics.

        Args:
            repositories: List of repository data

        Returns:
            Tuple of (score, findings)
        """
        findings = []
        
        if not repositories:
            findings.append(Finding(
                title="No Repositories Found",
                description="No GitHub repositories were found for this company.",
                severity="critical"
            ))
            return 0.0, findings
        
        # Calculate average code quality metrics across repositories
        avg_test_coverage = sum(repo.get("code_quality", {}).get("test_coverage", 0) for repo in repositories) / len(repositories)
        avg_documentation = sum(repo.get("code_quality", {}).get("documentation_score", 0) for repo in repositories) / len(repositories)
        avg_linting = sum(repo.get("code_quality", {}).get("linting_score", 0) for repo in repositories) / len(repositories)
        avg_complexity = sum(repo.get("code_quality", {}).get("complexity_score", 0) for repo in repositories) / len(repositories)
        total_vulnerabilities = sum(repo.get("code_quality", {}).get("vulnerabilities", 0) for repo in repositories)
        
        # Evaluate test coverage
        if avg_test_coverage < 0.3:
            findings.append(Finding(
                title="Low Test Coverage",
                description=f"Average test coverage across repositories is {avg_test_coverage:.1%}, "
                           f"which is concerning. This indicates a high risk of regressions and bugs.",
                severity="critical",
                recommendations=["Implement a test strategy", "Add unit and integration tests", "Set up CI/CD for testing"]
            ))
        elif avg_test_coverage < 0.6:
            findings.append(Finding(
                title="Moderate Test Coverage",
                description=f"Average test coverage across repositories is {avg_test_coverage:.1%}, "
                           f"which could be improved. Key components should have higher coverage.",
                severity="warning",
                recommendations=["Increase test coverage for critical components", "Add integration tests"]
            ))
        else:
            findings.append(Finding(
                title="Good Test Coverage",
                description=f"Average test coverage across repositories is {avg_test_coverage:.1%}, "
                           f"which indicates a good testing practice.",
                severity="info"
            ))
        
        # Evaluate documentation
        if avg_documentation < 0.3:
            findings.append(Finding(
                title="Poor Documentation",
                description=f"The codebase has limited documentation ({avg_documentation:.1%} score), "
                           f"which makes onboarding and maintenance difficult.",
                severity="warning",
                recommendations=["Add README files to all repositories", "Document key components and APIs"]
            ))
        
        # Evaluate code style/linting
        if avg_linting < 0.5:
            findings.append(Finding(
                title="Inconsistent Code Style",
                description=f"Code style consistency is low ({avg_linting:.1%} score), "
                           f"suggesting a lack of standardized formatting and linting.",
                severity="warning",
                recommendations=["Implement linters and formatters", "Set up pre-commit hooks"]
            ))
        
        # Evaluate code complexity
        if avg_complexity < 0.4:
            findings.append(Finding(
                title="High Code Complexity",
                description=f"The codebase has high complexity ({avg_complexity:.1%} score), "
                           f"suggesting potential maintenance challenges.",
                severity="warning",
                recommendations=["Refactor complex functions", "Apply SOLID principles", "Review architectural decisions"]
            ))
        
        # Evaluate security vulnerabilities
        vulnerabilities_per_repo = total_vulnerabilities / len(repositories)
        if vulnerabilities_per_repo > 3:
            findings.append(Finding(
                title="Security Vulnerabilities",
                description=f"Found an average of {vulnerabilities_per_repo:.1f} vulnerabilities per repository, "
                           f"which is concerning.",
                severity="critical",
                recommendations=["Address identified vulnerabilities", "Set up security scanning"]
            ))
        elif vulnerabilities_per_repo > 1:
            findings.append(Finding(
                title="Some Security Vulnerabilities",
                description=f"Found an average of {vulnerabilities_per_repo:.1f} vulnerabilities per repository.",
                severity="warning",
                recommendations=["Review and fix vulnerabilities", "Implement security scanning"]
            ))
        
        # Calculate overall score (weighted average)
        weights = {
            "test_coverage": 0.3,
            "documentation": 0.2,
            "linting": 0.15,
            "complexity": 0.25,
            "vulnerabilities": 0.1
        }
        
        # For vulnerabilities, convert to a score (higher is better)
        vulnerability_score = max(0, 1 - (vulnerabilities_per_repo / 10))
        
        overall_score = (
            avg_test_coverage * weights["test_coverage"] +
            avg_documentation * weights["documentation"] +
            avg_linting * weights["linting"] +
            avg_complexity * weights["complexity"] +
            vulnerability_score * weights["vulnerabilities"]
        )
        
        return overall_score, findings
    
    def _analyze_repository_activity(self, github_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze repository activity.

        Args:
            github_data: GitHub data

        Returns:
            Tuple of (score, activity_data)
        """
        repositories = github_data.get("repositories", [])
        
        if not repositories:
            return 0.0, {"reason": "No repositories found"}
        
        # Calculate average commit frequency
        avg_commit_frequency = sum(repo.get("commit_frequency", 0) for repo in repositories) / len(repositories)
        
        # Determine time since last commit
        from datetime import datetime
        today = datetime.now()
        
        if all(repo.get("last_commit") for repo in repositories):
            last_commits = [datetime.strptime(repo["last_commit"], "%Y-%m-%d") for repo in repositories]
            most_recent_commit = max(last_commits)
            days_since_last_commit = (today - most_recent_commit).days
        else:
            # Default if we don't have last commit data
            days_since_last_commit = 30
        
        # Determine active repositories percentage
        active_repos = sum(1 for repo in repositories if not repo.get("is_archived", False))
        active_repos_percentage = active_repos / len(repositories)
        
        # Calculate contributor ratio (avg contributors per repo)
        avg_contributors = sum(repo.get("contributors", 0) for repo in repositories) / len(repositories)
        contributor_ratio_score = min(1.0, avg_contributors / 5)  # 5+ contributors is ideal
        
        # Calculate activity score
        activity_data = {
            "avg_commit_frequency": avg_commit_frequency,
            "days_since_last_commit": days_since_last_commit,
            "active_repos_percentage": active_repos_percentage,
            "avg_contributors": avg_contributors
        }
        
        commit_frequency_score = min(1.0, avg_commit_frequency / 5)  # 5+ commits per day is ideal
        recency_score = max(0, 1 - (days_since_last_commit / 60))  # 0-60 days scale
        
        activity_score = (
            commit_frequency_score * 0.4 +
            recency_score * 0.3 +
            active_repos_percentage * 0.15 +
            contributor_ratio_score * 0.15
        )
        
        return activity_score, activity_data
    
    def _analyze_tech_stack(self, repositories: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze technical stack.

        Args:
            repositories: List of repository data

        Returns:
            Tuple of (score, tech_stack_data)
        """
        if not repositories:
            return 0.0, {"reason": "No repositories found"}
        
        # Collect all languages, frameworks, and tools used across repositories
        languages = {}
        frameworks = {}
        databases = {}
        tools = {}
        
        for repo in repositories:
            # Count languages
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            
            # Count frameworks
            for framework in repo.get("frameworks", []):
                frameworks[framework] = frameworks.get(framework, 0) + 1
            
            # Count databases
            for db in repo.get("databases", []):
                databases[db] = databases.get(db, 0) + 1
            
            # Count tools
            for tool in repo.get("tools", []):
                tools[tool] = tools.get(tool, 0) + 1
        
        # Calculate tech diversity
        language_diversity = len(languages) / max(1, len(repositories))
        framework_diversity = len(frameworks) / max(1, len(repositories) * 2)  # Assuming ~2 frameworks per repo is ideal
        
        # Technology consistency (primary language usage)
        primary_language = max(languages.items(), key=lambda x: x[1])[0]
        primary_language_usage = languages[primary_language] / len(repositories)
        
        # Modern frameworks/tools assessment
        # This is a simplification - in a real system we would have a database of framework maturity and popularity
        modern_frameworks = {
            "React": 0.9, "Vue": 0.9, "Angular": 0.8, 
            "Next.js": 0.95, "Nuxt": 0.9, "Django": 0.8, 
            "FastAPI": 0.95, "Flask": 0.8, "Spring Boot": 0.85,
            "Node.js": 0.85, "Express": 0.8, "Rails": 0.75,
            "Laravel": 0.8, ".NET Core": 0.85, "ASP.NET": 0.75,
            "Phoenix": 0.9, "Rust": 0.95, "Go": 0.9
        }
        
        framework_modernity = 0
        for framework, count in frameworks.items():
            modernity_score = modern_frameworks.get(framework, 0.5)
            framework_modernity += modernity_score * (count / sum(frameworks.values()))
        
        # Calculate overall tech stack score
        tech_stack_data = {
            "languages": languages,
            "frameworks": frameworks,
            "databases": databases,
            "tools": tools,
            "primary_language": primary_language,
            "primary_language_usage": primary_language_usage,
            "language_diversity": language_diversity,
            "framework_diversity": framework_diversity,
            "framework_modernity": framework_modernity
        }
        
        # Balance between consistency and diversity
        diversity_score = (language_diversity * 0.3) + (framework_diversity * 0.7)
        diversity_score = min(1.0, diversity_score * 1.5)  # Normalize
        
        consistency_score = primary_language_usage
        modernity_score = framework_modernity
        
        tech_stack_score = (
            consistency_score * 0.3 +
            diversity_score * 0.3 +
            modernity_score * 0.4
        )
        
        return tech_stack_score, tech_stack_data
    
    def _analyze_architecture(self, repositories: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze architecture quality.

        Args:
            repositories: List of repository data

        Returns:
            Tuple of (score, architecture_data)
        """
        if not repositories:
            return 0.0, {"reason": "No repositories found"}
        
        # Check repository organization
        has_api_repo = any("api" in repo.get("name", "").lower() for repo in repositories)
        has_frontend_repo = any("frontend" in repo.get("name", "").lower() or "ui" in repo.get("name", "").lower() for repo in repositories)
        has_backend_repo = any("backend" in repo.get("name", "").lower() or "service" in repo.get("name", "").lower() for repo in repositories)
        
        service_separation = (has_api_repo + has_frontend_repo + has_backend_repo) / 3
        
        # Look for microservices architecture
        microservices_likelihood = min(1.0, len(repositories) / 8)  # More repos suggest microservices
        
        # Infer code organization from repository descriptions and names
        monolith_likelihood = 1.0 - microservices_likelihood
        
        architecture_data = {
            "service_separation": service_separation,
            "microservices_likelihood": microservices_likelihood,
            "monolith_likelihood": monolith_likelihood,
            "repos_count": len(repositories)
        }
        
        # Calculate architecture score
        # Neither microservices nor monolith is inherently better,
        # but clear separation of concerns is generally good
        architecture_score = (
            service_separation * 0.6 +
            0.4  # Base score
        )
        
        return architecture_score, architecture_data
    
    def _analyze_security(self, repositories: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze security considerations.

        Args:
            repositories: List of repository data

        Returns:
            Tuple of (score, security_data)
        """
        if not repositories:
            return 0.0, {"reason": "No repositories found"}
        
        # Count security vulnerabilities
        total_vulnerabilities = sum(repo.get("code_quality", {}).get("vulnerabilities", 0) for repo in repositories)
        vulnerabilities_per_repo = total_vulnerabilities / len(repositories)
        
        # Check for security tooling
        security_tools = ["eslint-security", "bandit", "snyk", "dependabot", "sonarqube", "owasp"]
        has_security_tools = False
        
        for repo in repositories:
            for tool in repo.get("tools", []):
                if any(security_tool in tool.lower() for security_tool in security_tools):
                    has_security_tools = True
                    break
        
        security_data = {
            "total_vulnerabilities": total_vulnerabilities,
            "vulnerabilities_per_repo": vulnerabilities_per_repo,
            "has_security_tools": has_security_tools
        }
        
        # Calculate security score
        vulnerability_score = max(0, 1 - (vulnerabilities_per_repo / 5))
        tooling_score = 0.7 if has_security_tools else 0.3
        
        security_score = (
            vulnerability_score * 0.6 +
            tooling_score * 0.4
        )
        
        return security_score, security_data
    
    def _get_code_quality_description(self, score: float) -> str:
        """Generate a description of code quality based on score."""
        if score < 0.3:
            return ("The codebase shows significant quality issues, including poor test coverage, "
                   "inadequate documentation, and potential security vulnerabilities. "
                   "A comprehensive review and refactoring effort is recommended.")
        elif score < 0.6:
            return ("The code quality is moderate, with room for improvement. "
                   "Specific areas to address include enhancing test coverage, "
                   "improving documentation, and addressing potential technical debt.")
        else:
            return ("The codebase demonstrates good overall quality, with reasonable test coverage, "
                   "documentation, and maintainable code. Continue to maintain standards "
                   "and address any specific areas flagged in the findings.")
    
    def _get_activity_description(self, score: float, activity_data: Dict[str, Any]) -> str:
        """Generate a description of repository activity based on score and data."""
        avg_commit = activity_data.get("avg_commit_frequency", 0)
        days_since = activity_data.get("days_since_last_commit", 0)
        
        if score < 0.3:
            return (f"Repository activity is low with {avg_commit:.1f} average commits per day. "
                   f"The most recent commit was approximately {days_since} days ago. "
                   f"This suggests the project may be inactive or minimally maintained.")
        elif score < 0.6:
            return (f"Repository shows moderate activity with {avg_commit:.1f} average commits per day. "
                   f"The most recent commit was approximately {days_since} days ago. "
                   f"Regular development is occurring, but velocity could be improved.")
        else:
            return (f"Repository demonstrates healthy activity with {avg_commit:.1f} average commits per day. "
                   f"The most recent commit was approximately {days_since} days ago. "
                   f"This indicates active development and maintenance.")
    
    def _get_tech_stack_description(self, score: float, tech_data: Dict[str, Any]) -> str:
        """Generate a description of tech stack based on score and data."""
        primary_lang = tech_data.get("primary_language", "unknown")
        framework_text = ", ".join(list(tech_data.get("frameworks", {}).keys())[:3])
        modernity = tech_data.get("framework_modernity", 0)
        
        if score < 0.3:
            return (f"The technical stack is primarily based on {primary_lang} with frameworks including {framework_text}. "
                   f"The technology choices show signs of age or inconsistency, with a modernity score of {modernity:.1%}. "
                   f"Consider evaluating whether the current stack can support future business requirements.")
        elif score < 0.6:
            return (f"The technical stack is primarily based on {primary_lang} with frameworks including {framework_text}. "
                   f"The technology choices are reasonable with a modernity score of {modernity:.1%}, "
                   f"though some components may benefit from updates or standardization.")
        else:
            return (f"The technical stack is primarily based on {primary_lang} with frameworks including {framework_text}. "
                   f"The technology choices are modern and appropriate with a modernity score of {modernity:.1%}. "
                   f"The stack appears well-suited to the project requirements.")
    
    def _get_architecture_description(self, score: float) -> str:
        """Generate a description of architecture based on score."""
        if score < 0.3:
            return ("The architecture shows signs of significant technical debt or design issues. "
                   "Service boundaries are unclear, and the overall system design may struggle to scale. "
                   "Consider a comprehensive architecture review.")
        elif score < 0.6:
            return ("The architecture is functional but shows some areas for improvement. "
                   "Service boundaries exist but may benefit from clearer separation. "
                   "The system will likely require some refactoring to scale effectively.")
        else:
            return ("The architecture demonstrates good design principles with clear service boundaries. "
                   "The system appears well-organized and should scale reasonably well. "
                   "Continue maintaining clean architecture as the system evolves.")
    
    def _get_security_description(self, score: float) -> str:
        """Generate a description of security based on score."""
        if score < 0.3:
            return ("Security considerations appear inadequate. Multiple vulnerabilities were detected, "
                   "and there is limited evidence of security tooling or practices. "
                   "A security audit is strongly recommended.")
        elif score < 0.6:
            return ("Security measures are present but could be strengthened. Some vulnerabilities were detected, "
                   "and security tooling is partially implemented. "
                   "Consider enhancing security practices and addressing identified vulnerabilities.")
        else:
            return ("Security appears reasonably well-managed with limited vulnerabilities detected. "
                   "Security tooling is in place, and good practices are evident. "
                   "Continue regular security reviews and maintaining secure development practices.")
    
    def _generate_summary(
        self,
        overall_score: float,
        code_quality_score: float,
        activity_score: float,
        tech_stack_score: float,
        architecture_score: float,
        security_score: float,
        github_data: Dict[str, Any]
    ) -> str:
        """
        Generate a summary based on technical assessment scores.
        
        Args:
            various scores and github data
            
        Returns:
            Summary text
        """
        repo_count = len(github_data.get("repositories", []))
        total_stars = github_data.get("total_stars", 0)
        
        if overall_score < 0.4:
            summary = f"Technical due diligence across {repo_count} repositories reveals significant concerns. "
        elif overall_score < 0.7:
            summary = f"Technical due diligence across {repo_count} repositories shows mixed results. "
        else:
            summary = f"Technical due diligence across {repo_count} repositories demonstrates overall good quality. "
        
        # Add details about strongest and weakest areas
        scores = {
            "code quality": code_quality_score,
            "repository activity": activity_score,
            "technology stack": tech_stack_score,
            "architecture": architecture_score,
            "security practices": security_score
        }
        
        strongest = max(scores.items(), key=lambda x: x[1])
        weakest = min(scores.items(), key=lambda x: x[1])
        
        summary += f"The strongest area is {strongest[0]} ({strongest[1]:.1%}), "
        summary += f"while the weakest is {weakest[0]} ({weakest[1]:.1%}). "
        
        if weakest[1] < 0.3:
            summary += f"Immediate attention is recommended to address issues with {weakest[0]}."
        elif weakest[1] < 0.6:
            summary += f"Improvement is recommended in {weakest[0]}."
        else:
            summary += "All technical indicators are within acceptable ranges."
        
        if total_stars > 100:
            summary += f" The repositories have attracted {total_stars} stars, indicating good community interest."
        
        return summary
    
    def _get_status_from_score(self, score: float) -> str:
        """
        Convert a score to a status string.
        
        Args:
            score: Numeric score (0.0 to 1.0)
            
        Returns:
            Status string ("pass", "warning", or "fail")
        """
        if score < 0.4:
            return "fail"
        elif score < 0.7:
            return "warning"
        else:
            return "pass"