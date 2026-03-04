"""
Training service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.models.training import Course, CourseEdition, CourseParticipation, CourseStatus, EditionStatus
from app.schemas.training import CourseCreate, CourseUpdate, EditionCreate, EditionUpdate, ParticipationCreate, ParticipationUpdate


class CourseService:

    @staticmethod
    def create(db: Session, data: CourseCreate) -> Course:
        course = Course(**data.model_dump())
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def get_by_id(db: Session, course_id: int) -> Course:
        course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
        if not course:
            raise ValueError(f"Corso {course_id} non trovato")
        return course

    @staticmethod
    def get_all(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> list[Course]:
        query = db.query(Course).filter(Course.is_active == True)
        if company_id:
            query = query.filter(Course.company_id == company_id)
        return query.order_by(Course.titolo).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, course_id: int, data: CourseUpdate) -> Course:
        course = CourseService.get_by_id(db, course_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(course, field, value)
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def delete(db: Session, course_id: int) -> None:
        course = CourseService.get_by_id(db, course_id)
        course.is_active = False
        db.commit()


class EditionService:

    @staticmethod
    def create(db: Session, data: EditionCreate) -> CourseEdition:
        edition = CourseEdition(**data.model_dump())
        db.add(edition)
        db.commit()
        db.refresh(edition)
        return edition

    @staticmethod
    def get_by_id(db: Session, edition_id: int) -> CourseEdition:
        edition = db.query(CourseEdition).filter(CourseEdition.id == edition_id).first()
        if not edition:
            raise ValueError(f"Edizione {edition_id} non trovata")
        return edition

    @staticmethod
    def get_by_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> list[CourseEdition]:
        return db.query(CourseEdition).filter(
            CourseEdition.course_id == course_id
        ).order_by(CourseEdition.data_inizio.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, edition_id: int, data: EditionUpdate) -> CourseEdition:
        edition = EditionService.get_by_id(db, edition_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(edition, field, value)
        db.commit()
        db.refresh(edition)
        return edition

    @staticmethod
    def complete(db: Session, edition_id: int) -> CourseEdition:
        edition = EditionService.get_by_id(db, edition_id)
        edition.stato = EditionStatus.COMPLETED
        db.commit()
        db.refresh(edition)
        return edition


class ParticipationService:

    @staticmethod
    def create(db: Session, data: ParticipationCreate) -> CourseParticipation:
        participation = CourseParticipation(**data.model_dump())
        db.add(participation)
        db.commit()
        db.refresh(participation)
        return participation

    @staticmethod
    def get_by_id(db: Session, participation_id: int) -> CourseParticipation:
        p = db.query(CourseParticipation).filter(CourseParticipation.id == participation_id).first()
        if not p:
            raise ValueError(f"Partecipazione {participation_id} non trovata")
        return p

    @staticmethod
    def get_by_worker(db: Session, worker_id: int, skip: int = 0, limit: int = 100) -> list[CourseParticipation]:
        return db.query(CourseParticipation).filter(
            CourseParticipation.worker_id == worker_id
        ).order_by(CourseParticipation.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_edition(db: Session, edition_id: int) -> list[CourseParticipation]:
        return db.query(CourseParticipation).filter(
            CourseParticipation.edition_id == edition_id
        ).all()

    @staticmethod
    def update(db: Session, participation_id: int, data: ParticipationUpdate) -> CourseParticipation:
        p = ParticipationService.get_by_id(db, participation_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(p, field, value)
        db.commit()
        db.refresh(p)
        return p

    @staticmethod
    def delete(db: Session, participation_id: int) -> None:
        p = ParticipationService.get_by_id(db, participation_id)
        db.delete(p)
        db.commit()
