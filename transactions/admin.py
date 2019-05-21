from django.contrib import admin

from .models import Transaction, Deposit, Savings, ClientAccount

admin.site.register(Transaction)
admin.site.register(Deposit)
admin.site.register(Savings)
admin.site.register(ClientAccount)
