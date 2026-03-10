"""
SQLAlchemy ORM models.
"""
from app.models.user import User, UserRole
from app.models.company import Company, Location, Department
from app.models.worker import Worker, ContractType, WorkerStatus
from app.models.deadline import Deadline, DeadlineType, DeadlineStatus, DeadlinePriority
from app.models.document import Document
from app.models.medical import HealthProtocol, MedicalVisit
from app.models.training import Course, CourseEdition, CourseParticipation
from app.models.dpi import DPIItem, DPIAssignment
from app.models.attendance import Timbratura, AttendanceRecord

# Ensure relationships are established
User.company = None
Worker.company = None

__all__ = [
    "User", "UserRole",
    "Company", "Location", "Department",
    "Worker", "ContractType", "WorkerStatus",
    "Deadline", "DeadlineType", "DeadlineStatus", "DeadlinePriority",
    "Document",
    "HealthProtocol", "MedicalVisit",
    "Course", "CourseEdition", "CourseParticipation",
    "DPIItem", "DPIAssignment",
    "Timbratura", "AttendanceRecord",
]
