from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from .schemas import PostCreate, PostUpdate, PostResponse, LikedPostResponse
from db.models import Post, User
from .auth import get_current_user

router = APIRouter()


@router.get('/posts', response_model=list[PostResponse], tags=['posts'])
def post_list(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts


@router.post('/posts/create', response_model=PostResponse, tags=['posts'])
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# @router.post("/post/update/{post_id}", status_code=status.HTTP_200_OK, tags=['posts'])
# def update_post(
#     post_id: int,
#     post: PostUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     db_post = db.query(Post).filter(Post.id == post_id).first()
#     if db_post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
#     if current_user.id != db_post.author_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")
#     if post.title is not None:
#         db_post.title = post.title
#     if post.content is not None:
#         db_post.content = post.content
#     db.commit()
#     db.refresh(db_post)
#     return {"status": "Updated!", "post": db_post}
