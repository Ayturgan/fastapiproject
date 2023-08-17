from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from .schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
    LikedPostResponse,
    UserProfile,
    UserProfileWithPosts,
    FavoritesUserPosts,
)
from db.models import Post, User
from .auth import get_current_user

router = APIRouter()


@router.get("/posts", response_model=list[PostResponse], tags=["posts"])
def post_list(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts


@router.get("/post/{post_id}/", response_model=PostResponse, tags=["posts"])
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="POst not found"
        )
    return post


@router.post("/post/create", response_model=PostResponse, tags=["posts"])
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.put("/post/{post_id}/", response_model=PostResponse, tags=["posts"])
def update_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_post = db.query(Post).get(post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if current_user.id != existing_post.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    existing_post.title = post.title
    existing_post.content = post.content
    db.commit()
    db.refresh(existing_post)
    return existing_post


@router.delete("/post/delete/{post_id}", tags=["posts"])
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if current_user.id != post.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    db.delete(post)
    db.commit()
    return {"status": "Deleted!"}


@router.get("/current_profile/", response_model=UserProfileWithPosts, tags=["profiles"])
def get_current_profile(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_profile = UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
    )
    user_posts = [
        PostResponse(
            id=post.id, title=post.title, content=post.content, author=user_profile
        )
        for post in current_user.posts
    ]

    return {"user_profile": user_profile, "user_posts": user_posts}


@router.get(
    "/profile/{profile_id}/", response_model=UserProfileWithPosts, tags=["profiles"]
)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(profile_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_profile = UserProfile(
        id=user.id, username=user.username, email=user.email, full_name=user.full_name
    )
    user_posts = [
        PostResponse(
            id=post.id, title=post.title, content=post.content, author=user_profile
        )
        for post in user.posts
    ]
    return {"user_profile": user_profile, "user_posts": user_posts}


@router.post("/post/{post_id}/like", tags=["post_likes"])
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if current_user.id == post.author_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot like or dislike your own post",
        )
    if current_user in post.liked_by:
        post.liked_by.remove(current_user)
        db.commit()
        return HTTPException(status_code=status.HTTP_200_OK, detail="Disliked!")
    else:
        post.liked_by.append(current_user)
        db.commit()
        return HTTPException(status_code=status.HTTP_200_OK, detail="Liked!")


@router.get("/liked-posts/", response_model=LikedPostResponse, tags=["post_likes"])
def get_liked_posts(current_user: User = Depends(get_current_user)):
    liked_posts = current_user.liked_posts
    return {"liked_posts": liked_posts}


@router.post("/post/{post_id}/favorite", tags=["favorite_posts"])
def favorite_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post in current_user.favorites:
        current_user.favorites.remove(post)
        db.commit()
        return HTTPException(status_code=status.HTTP_200_OK, detail="De Favored!")
    current_user.favorites.append(post)
    db.commit()
    return {"status": "Added to favorites!"}


@router.get("/favorites", response_model=FavoritesUserPosts, tags=["favorite_posts"])
def get_favorites(current_user: User = Depends(get_current_user)):
    favorite_posts = current_user.favorites
    return {"favorite_posts": favorite_posts}
