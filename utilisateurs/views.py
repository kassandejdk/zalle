from django.shortcuts import render,redirect
from django.core.mail import BadHeaderError
from .forms import UserForm, ProfileForm, LoginForm
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
from .models import OTP,Transaction,Subscription
from django.contrib import messages
from .forms import UserUpdateForm


import requests
import json
from datetime import datetime
import random
from django.contrib import messages

# Create your views here.
def acceuil(request):
    return render(request,'utilisateurs/index.html')

def generate_otp():
    return random.randint(100000, 999999)

def send_otp(email, otp):
    subject = 'Votre OTP pour confirmer votre inscription'
    message = f'Votre code OTP {otp}'
    from_email = 'izalle245@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    try:
        send_mail(subject, message, from_email, recipient_list)
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    except Exception as e:
        return HttpResponse(f'An error occurred: {e}')


def register(request):
    registered = False
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True
            otp_code = generate_otp()
            OTP.objects.create(user=user, code=otp_code)
            send_otp(user.email, otp_code)
            request.session['requires_otp'] = True  # Set session variable
            return HttpResponseRedirect('login')
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    content = {
        'registered': registered,
        'form1': user_form,
        'form2': profile_form,
    }
    return render(request, 'utilisateurs/register.html', content)

def user_login(request):
    error_message = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            otp = form.cleaned_data.get('otp')

            users = User.objects.filter(username=username) | User.objects.filter(email=username) | User.objects.filter(profile__phone_number=username)
            
            if users.exists():
                user = users.first()
                user_auth = authenticate(username=user.username, password=password)
                
                if user_auth is not None:
                    if user_auth.is_active:
                        if request.session.get('requires_otp', False):
                            otp_instance = OTP.objects.filter(user=user, code=otp).first()
                            
                            if otp_instance:
                                login(request, user_auth)
                                otp_instance.delete()
                                request.session.pop('requires_otp', None)
                                return HttpResponseRedirect('/')
                            else:
                                error_message = "OTP invalide."
                        else:
                            login(request, user_auth)
                            return HttpResponseRedirect('/')
                    else:
                        error_message = "L'utilisateur est désactivé."
                else:
                    error_message = "Mot de passe incorrect."
            else:
                error_message = "Utilisateur non trouvé."
        else:
            error_message = "Formulaire invalide. Veuillez vérifier les informations fournies."
    
    else:
        form = LoginForm()
    
    return render(request, 'utilisateurs/login.html', {'error_message': error_message, 'form': form, 'requires_otp': request.session.get('requires_otp', False)})
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/') # on a pas besoin de page ici

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('acceuil')  # Assurez-vous que 'home' est défini dans vos URLs
    else:
        user_form = UserUpdateForm(instance=request.user)

    context = {
        'user_form': user_form
    }

    return render(request, 'utilisateurs/update_profile.html', context)



######################################""""""

#api ligdicash


@login_required
def choose_subscription(request):
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        subscription, created = Subscription.objects.get_or_create(user=request.user)
        subscription.subscription_type = subscription_type
        subscription.save()

        # Effectuer le paiement
        id_transac = f'TRANS{random.randint(0, 9999)}{datetime.now().strftime("%Y%m%d%H%M%S")}'
        user = request.user
        response = payement_redirection(id_transac, subscription_type)

        if response.get('response_code') == '00':
            token = response.get("token")
            redirect_url = response.get("response_text")

            Transaction.objects.create(
                user=user,
                transID=id_transac,
                status="pending",
                token=token 
            )

            request.session['transaction_id'] = id_transac
            return redirect(redirect_url)
        else:
            return render(request, 'utilisateurs/cancel.html')

    return render(request, 'utilisateurs/choose_subscription.html')

def payement_redirection(trans_id, subscription_type):
    price = "10" if subscription_type == "standard" else "5"
    description = "Abonnement Standard" if subscription_type == "standard" else "Abonnement Premium"
    
    url = "https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/create"
    headers = {
        "Apikey": "MAGPMLT3QFJLIPUDN",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZF9hcHAiOjE1MDA5LCJpZF9hYm9ubmUiOjg5OTQyLCJkYXRlY3JlYXRpb25fYXBwIjoiMjAyNC0wNC0wOCAwODozMjoyNCJ9.NRcyHfFO8OyaXOaklZ2DJ2Arf-gV8OXGfMIELQzdw88",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "commande": {
            "invoice": {
                "items": [
                    {
                        "name": description,
                        "description": description,
                        "quantity": 1,
                        "unit_price": price,
                        "total_price": price
                    }
                ],
                "total_amount": price,
                "devise": "XOF",
                "description": description,
                "customer": "",
                "customer_firstname": "Prenom du client",
                "customer_lastname": "Nom du client",
                "customer_email": "edlign17@gmail.com"
            },
            "store": {
                "name": "Apprentissage",
                "website_url": "http://localhost:8000/"
            },
            "actions": {
                "cancel_url": "http://127.0.0.1:8000/cancel/",
                "return_url": "http://localhost:8000/success",
                "callback_url": "http://localhost:8000/success/"
            },
            "custom_data": {
                "transaction_id": trans_id
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    return response.json()

@login_required
def cancel(request):
    return render(request, 'cancel.html')

@login_required
def info_payement(request):
    return render(request, 'payement.html')

def check_payment_status(token):
    url = f"https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/confirm/?invoiceToken={token}"
    headers = {
        "Apikey": "MAGPMLT3QFJLIPUDN",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZF9hcHAiOjE1MDA5LCJpZF9hYm9ubmUiOjg5OTQyLCJkYXRlY3JlYXRpb25fYXBwIjoiMjAyNC0wNC0wOCAwODozMjoyNCJ9.NRcyHfFO8OyaXOaklZ2DJ2Arf-gV8OXGfMIELQzdw88",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        return {"error": "HTTP Error", "message": str(errh)}
    except requests.exceptions.RequestException as err:
        return {"error": "Request Exception", "message": str(err)}

@login_required
def success(request):
    transaction_id = request.session.get('transaction_id')
    if transaction_id:
        try:
            payment = Transaction.objects.get(transID=transaction_id)
            payment_data = check_payment_status(payment.token)

            if payment_data.get("status") == "completed":
                payment.status = "completed"
                payment.save()
                return redirect('acceuil')
            else:
                return redirect('cancel')
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaction introuvable. Veuillez réessayer.')
    else:
        messages.error(request, 'Erreur de transaction. Veuillez réessayer.')

    return render(request, 'utilisateurs/error.html')  
    
