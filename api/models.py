from django.db import models


class User(models.Model):
    name = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=64)
    creation_time = models.DateTimeField(auto_now_add=True)


class Team(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128)
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='admin_teams')
    users = models.ManyToManyField(User, related_name='teams')
    creation_time = models.DateTimeField(auto_now_add=True)


class Board(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='OPEN')  # OPEN or CLOSED


class Task(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    # OPEN, IN_PROGRESS, COMPLETE
    status = models.CharField(max_length=12, default='OPEN')
