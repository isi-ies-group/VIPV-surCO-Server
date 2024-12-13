from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserCredentials(Base):
    """
    UserCredentials table model

    Attributes
    ----------
    id: Integer, primary key
    username: String, max length 15, not nullable
    email: String, max length 80, not nullable
    passhash: String, max length 50, not nullable
    salt: String, max length 50, not nullable

    See also
    --------
    SessionFiles
       Table model for storing user files, referenced by user_id
    """
    __tablename__ = "UserCredentials"

    id = Column(Integer, primary_key=True)
    username = Column(String(21), nullable=False)
    email = Column(String(80), nullable=False)
    passhash = Column(String(50), nullable=False)
    salt = Column(String(50), nullable=False)

    def __init__(self, username, email, passhash, salt):
        self.username = username
        self.email = email
        self.passhash = passhash
        self.salt = salt

    def __repr__(self):
        return f"<User {self.id}>"


class SessionFiles(Base):
    """
    SessionFiles table model

    Attributes
    ----------
    id: Integer, primary key
    user_id: Integer, foreign key to UserCredentials.id
    filename: String, max length 100, not nullable

    See also
    --------
    UserCredentials
       Table model for storing user credentials, referenced by user_id
    """
    __tablename__ = "SessionFiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("UserCredentials.id"))
    filename = Column(String(100), nullable=False)

    def __init__(self, user_id, filename):
        self.user_id = user_id
        self.filename = filename

    def __repr__(self):
        return f"<File {self.id}>"
