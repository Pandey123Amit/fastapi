from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def get_course_by_code(db: Session, code: str) -> Course | None:
    stmt = select(Course).where(Course.code == code)
    return db.scalars(stmt).first()


def get_courses(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> tuple[list[Course], int]:
    count_stmt = select(func.count()).select_from(Course)
    stmt = select(Course)
    if not include_inactive:
        count_stmt = count_stmt.where(Course.is_active.is_(True))
        stmt = stmt.where(Course.is_active.is_(True))
    total = db.scalar(count_stmt) or 0
    stmt = stmt.order_by(Course.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all()), total


def create_course(db: Session, obj: CourseCreate) -> Course:
    db_obj = Course(**obj.model_dump(mode="json"))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_course(db: Session, db_obj: Course, obj: CourseUpdate) -> Course:
    data = obj.model_dump(mode="json", exclude_unset=True)
    for key, value in data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_course(db: Session, db_obj: Course) -> None:
    db.delete(db_obj)
    db.commit()
