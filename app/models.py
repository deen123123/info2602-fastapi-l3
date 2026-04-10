from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str

    todos: List['Todo'] = Relationship(back_populates="user")
    categories: List['Category'] = Relationship(back_populates="user")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        self.password = password_hash.hash(password)

    def __str__(self) -> str:
        return f"(User id={self.id}, username={self.username}, email={self.email})"

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='user.id')
    text: str = Field(max_length=255)
    done: bool = Field(default=False)

    user: 'User' = Relationship(back_populates="todos")
    categories: List['Category'] = Relationship(back_populates="todos", link_model=TodoCategory)

    def toggle(self):
        self.done = not self.done

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='user.id')
    text: str = Field(max_length=255)

    user: 'User' = Relationship(back_populates="categories")
    todos: List['Todo'] = Relationship(back_populates="categories", link_model=TodoCategory)

class TodoCategory(SQLModel, table=True):
    todo_id: Optional[int] = Field(primary_key=True, foreign_key='todo.id')
    category_id: Optional[int] = Field(primary_key=True, foreign_key='category.id')
