"""
Employer building and job system for Simulacra environment.
"""
from typing import List, Optional
from src.environment.buildings.base import Building
from src.utils.types import (
    EmployerID, AgentID, JobID, SimulationTime
)


class JobOpening:
    """Represents a job opening at an employer."""
    def __init__(
        self,
        job_id: JobID,
        title: str,
        monthly_salary: float,
        required_skills: float,  # Simplified skill requirement [0,1]
        stress_level: float      # [0,1]
    ):
        self.id = job_id
        self.title = title
        self.monthly_salary = monthly_salary
        self.required_skills = required_skills
        self.stress_level = stress_level

    def get_monthly_stress_increase(self) -> float:
        """Return stress increase from this job per month."""
        return self.stress_level * 0.1


class Employment:
    """Represents an agent's employment contract."""
    def __init__(
        self,
        agent_id: AgentID,
        employer_id: EmployerID,
        job: JobOpening,
        start_time: SimulationTime
    ):
        self.agent_id = agent_id
        self.employer_id = employer_id
        self.job = job
        self.start_time = start_time
        self.performance = 1.0

    def calculate_monthly_pay(self) -> float:
        """Calculate pay adjusted by performance."""
        return self.job.monthly_salary * self.performance


class Employer(Building):
    """Employer building where agents can find and hold jobs."""
    def __init__(
        self,
        building_id: EmployerID,
        plot,
        company_name: str,
        jobs: List[JobOpening]
    ):
        super().__init__(building_id, plot)
        self.company_name = company_name
        self.jobs = jobs

    def generate_cues(self, agent_location: any) -> List:
        """Employers do not generate environmental cues."""
        return []

    def can_interact(self, agent) -> bool:
        """Agents can interact if any job opening is present."""
        return bool(self.jobs)

    def hire_agent(self, agent) -> Optional[Employment]:
        """Attempt to hire an agent into the first matching job."""
        if not self.jobs:
            return None
        job = self.jobs[0]
        # Simplified: hire any agent
        return Employment(
            agent_id=agent.id,
            employer_id=self.id,
            job=job,
            start_time=SimulationTime()
        )

    def __repr__(self) -> str:
        return (
            f"Employer(id={self.id}, company={self.company_name}, jobs={len(self.jobs)})"
        ) 
