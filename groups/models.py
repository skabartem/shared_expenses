from django.db import models
from users.models import Profile
import uuid
from datetime import datetime


class Group(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    created_by = models.ForeignKey(Profile, related_name='created_by', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(null=True, max_length=100)
    group_users = models.ManyToManyField(Profile, through='GroupUser')

    def __str__(self):
        return self.name


class Expense(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    title = models.CharField(null=True, max_length=100)
    price = models.FloatField(null=True)
    paid_date = models.DateTimeField(default=datetime.now(), null=True)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    split_with = models.ForeignKey(Profile, related_name='expense_split', on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.title


class GroupUser(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    balance = models.FloatField(null=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    created_expenses = models.ForeignKey(Expense, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.group} | {self.profile}'

