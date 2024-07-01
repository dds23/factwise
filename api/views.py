from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Team, Board, Task
from .serializers import UserSerializer, TeamSerializer, BoardSerializer, TaskSerializer
from datetime import datetime
import os
import re


class UserViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"id": serializer.data['id']})
        return Response(serializer.errors, status=400)

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def describe_user(self, request):
        user_id = request.data.get('id')
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    @action(detail=False, methods=['post'])
    def update_user(self, request):
        user_id = request.data.get('id')
        user_data = request.data.get('user')
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=user_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "User updated successfully"})
            return Response(serializer.errors, status=400)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    @action(detail=False, methods=['post'])
    def get_user_teams(self, request):
        user_id = request.data.get('id')
        try:
            user = User.objects.get(id=user_id)
            teams = Team.objects.filter(admin=user)
            serializer = TeamSerializer(teams, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class TeamViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"id": serializer.data['id']})
        return Response(serializer.errors, status=400)

    def list(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def describe_team(self, request):
        team_id = request.data.get('id')
        try:
            team = Team.objects.get(id=team_id)
            serializer = TeamSerializer(team)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

    @action(detail=False, methods=['post'])
    def update_team(self, request):
        team_id = request.data.get('id')
        team_data = request.data.get('team')
        try:
            team = Team.objects.get(id=team_id)
            serializer = TeamSerializer(team, data=team_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "Team updated successfully"})
            return Response(serializer.errors, status=400)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

    @action(detail=False, methods=['post'])
    def add_users_to_team(self, request):
        team_id = request.data.get('id')
        user_ids = request.data.get('users')
        try:
            team = Team.objects.get(id=team_id)
            if len(user_ids) > 50:
                return Response({"error": "Cannot add more than 50 users"}, status=400)
            users = User.objects.filter(id__in=user_ids)
            if users.count() != len(user_ids):
                return Response({"error": "Some users not found"}, status=404)
            team.users.add(*users)
            return Response({"status": "Users added"})
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

    @action(detail=False, methods=['post'])
    def remove_users_from_team(self, request):
        team_id = request.data.get('id')
        user_ids = request.data.get('users')
        try:
            team = Team.objects.get(id=team_id)
            if len(user_ids) > 50:
                return Response({"error": "Cannot remove more than 50 users"}, status=400)
            users = User.objects.filter(id__in=user_ids)
            if users.count() != len(user_ids):
                return Response({"error": "Some users not found"}, status=404)
            team.users.remove(*users)
            return Response({"status": "Users removed"})
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

    @action(detail=False, methods=['post'])
    def list_team_users(self, request):
        team_id = request.data.get('id')
        try:
            team = Team.objects.get(id=team_id)
            users = team.users.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)


class BoardViewSet(viewsets.ViewSet):
    def create(self, request):
        data = request.data.copy()
        data['user'] = data.pop('user_id', None)
        data['team'] = data.pop('team_id', None)
        serializer = BoardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"id": serializer.data['id']})
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'])
    def close_board(self, request):
        board_id = request.data.get('id')
        try:
            board = Board.objects.get(id=board_id)
            if board.status == 'CLOSED':
                return Response({"error": "Board is already closed"}, status=400)
            incomplete_tasks = Task.objects.filter(
                board=board, status__in=['OPEN', 'IN_PROGRESS'])
            if incomplete_tasks.exists():
                return Response({"error": "Cannot close board with incomplete tasks"}, status=400)
            board.status = 'CLOSED'
            board.save()
            return Response({"status": "Board closed"})
        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=404)

    @action(detail=False, methods=['post'])
    def add_task(self, request):
        data = request.data.copy()
        data['user'] = data.pop('user_id', None)
        data['board'] = data.pop('board_id', None)
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            board_id = request.data.get('board_id')
            try:
                board = Board.objects.get(id=board_id)
                if board.status != 'OPEN':
                    return Response({"error": "Cannot add task to a closed board"}, status=400)
                serializer.save(board=board)
                return Response({"id": serializer.data['id']})
            except Board.DoesNotExist:
                return Response({"error": "Board not found"}, status=404)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'])
    def update_task_status(self, request):
        task_id = request.data.get('id')
        status = request.data.get('status')
        try:
            task = Task.objects.get(id=task_id)
            task.status = status
            task.save()
            return Response({"status": "Task status updated"})
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

    @action(detail=False, methods=['post'])
    def list_boards(self, request):
        team_id = request.data.get('id')
        try:
            team = Team.objects.get(id=team_id)
            boards = Board.objects.filter(team=team, status='OPEN')
            serializer = BoardSerializer(boards, many=True)
            return Response(serializer.data)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

    @action(detail=False, methods=['post'])
    def export_board(self, request):
        board_id = request.data.get('id')
        try:
            board = Board.objects.get(id=board_id)
            tasks = Task.objects.filter(board=board)

            # Create a formatted string for the board and its tasks
            board_info = (
                f"Board: {board.name}\n"
                f"Description: {board.description}\n"
                f"Team: {board.team.name}\n"
                f"Creation Time: {board.creation_time}\n"
                f"Status: {board.status}\n"
                "\nTASKS:\n\n"
            )

            # Organize tasks by status
            tasks_by_status = {
                'To Do': tasks.filter(status='OPEN'),
                'In Progress': tasks.filter(status='IN_PROGRESS'),
                'Done': tasks.filter(status='COMPLETE')
            }
            
            task_info = ""
            for status, tasks in tasks_by_status.items():
                task_info += f"{status}:\n"
                if tasks:
                    task_len = len(tasks)
                    for i in range(task_len):
                        task = tasks[i]
                        end = '\n'
                        if i == task_len - 1:
                            end += '\n'

                        task_info += (
                            f"  - Task {task.id}: {task.title}\n"
                            f"    Description: {task.description}\n"
                            f"    Assigned to: {task.user.name}\n"
                            f"    Creation Time: {task.creation_time}\n"
                            f"    Status: {task.status}\n"
                            f"{end}"
                        )
                else:
                    task_info += "  No tasks"
                    if status != 'Done':
                        task_info += '\n\n\n'
                    print('ti = ', task_info)

            content = board_info + task_info

            # Ensure the 'out' directory exists
            if not os.path.exists('out'):
                os.makedirs('out')

            # Sanitize the board name to be used in the file name
            sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', board.name)
            readable_timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            file_name = f"{sanitized_name}_{readable_timestamp}.txt"
            file_path = os.path.join('out', file_name)

            with open(file_path, 'w') as f:
                f.write(content)

            return Response({"out_file": file_name})

        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=404)
