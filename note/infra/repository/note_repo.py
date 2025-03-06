from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from database import SessionLocal
from note.domain.note import Note as NoteVo
from note.domain.repository.note_repo import INoteRepository
from note.infra.db_models.note import Note, Tag
from utils.db_utils import row_to_dict


class NoteRepository(INoteRepository):
    def get_notes(self, user_id: str, page: int, items_per_page: int) -> tuple[int, list[NoteVo]]:
        with SessionLocal() as session:
            query = session.query(Note).options(joinedload(Note.tags)).filter(Note.user_id == user_id)

            total_count = query.count()
            notes = query.offset((page-1) * items_per_page).limit(items_per_page).all()

        note_vos = [NoteVo(**row_to_dict(note)) for note in notes]
        return total_count, note_vos

    def find_by_id(self, user_id: str, id: str) -> NoteVo:
        with SessionLocal() as session:
            note = session.query(Note).option(joinedload(Note.tags)).filter(Note.user_id == user_id).filter(Note.id == id).first()
            if not note:
                raise HTTPException(status_code=422)
        return NoteVo(**row_to_dict(note))

    def save(self, user_id: str, note_vo: NoteVo):
        with SessionLocal() as session:
            tags: list[Tag] = []
            for tag in note_vo.tags:
                existing_tag = session.query(Tag).filter(Tag.name == tag.name).first()
                if existing_tag:
                    tags.append(existing_tag)
                else:
                    tags.append(Tag(id=tag.id, name=tag.name, created_at=tag.created_at, updated_at=tag.updated_at))

            new_note = Note(
                id=note_vo.id,
                user_id=user_id,
                title=note_vo.title,
                content=note_vo.content,
                memo_date=note_vo.memo_date,
                tags=tags,
                created_at=note_vo.created_at,
                updated_at=note_vo.updated_at,
            )

            session.add(new_note)
            session.commit()

            return NoteVo(**row_to_dict(new_note))

    def update(self, user_id: str, note_vo: NoteVo):
        with SessionLocal() as session:
            self.delete_tags(user_id=user_id, id=note_vo.id)

            note = session.query(Note).filter(Note.user_id == user_id).filter(Note.id == note_vo.id).first()
            if not note:
                raise HTTPException(status_code=422)

            note.title = note_vo.title
            note.content = note_vo.content
            note.memo_date = note_vo.memo_date

            tags: list[Tag] = []
            for tag in note_vo.tags:
                existing_tag = session.query(Tag).filter(Tag.name == tag.name).first()
                if existing_tag:
                    tags.append(existing_tag)
                else:
                    tags.append(Tag(id=tag.id, name=tag.name, created_at=tag.created_at, updated_at=tag.updated_at))

            note.tags = tags

            session.add(note)
            session.commit()
            return NoteVo(**row_to_dict(note))

    def delete(self, user_id: str, id: str):
        with SessionLocal() as session:
            self.delete_tags(user_id=user_id, id=id)

            note = session.query(Note).filter(Note.user_id == user_id).filter(Note.id == id).first()
            if not note:
                raise HTTPException(status_code=422)

            session.delete(note)
            session.commit()

    def delete_tags(self, user_id: str, id: str):
        with SessionLocal() as session:
            note = session.query(Note).filter(Note.user_id == user_id).filter(Note.id == id).first()
            if not note:
                raise HTTPException(status_code=422)

            note.tags = []
            session.add(note)
            session.commit()

            unused_tags = session.query(Tag).filter(~Tag.notes.any()).all()
            for tag in unused_tags:
                session.delete(tag)

            session.commit()

    def get_notes_by_tag_name(self, user_id: str, tag_name: str, page: int, items_per_page: int) -> tuple[int, list[NoteVo]]:
        with SessionLocal() as session:
            tag = session.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                return 0, []

            query = session.query(Note).filter(Note.user_id == user_id).filter(Note.tags.any(id=tag.id)).all()

            total_count = query.count()
            notes = query.offset((page-1) * items_per_page).limit(items_per_page).all()

            res_notes = [NoteVo(**row_to_dict(note))  for note in notes]
            return total_count, res_notes


