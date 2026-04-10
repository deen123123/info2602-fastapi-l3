# ... (keep all existing imports and commands) ...
from sqlmodel import select
from sqlalchemy import or_, and_

# ... (keep all existing commands) ...

@cli.command()
def add_task(
    username: str = typer.Argument(..., help="Username to add todo for"),
    task: str = typer.Argument(..., help="Text of the todo item")
):
    """Add a new todo task for a specific user."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        todo = Todo(text=task, user_id=user.id)
        user.todos.append(todo)
        db.add(user)
        db.commit()
        print(f"Task '{task}' added for user '{username}' (ID: {todo.id})")

@cli.command()
def toggle_todo(
    todo_id: int = typer.Argument(..., help="ID of todo to toggle"),
    username: str = typer.Argument(..., help="Username who owns the todo")
):
    """Toggle the done state of a specific todo item."""
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("This todo doesn't exist")
            return
        if todo.user.username != username:
            print(f"This todo doesn't belong to {username}")
            return

        todo.toggle()
        db.add(todo)
        db.commit()
        print(f"Todo '{todo.text}' done state set to {todo.done}")

@cli.command()
def list_todo_categories(
    todo_id: int = typer.Argument(..., help="ID of todo to list categories for"),
    username: str = typer.Argument(..., help="Username who owns the todo")
):
    """List all categories assigned to a specific todo."""
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
            return
        elif todo.user.username != username:
            print("Todo doesn't belong to that user")
            return
        else:
            if not todo.categories:
                print("No categories assigned to this todo")
            else:
                print(f"Categories for todo {todo_id}: {[cat.text for cat in todo.categories]}")

@cli.command()
def create_category(
    username: str = typer.Argument(..., help="Username to create category for"),
    cat_text: str = typer.Argument(..., help="Category text/name")
):
    """Create a new category for a user (skips if already exists)."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return

        category = db.exec(
            select(Category).where(
                and_(Category.text == cat_text, Category.user_id == user.id)
            )
        ).one_or_none()
        if category:
            print("Category exists! Skipping creation")
            return
        
        category = Category(text=cat_text, user_id=user.id)
        db.add(category)
        db.commit()
        print(f"Category '{cat_text}' added for user '{username}' (ID: {category.id})")

@cli.command()
def list_user_categories(
    username: str = typer.Argument(..., help="Username to list categories for")
):
    """List all categories created by a specific user."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        categories = db.exec(select(Category).where(Category.user_id == user.id)).all()
        if not categories:
            print("No categories found for this user")
        else:
            print(f"Categories for '{username}': {[category.text for category in categories]}")

@cli.command()
def assign_category_to_todo(
    username: str = typer.Argument(..., help="Username who owns todo and category"),
    todo_id: int = typer.Argument(..., help="ID of todo to assign category to"),
    category_text: str = typer.Argument(..., help="Category text/name to assign")
):
    """Assign a category to a todo (creates category if it doesn't exist)."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        
        # Check if category exists, create if not
        category = db.exec(
            select(Category).where(
                and_(Category.text == category_text, Category.user_id == user.id)
            )
        ).one_or_none()
        if not category:
            category = Category(text=category_text, user_id=user.id)
            db.add(category)
            db.commit()
            print(f"Category '{category_text}' didn't exist for user, creating it (ID: {category.id})")
        
        # Check if todo exists and belongs to user
        todo = db.exec(
            select(Todo).where(
                and_(Todo.id == todo_id, Todo.user_id == user.id)
            )
        ).one_or_none()
        if not todo:
            print("Todo doesn't exist for user")
            return
        
        # Assign category to todo
        todo.categories.append(category)
        db.add(todo)
        db.commit()
        print(f"Added category '{category_text}' to todo '{todo.text}'")

@cli.command()
def list_todos():
    """List all todos with ID, text, username, and done status."""
    with get_session() as db:
        todos = db.exec(select(Todo)).all()
        if not todos:
            print("No todos found")
            return
        
        print("All Todos:")
        print("-" * 60)
        for todo in todos:
            print(f"ID: {todo.id:3d} | Text: {todo.text:<40} | User: {todo.user.username:<12} | Done: {todo.done}")

@cli.command()
def delete_todo(
    todo_id: int = typer.Argument(..., help="ID of todo to delete")
):
    """Delete a todo by its ID."""
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print(f"Todo with ID {todo_id} doesn't exist")
            return
        
        username = todo.user.username
        db.delete(todo)
        db.commit()
        print(f"Todo ID {todo_id} ('{todo.text}') deleted for user '{username}'")

@cli.command()
def complete_all_user_todos(
    username: str = typer.Argument(..., help="Username whose todos to mark complete")
):
    """Mark all todos for a specific user as complete."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        
        todos = db.exec(select(Todo).where(Todo.user_id == user.id)).all()
        if not todos:
            print(f"No todos found for user '{username}'")
            return
        
        completed_count = 0
        for todo in todos:
            if not todo.done:
                todo.done = True
                db.add(todo)
                completed_count += 1
        
        db.commit()
        print(f"Marked {completed_count} todos as complete for user '{username}'")

if __name__ == "__main__":
    cli()
