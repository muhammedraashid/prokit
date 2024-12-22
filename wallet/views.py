from django.shortcuts import render, redirect, get_object_or_404
from .models import Wallet, WalletTransaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# Create your views here.


@login_required
def add_to_wallet(request):
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount', '0'))  
            if amount < 0 :
                messages.error(request, "Invalid amount entered!")
                return redirect('wallet')
                
        except ValueError:
            messages.error(request, "Invalid amount entered!")
            return redirect('wallet')
        
        wallet = request.user.wallet
        wallet.balance += amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='credit'
        )
        messages.success(request, f"₹{amount} credited to your wallet")
        return redirect('wallet')
    
    return render(request,'wallet.html')

def wallet(request):
    wallet = request.user.wallet
    wallet_transactions = wallet.transactions.all().order_by('-transaction_at')
    context={
        "wallet":wallet,
        'wallet_transactions':wallet_transactions
    }
    return render(request, 'wallet.html', context)
