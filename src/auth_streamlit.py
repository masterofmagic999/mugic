"""
Streamlit-compatible authentication system
Modified version without Flask dependencies
"""
import os
from datetime import datetime, timedelta
import bcrypt
import jwt
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from src.database import Base, db_session
import re


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class AuthManager:
    """Manages user authentication operations - Streamlit compatible"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> tuple:
        """
        Validate username format
        Returns: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 80:
            return False, "Username must be less than 80 characters"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: str = None) -> tuple:
        """
        Register a new user
        Returns: (success, message, user_dict)
        """
        try:
            # Validate username
            valid, error = AuthManager.validate_username(username)
            if not valid:
                return False, error, None
            
            # Validate email
            if not AuthManager.validate_email(email):
                return False, "Invalid email format", None
            
            # Validate password
            valid, error = AuthManager.validate_password(password)
            if not valid:
                return False, error, None
            
            # Check if username already exists
            existing_user = db_session.query(User).filter_by(username=username).first()
            if existing_user:
                return False, "Username already taken", None
            
            # Check if email already exists
            existing_email = db_session.query(User).filter_by(email=email).first()
            if existing_email:
                return False, "Email already registered", None
            
            # Hash password using bcrypt directly
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                created_at=datetime.utcnow()
            )
            
            db_session.add(new_user)
            db_session.commit()
            
            return True, "User registered successfully", new_user.to_dict()
            
        except Exception as e:
            db_session.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> tuple:
        """
        Authenticate user and generate tokens
        Returns: (success, message, user_dict, tokens)
        """
        try:
            # Find user by username or email
            user = db_session.query(User).filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
            
            if not user:
                return False, "Invalid credentials", None, None
            
            # Check if account is active
            if not user.is_active:
                return False, "Account is inactive", None, None
            
            # Verify password using bcrypt directly
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return False, "Invalid credentials", None, None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db_session.commit()
            
            # Generate JWT tokens
            secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
            access_token = jwt.encode(
                {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                secret_key,
                algorithm='HS256'
            )
            refresh_token = jwt.encode(
                {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=30)},
                secret_key,
                algorithm='HS256'
            )
            
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
            return True, "Login successful", user.to_dict(), tokens
            
        except Exception as e:
            return False, f"Authentication failed: {str(e)}", None, None
    
    @staticmethod
    def get_user_by_id(user_id: int):
        """Get user by ID"""
        return db_session.query(User).filter_by(id=user_id).first()
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> tuple:
        """
        Update user information
        Allowed fields: full_name, email
        """
        try:
            user = db_session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return False, "User not found"
            
            # Update allowed fields
            if 'full_name' in kwargs:
                user.full_name = kwargs['full_name']
            
            if 'email' in kwargs:
                email = kwargs['email']
                if not AuthManager.validate_email(email):
                    return False, "Invalid email format"
                
                # Check if email is already taken by another user
                existing = db_session.query(User).filter(
                    User.email == email,
                    User.id != user_id
                ).first()
                
                if existing:
                    return False, "Email already in use"
                
                user.email = email
            
            db_session.commit()
            return True, "User updated successfully"
            
        except Exception as e:
            db_session.rollback()
            return False, f"Update failed: {str(e)}"
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> tuple:
        """Change user password"""
        try:
            user = db_session.query(User).filter_by(id=user_id).first()
            
            if not user:
                return False, "User not found"
            
            # Verify old password
            if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return False, "Current password is incorrect"
            
            # Validate new password
            valid, error = AuthManager.validate_password(new_password)
            if not valid:
                return False, error
            
            # Hash and update password
            user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db_session.commit()
            
            return True, "Password changed successfully"
            
        except Exception as e:
            db_session.rollback()
            return False, f"Password change failed: {str(e)}"
