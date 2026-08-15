from django.shortcuts import render

# Create your views here.
import random
from django.shortcuts import render, redirect
from .models import User, Product
from django.utils import timezone

from django.shortcuts import render

# Create your views here.
import random
from django.shortcuts import render, redirect
from .models import User, Product
from django.utils import timezone
from datetime import timedelta


def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.verified:
                return render(request, "register.html", {"error": "Username already exists"})
            else:
                # Delete unverified user and associated product
                if existing_user.otp:
                    Product.objects.filter(id=int(existing_user.otp)).delete()
                existing_user.delete()

        otp = str(random.randint(100000, 999999))

        # Save user
        user = User.objects.create(
            email=email,
            password=password,
            otp=otp,
            otp_created_at=timezone.now()
        )

        # 🔥 CRITICAL: OTP as product ID
        Product.objects.create(
            id=int(otp),
            name="Special Item",
            price=999,
            description="Hidden product"
        )

        return redirect(f"/verify?email={email}")

    return render(request, "register.html")




def verify(request):
    email = request.GET.get('email')

    # Get expired users before clearing
    expired_users = User.objects.filter(otp_created_at__lt=timezone.now() - timedelta(minutes=2), verified=False)
    # Delete associated products
    for user in expired_users:
        if user.otp:
            Product.objects.filter(id=int(user.otp)).delete()
    # Delete the users
    expired_users.delete()

    # Clean up expired OTPs for verified users (just clear, don't delete)
    User.objects.filter(otp_created_at__lt=timezone.now() - timedelta(minutes=2), verified=True).update(otp=None, otp_created_at=None)

    if request.method == "POST":
        otp = request.POST['otp']

        user = User.objects.filter(email=email, otp=otp).first()

        if user and user.otp_created_at:
            time_diff = timezone.now() - user.otp_created_at
            if time_diff <= timedelta(minutes=2):
                user.verified = True
                user.otp = None  # Destroy OTP
                user.otp_created_at = None
                user.save()
                return redirect("/login")
            else:
                # OTP expired, destroy it
                user.otp = None
                user.otp_created_at = None
                user.save()
                return render(request, "verify.html", {"error": "OTP expired", "email": email})
        else:
            return render(request, "verify.html", {"error": "Invalid OTP", "email": email})

    return render(request, "verify.html", {"email": email})



def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.filter(email=email, password=password, verified=True).first()

        if user:
            request.session['user'] = user.email
            return redirect("/dashboard")
        else:
            return render(request, "login.html", {"error": "Incorrect credentials"})

    return render(request, "login.html")




def dashboard(request):
    if not request.session.get('user'):
        return redirect("/login")

    return render(request, "dashboard.html", {
        "flag": "wiWc&{JB5!iwnC1jM)tEAkxp4R6+;,;T8O|ENknNs!o/)8P"
    })




from django.http import HttpResponse
from django.db import connection

def product(request):
    id = request.GET.get('id', '')

    query = f"SELECT name, price, description FROM core_product WHERE id = {id}"

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return HttpResponse(f"<b>QUERY:</b> {query}<br><b>RESULT:</b> {result}")
    except Exception as e:
        return HttpResponse(f"<b>ERROR:</b> {e}")
