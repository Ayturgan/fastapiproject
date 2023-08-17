from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

    class Config:
        from_attributes = True


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    username: str
    password: str


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    title: str
    content: str


class PostUpdate(PostBase):
    title: Optional[str]
    content: Optional[str]


class PostDelete(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    author: UserProfile

    class Config:
        from_attributes = True


class PostWithAuthorResponse(PostResponse):
    author: UserProfile


class LikedPostResponse(BaseModel):
    liked_posts: List[PostResponse]


class UserProfileWithPosts(BaseModel):
    user_profile: UserProfile
    user_posts: List[PostResponse]


class FavoritesUserPosts(BaseModel):
    favorite_posts: List[PostResponse]
