from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)



def get_student_by_email(db: Session, email: str) -> Student | None:
    stmt = select(Student).where(Student.email == email)
    return db.scalars(stmt).first()


def get_students(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> tuple[list[Student], int]:
    count_stmt = select(func.count()).select_from(Student)
    stmt = select(Student)
    if not include_inactive:
        count_stmt = count_stmt.where(Student.is_active.is_(True))
        stmt = stmt.where(Student.is_active.is_(True))
    total = db.scalar(count_stmt) or 0
    stmt = stmt.order_by(Student.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all()), total


def create_student(db: Session, obj: StudentCreate) -> Student:
    
    db_obj = Student(**obj.model_dump(mode="json"))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_student(db: Session, db_obj: Student, obj: StudentUpdate) -> Student:
    data = obj.model_dump(mode="json", exclude_unset=True)
    for key, value in data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_student(db: Session, db_obj: Student) -> None:
    db.delete(db_obj)
    db.commit()
