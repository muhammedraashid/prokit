from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f'{self.user} s wallet - {self.balance}'


class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOISES = [
        ('debit','Debited'),
        ('credit','Credited')
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_at = models.DateTimeField(auto_now_add=True)
    transaction_type=models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOISES)

    def __str__(self):
        return f'{self.wallet.user} - {self.amount} - {self.transaction_type}'