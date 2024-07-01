# Project Planner API

## Overview

This project implements a team project planner tool using Django. The tool consists of APIs for managing users, teams, and project boards.

## Features

- User Management
- Team Management
- Project Board and Task Management

## Thought Process

1. **Models**: Defined models for Users, Teams, Boards, and Tasks.
2. **Serializers**: Created serializers to convert model instances to and from JSON.
3. **Views**: Implemented viewsets to handle API requests.
4. **URLs**: Configured URL routing for the API.
5. **Persistence**: Used Django ORM for database operations and ensured data is saved in the `db` folder.

## Assumptions

- The application uses Django's ORM for database operations.
- SQLite3 is used as the database.
- The `out` folder is used for exporting board data to text files.

## Running the Project

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

3. Start the server:
    ```bash
    python manage.py runserver
    ```

## API Endpoints

- `POST /api/users/`: Create a new user.
- `GET /api/users/`: List all users.
- `POST /api/users/describe_user/`: Describe a user.
- `POST /api/users/update_user/`: Update a user.
- `POST /api/users/get_user_teams/`: Get teams of a user.
- `POST /api/teams/`: Create a new team.
- `GET /api/teams/`: List all teams.
- `POST /api/teams/describe_team/`: Describe a team.
- `POST /api/teams/update_team/`: Update a team.
- `POST /api/teams/add_users_to_team/`: Add users to a team.
- `POST /api/teams/remove_users_from_team/`: Remove users from a team.
- `POST /api/teams/list_team_users/`: List users of a team.
- `POST /api/boards/`: Create a new board.
- `POST /api/boards/close_board/`: Close a board.
- `POST /api/boards/add_task/`: Add a task to a board.
- `POST /api/boards/update_task_status/`: Update the status of a task.
- `POST /api/boards/list_boards/`: List all open boards for a team.
- `POST /api/boards/export_board/`: Export a board to a text file.

## Dependencies

- Django
- Django REST Framework
- Django filter
