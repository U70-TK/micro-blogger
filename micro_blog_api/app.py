from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import time

from models import Base, User, Post, Like, Reply, get_db, engine

# JWT settings
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Use bcrypt_sha256 to pre-hash long passwords with SHA-256 before bcrypt,
# avoiding the 72-byte bcrypt limit while remaining compatible with bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()

app = FastAPI()

# Enable CORS for development so the frontend dev server can call the API.
# In production, restrict `allow_origins` to your frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create database tables on startup, retrying until the DB is available.

    This avoids crashing when the app container starts before Postgres is ready.
    """
    retries = 10
    delay_seconds = 2
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)

# Pydantic Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    hashed_password: str


class MeOut(BaseModel):
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]


class PostCreate(BaseModel):
    content: str


class ReplyCreate(BaseModel):
    content: str


class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    username: str
    display_name: Optional[str]
    likes_count: int
    replies_count: int

    class Config:
        orm_mode = True


class ReplyOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    username: str

    class Config:
        orm_mode = True

# Utility functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user_by_username(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def authenticate_user_by_email(db: Session, email: str, provided: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    # Accept exact stored-hash match or verify plain password
    try:
        if provided == user.password_hash or verify_password(provided, user.password_hash):
            return user
    except Exception:
        return None
    return None


def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return credentials.credentials


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    # Argon2 supports long passwords; hash directly
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate using email and a client-provided hashed password.

    The endpoint accepts JSON { "email": "...", "hashed_password": "..." }.
    Authentication succeeds if either:
      - the provided `hashed_password` exactly matches the stored value (client sent final hash), OR
      - the provided value verifies as the plain password against the stored hash (client sent plain password).

    This dual approach supports clients that either send the already-hashed value
    or send plain passwords (for compatibility).
    """
    user = authenticate_user_by_email(db, req.email, req.hashed_password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=MeOut)
def read_users_me(token: str = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(token=token, db=db)
    return {"username": user.username, "email": user.email}


@app.put("/me", response_model=MeOut)
def update_me(
    update: ProfileUpdate, token: str = Depends(get_token), db: Session = Depends(get_db)
):
    user = get_current_user(token=token, db=db)
    if update.display_name is not None:
        user.display_name = update.display_name
    if update.bio is not None:
        user.bio = update.bio
    if update.avatar_url is not None:
        user.avatar_url = update.avatar_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"username": user.username, "email": user.email}


@app.get("/users/{username}")
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = (
        db.query(Post)
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    posts_out = []
    for p in posts:
        posts_out.append(
            {
                "id": p.id,
                "user_id": p.user_id,
                "content": p.content,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "username": user.username,
                "display_name": user.display_name,
                "likes_count": len(p.likes),
                "replies_count": len(p.replies),
            }
        )
    return {
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "posts": posts_out,
    }


@app.post("/posts", response_model=PostOut)
def create_post(payload: PostCreate, token: str = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(token=token, db=db)
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    if len(content) > 280:
        raise HTTPException(status_code=400, detail="Content exceeds 280 characters")
    post = Post(user_id=user.id, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "username": user.username,
        "display_name": user.display_name,
        "likes_count": 0,
        "replies_count": 0,
    }


@app.get("/posts", response_model=List[PostOut])
def get_feed(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset).all()
    out = []
    for p in posts:
        out.append(
            {
                "id": p.id,
                "user_id": p.user_id,
                "content": p.content,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "username": p.user.username,
                "display_name": p.user.display_name,
                "likes_count": len(p.likes),
                "replies_count": len(p.replies),
            }
        )
    return out


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    replies = []
    for r in post.replies:
        replies.append(
            {
                "id": r.id,
                "post_id": r.post_id,
                "user_id": r.user_id,
                "content": r.content,
                "created_at": r.created_at,
                "username": r.user.username,
            }
        )
    return {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "username": post.user.username,
        "display_name": post.user.display_name,
        "likes_count": len(post.likes),
        "replies": replies,
    }


@app.get("/get_like_numbers_by_post_id")
def get_like_numbers_by_post_id(post_id: int, db: Session = Depends(get_db)):
    """Return the number of likes for a given post id.

    Query param: ?post_id=123
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    likes_count = db.query(Like).filter(Like.post_id == post_id).count()
    return {"post_id": post_id, "likes_count": likes_count}


@app.post("/posts/{post_id}/like")
def toggle_like(post_id: int, token: str = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(token=token, db=db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.query(Like).filter(Like.post_id == post_id, Like.user_id == user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        # get the authoritative count from the DB
        likes_count = db.query(Like).filter(Like.post_id == post_id).count()
        return {"liked": False, "likes_count": likes_count}

    like = Like(user_id=user.id, post_id=post_id)
    db.add(like)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not like post")
    # get the authoritative count from the DB
    likes_count = db.query(Like).filter(Like.post_id == post_id).count()
    return {"liked": True, "likes_count": likes_count}


@app.post("/posts/{post_id}/reply", response_model=ReplyOut)
def create_reply(post_id: int, payload: ReplyCreate, token: str = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(token=token, db=db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Reply content cannot be empty")
    if len(content) > 280:
        raise HTTPException(status_code=400, detail="Reply exceeds 280 characters")
    reply = Reply(post_id=post_id, user_id=user.id, content=content)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return {
        "id": reply.id,
        "post_id": reply.post_id,
        "user_id": reply.user_id,
        "content": reply.content,
        "created_at": reply.created_at,
        "username": user.username,
    }


@app.get("/posts/{post_id}/replies", response_model=List[ReplyOut])
def get_replies(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    out = []
    for r in post.replies:
        out.append(
            {
                "id": r.id,
                "post_id": r.post_id,
                "user_id": r.user_id,
                "content": r.content,
                "created_at": r.created_at,
                "username": r.user.username,
            }
        )
    return out