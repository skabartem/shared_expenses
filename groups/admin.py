from django.contrib import admin
from .models import *

admin.site.register(Group)
admin.site.register(GroupUser)
admin.site.register(PaymentToSettle)
admin.site.register(Expense)
admin.site.register(ExpenseComment)
admin.site.register(ExpenseImpact)
