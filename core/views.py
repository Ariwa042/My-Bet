from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from betting.models import Odds
from .models import League, Team, Match, Deposit, Withdrawal, Cryptocurrency
from .forms import DepositForm, WithdrawalForm
from .utils import generate_qr_code


from account.models import Profile, User
from django.contrib.auth import get_user_model
from decimal import Decimal

def home(request):
    """
    Render the home page with a list of leagues, teams, and matches.
    """
    context = {
        'leagues': League.objects.all(),
        'teams': Team.objects.all(),
        'matches': Match.objects.all(),
    }
    return render(request, 'core/home.html', context)

def league_detail(request, league_id):
    """
    Render the detail page for a specific league, including its teams and matches.
    """
    league = get_object_or_404(League, id=league_id)
    context = {
        'league': league,
        'teams': league.teams.all(),
        'matches': league.matches.all(),
    }
    return render(request, 'core/league_detail.html', context)

def team_detail(request, team_id):
    """
    Render the detail page for a specific team, including its matches.
    """
    team = get_object_or_404(Team, id=team_id)
    matches = Match.objects.filter(home_team=team) | Match.objects.filter(away_team=team)
    context = {
        'team': team,
        'matches': matches,
    }
    return render(request, 'core/team_detail.html', context)

def match_list(request):
    """
    Render a list of all matches.
    """
    context = {
        'matches': Match.objects.all(),
    }
    return render(request, 'core/match_list.html', context)

def match_detail(request, match_id):
    """
    Render the detail page for a specific match, including its odds.
    """
    match = get_object_or_404(Match, id=match_id)
    context = {
        'match': match,
        'odds': Odds.objects.filter(match=match),
    }
    return render(request, 'core/match_detail.html', context)

@login_required
def deposit(request):
    """
    Handle user deposits.
    """
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            # Store the form data temporarily in the session
            form_data = {
                'cryptocurrency_id': form.cleaned_data.get('cryptocurrency').id,  # Store the ID instead of the whole object
                'amount': str(form.cleaned_data.get('amount'))
            }
            request.session['deposit_form_data'] = form_data
            request.session.modified = True  # Ensure session is marked as changed
            # Optional: add a debug message
            messages.info(request, "Deposit data stored in session: %s" % form_data)
            return redirect('core:deposit_instructions')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepositForm()
    context = {'form': form}
    return render(request, 'core/deposit.html', context)

def deposit_instructions(request):
    form_data = request.session.get('deposit_form_data')
    if not form_data:
        messages.error(request, 'No deposit data found. Please try again.')
        return redirect('core:deposit')
    
    try:
        cryptocurrency = Cryptocurrency.objects.get(id=form_data.get('cryptocurrency_id'))
    except Cryptocurrency.DoesNotExist:
        return redirect('core:deposit')

    amount = Decimal(form_data.get('amount'))
    qr_code = generate_qr_code(cryptocurrency.wallet_address)

    if request.method == 'POST':
        # Finalize the deposit
        Deposit.objects.create(
            user=request.user,
            cryptocurrency=cryptocurrency,
            amount=amount,
        )
        # Clear session data
        request.session.pop('deposit_form_data', None)
        return redirect('core:transaction_history')
    
    return render(request, 'core/deposit_instructions.html', {
        'cryptocurrency': cryptocurrency,
        'amount': form_data.get('amount'),
        'qr_code': qr_code,
    })

@login_required
def withdrawal(request):
    """
    Handle user withdrawals.
    """
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user
            withdrawal_amount = withdrawal.amount

            # Check if the user has enough balance
            profile = Profile.objects.get(user=request.user)
            if profile.balance >= withdrawal_amount:
                withdrawal.status = 'pending'
                withdrawal.save()
                return redirect('core:transaction_history')
            else:
                messages.error(request, 'Insufficient balance for this withdrawal.')
                return redirect('core:withdrawal')
    else:
        form = WithdrawalForm()
    context = {'form': form}
    return render(request, 'core/withdrawal.html', context)

@login_required
@login_required
def transaction_history(request):
    deposits = Deposit.objects.filter(
        user=request.user).order_by('-created_at')
    withdrawals = Withdrawal.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'core/transaction_history.html', {
        'deposits': deposits,
        'withdrawals': withdrawals,
    })