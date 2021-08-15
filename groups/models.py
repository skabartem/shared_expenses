from django.db import models
from users.models import Profile
import uuid
from datetime import datetime


class Group(models.Model):
    id = models.UUIDField(uuid.uuid4, primary_key=True, unique=True)
    created_by = models.ForeignKey(Profile, related_name='created_by', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(null=True, max_length=100)
    group_users = models.ManyToManyField(Profile, through='GroupUser')


class Expense(models.Model):
    id = models.UUIDField(uuid.uuid4, primary_key=True, unique=True)
    title = models.CharField(null=True, max_length=100)
    price = models.FloatField(null=True)
    paid_date = models.DateTimeField(default=datetime.now(), null=True)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    split_with = models.ForeignKey(Profile, related_name='expense_split', on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GroupUser(models.Model):
    id = models.UUIDField(uuid.uuid4, primary_key=True, unique=True)
    balance = models.FloatField(null=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    created_expenses = models.ForeignKey(Expense, null=True, blank=True, on_delete=models.CASCADE)

