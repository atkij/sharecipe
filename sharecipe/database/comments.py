from ..models.comment import Comment

from .database import get_db

def find(recipe_id: int) -> list[Comment]:
    db = get_db()

    query = ('SELECT comment.*, profile_view.* FROM comment '
             'INNER JOIN profile_view ON comment.user_id = profile_view.user_id '
             'WHERE comment.recipe_id = ? ORDER BY created DESC')
    
    comments = db.execute(
        query,
        (recipe_id,)
    ).fetchall()

    return list(map(Comment.from_query, comments))

def find_one(comment_id: int) -> Comment|None:
    db = get_db()

    query = ('SELECT comment.*, profile_view.* FROM comment '
             'INNER JOIN profile_view ON comment.user_id = profile_view.user_id '
             'WHERE comment.comment_id = ?')
    
    comment = db.execute(
        query,
        (comment_id,)
    ).fetchone()

    if comment is None:
        return None
    
    return Comment.from_query(comment)

def create(user_id, recipe_id, body):
    db = get_db()

    query = 'INSERT INTO comment (user_id, recipe_id, body) VALUES (?, ?, ?)'

    db.execute(
        query,
        (user_id, recipe_id, body)
    )

    db.commit()

def delete(comment_id):
    db = get_db()

    query = 'DELETE FROM comment WHERE comment_id = ?'

    db.execute(
        query,
        (comment_id,)
    )

    db.commit()