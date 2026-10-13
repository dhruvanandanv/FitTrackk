from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.user import User, UserProfile
from backend.app.schemas.auth import UserRegister, UserLogin
from backend.app.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    def register_user(db: Session, data: UserRegister) -> tuple[User, str]:
        # Check if email already registered
        existing = db.query(User).filter(User.email == data.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists.",
            )

        # Hash password with Argon2
        hashed = hash_password(data.password)

        new_user = User(
            name=data.name.strip(),
            email=data.email.lower().strip(),
            password_hash=hashed,
        )
        db.add(new_user)
        db.flush()  # populate new_user.id

        # Create default profile
        profile = UserProfile(
            user_id=new_user.id,
            fitness_goal="maintain",
            preferred_units="metric",
            daily_step_target=10000,
            daily_water_target=2500,
            daily_sleep_target=8.0,
        )
        db.add(profile)
        db.commit()
        db.refresh(new_user)

        token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
        return new_user, token

    @staticmethod
    def authenticate_user(db: Session, data: UserLogin) -> tuple[User, str]:
        user = db.query(User).filter(User.email == data.email.lower().strip()).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        token = create_access_token({"sub": str(user.id), "email": user.email})
        return user, token
