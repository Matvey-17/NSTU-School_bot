from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import DeclarativeBase, relationship, Session

from random import choice

engine = create_engine('sqlite:///online-curators.db')


class Base(DeclarativeBase):
    pass


class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    id_tg = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    chat_id = Column(Integer)
    one_message = Column(String)
    curator_id = Column(Integer, ForeignKey('curators.id'))
    curator = relationship('Curators', back_populates='student')


class Curators(Base):
    __tablename__ = 'curators'

    id = Column(Integer, primary_key=True, index=True)
    id_tg = Column(Integer, unique=True, nullable=False)
    is_active = Column(Boolean, default=0)
    student = relationship('Students', back_populates='curator')


def add_student(tg_id, username):
    with Session(bind=engine) as db:
        student = Students(id_tg=tg_id, username=username)
        try:
            db.add(student)
            db.commit()
        except:
            db.rollback()


def add_curator(tg_id):
    with Session(bind=engine) as db:
        curator = Curators(id_tg=tg_id)
        try:
            db.add(curator)
            db.commit()
        except:
            db.rollback()


def set_curator(tg_id):
    with Session(bind=engine) as db:
        if (db.query(Students.curator_id).filter(Students.id_tg == tg_id).first())[0] == None:
            try:
                curators = list(db.query(Curators.id, Curators.id_tg).filter(Curators.is_active).all())
                if curators:
                    curator_random = choice(curators)
                    student_curator = db.query(Students).filter(Students.id_tg == tg_id).first()
                    student_curator.curator_id = int(curator_random.id)
                    db.commit()
                    return [1, int(curator_random.id_tg)]
                else:
                    return [-1]
            except:
                db.rollback()
        else:
            return [0]


def set_active(tg_id, active):
    with Session(bind=engine) as db:
        curator = db.query(Curators).filter(Curators.id_tg == tg_id).first()
        try:
            curator.is_active = active
            db.commit()
        except:
            db.rollback()


def list_students(tg_id):
    with Session(bind=engine) as db:
        curator = db.query(Curators).filter(Curators.id_tg == tg_id).first()
        text = []
        if curator.student:
            for students in curator.student:
                text.append(f'📌 @{students.username} - {students.id_tg}\n')
            return ' '.join(text)
        else:
            return 'Список пуст'


def complete(tg_id):
    with Session(bind=engine) as db:
        student = db.query(Students).filter(Students.id_tg == tg_id).first()
        if student:
            try:
                student.curator_id = None
                db.commit()
                return [1, student.username]
            except:
                db.rollback()
        else:
            return [0]


def add_chat_id(tg_id, id_message):
    with Session(bind=engine) as db:
        student = db.query(Students).filter(Students.id_tg == tg_id).first()
        try:
            student.chat_id = id_message
            db.commit()
            return student.chat_id
        except:
            db.rollback()


def set_chat_id(tg_id):
    with Session(bind=engine) as db:
        student = db.query(Students).filter(Students.id_tg == tg_id).first()
        if student.chat_id == None:
            return [False]
        else:
            return [True, student.chat_id]


def add_one_message(tg_id, one_message):
    with Session(bind=engine) as db:
        student = db.query(Students).filter(Students.id_tg == tg_id).first()
        if student.one_message == None:
            try:
                student.one_message = one_message
                db.commit()
            except:
                db.rollback()


def set_one_message(tg_id):
    with Session(bind=engine) as db:
        student = db.query(Students).filter(Students.id_tg == tg_id).first()
        return student.one_message


Base.metadata.create_all(bind=engine)
