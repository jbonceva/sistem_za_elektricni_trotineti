from datetime import timedelta
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import (
    Scooter,
    Reservation,
    Rental,
    Payment,
    ScooterTracking,
    Zone,
    Penalty,
    Employee,
    Maintenance,
)

SKOPJE_ROUTES = [
    # Centar
    (41.9981, 21.4254),
    # Debar Maalo
    (42.0018, 21.4165),
    # City Mall
    (42.0041, 21.3917),
    # Karposh
    (42.0005, 21.3902),
    # Ramstore
    (41.9946, 21.4315),
    # East Gate
    (41.9817, 21.4675),
    # Aerodrom
    (41.9853, 21.4658),
    # Novo Lisiche
    (41.9802, 21.4755),
    # Kisela Voda
    (41.9805, 21.4355),
    # Vodno
    (41.9870, 21.4098),
    # Taftalidze
    (42.0035, 21.3780),
    # Chair
    (42.0108, 21.4525),
    # Avtokomanda
    (42.0050, 21.4650),
    # GTC
    (41.9957, 21.4313),
    # Kale
    (42.0010, 21.4338),
]

def get_zone_for_location(longitude):

    if longitude > 21.45:
        return Zone.objects.filter(name='Karposh 2').first()

    elif longitude < 21.41:
        return Zone.objects.filter(name='Karposh').first()

    else:
        return Zone.objects.filter(name='Center').first()

def home(request):

    scooters = Scooter.objects.all()

    reservations = Reservation.objects.filter(status='active')

    rides = Rental.objects.filter(status='active')

    context = {
        'scooters': scooters,
        'reservations': reservations,
        'rides': rides,
    }

    return render(request, 'home.html', context)

def scooter_detail(request, scooter_id):

    scooter = get_object_or_404(Scooter, id=scooter_id)

    tracking_history = scooter.scootertracking_set.all().order_by('-timestamp')

    context = {
        'scooter': scooter,
        'tracking_history': tracking_history,
    }

    return render(request, 'scooter_detail.html', context)

@login_required
def reserve_scooter(request, scooter_id):

    scooter = get_object_or_404(Scooter, id=scooter_id)

    if scooter.status != 'available':
        return redirect('/')

    Reservation.objects.create(
        username=request.user,
        scooter=scooter,
        reserved_from=timezone.now(),
        reserved_until=timezone.now() + timedelta(hours=1),
        status='active'
    )

    scooter.status = 'reserved'
    scooter.save()

    return redirect('/')

@login_required
def reserve_scooter(request, scooter_id):

    scooter = get_object_or_404(Scooter, id=scooter_id)

    if scooter.status != 'available':
        return redirect('/')

    Reservation.objects.create(
        username=request.user,
        scooter=scooter,
        reserved_from=timezone.now(),
        reserved_until=timezone.now() + timedelta(hours=1),
        status='active'
    )

    scooter.status = 'reserved'
    scooter.save()

    return redirect('/')

def reservations(request):

    reservations = Reservation.objects.all().order_by('-reserved_from')

    return render(request, 'reservations.html', {
        'reservations': reservations
    })

def cancel_reservation(request, reservation_id):

    reservation = get_object_or_404(Reservation, id=reservation_id)

    reservation.status = 'cancelled'
    reservation.save()

    scooter = reservation.scooter
    scooter.status = 'available'
    scooter.save()

    return redirect('/reservations/')

def delete_reservation(request, reservation_id):

    reservation = get_object_or_404(Reservation, id=reservation_id)

    scooter = reservation.scooter
    scooter.status = 'available'
    scooter.save()

    reservation.delete()

    return redirect('/reservations/')

@login_required
def start_ride(request, reservation_id):

    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.username != request.user:
        return redirect('/')

    scooter = reservation.scooter

    last_tracking = scooter.scootertracking_set.last()

    zone = last_tracking.zone if last_tracking else None

    price_per_min = zone.price_per_min if zone else 7

    if request.method == 'POST':

        Rental.objects.create(
            username=request.user,
            scooter=scooter,
            location=None,
            start_time=timezone.now(),
            end_time=None,
            distance_km=0,
            total_price=0,
            status='active',
            discount_percent=0
        )

        new_location = random.choice(SKOPJE_ROUTES)

        current_zone = get_zone_for_location(new_location[1])

        ScooterTracking.objects.create(
            scooter=scooter,
            latitude=new_location[0],
            longitude=new_location[1],
            zone=current_zone,
            timestamp=timezone.now()
        )

        reservation.status = 'completed'
        reservation.save()

        scooter.status = 'rented'
        scooter.save()

        return redirect('/')

    return render(request, 'start_ride_payment.html', {
        'reservation': reservation,
        'scooter': scooter,
        'zone': zone,
        'price_per_min': price_per_min
    })

def rides(request):

    rides = Rental.objects.all().order_by('-start_time')

    return render(request, 'rides.html', {
        'rides': rides
    })

def end_ride(request, ride_id):

    ride = get_object_or_404(Rental, id=ride_id)

    ride.end_time = timezone.now()

    duration = ride.end_time - ride.start_time

    minutes = duration.total_seconds() / 60

    scooter = ride.scooter

    tracking = scooter.scootertracking_set.last()

    if tracking:
        price_per_min = tracking.zone.price_per_min
    else:
        price_per_min = 7

    total_price = minutes * price_per_min

    ride.total_price = round(total_price, 2)

    ride.status = 'completed'

    ride.save()

    Payment.objects.create(
        rental=ride,
        username=ride.username,
        amount=ride.total_price,
        payment_method='card',
        status='paid'
    )

    scooter.status = 'available'

    scooter.save()

    return redirect('/')
@login_required
def my_rides(request):

    active_rides = Rental.objects.filter(
        username=request.user,
        status='active'
    )

    completed_rides = Rental.objects.filter(
        username=request.user,
        status='completed'
    )

    active_reservations = Reservation.objects.filter(
        username=request.user,
        status='active'
    )

    payments = Payment.objects.filter(
        username=request.user
    )

    penalties = Penalty.objects.filter(
        username=request.user
    )

    context = {
        'active_rides': active_rides,
        'completed_rides': completed_rides,
        'active_reservations': active_reservations,
        'payments': payments,
        'penalties': penalties,
    }

    return render(request, 'my_rides.html', context)

@login_required
def payment(request, scooter_id):

    scooter = get_object_or_404(Scooter, id=scooter_id)

    if scooter.status != 'available':
        return redirect('/')

    if request.method == 'POST':

        Rental.objects.create(
            username=request.user,
            scooter=scooter,
            location=None,
            start_time=timezone.now(),
            end_time=None,
            distance_km=0,
            total_price=0,
            status='active',
            discount_percent=0
        )

        new_location = random.choice(SKOPJE_ROUTES)

        current_zone = get_zone_for_location(new_location[1])

        ScooterTracking.objects.create(
            scooter=scooter,
            latitude=new_location[0],
            longitude=new_location[1],
            zone=current_zone,
            timestamp=timezone.now()
        )

        scooter.status = 'rented'

        scooter.save()

        return redirect('/')

    return render(request, 'payment.html', {
        'scooter': scooter
    })

def instant_ride(request, scooter_id):

    return redirect(f'/payment/{scooter_id}/')

def register_user(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return redirect('/register/')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('/')

    return render(request, 'register.html')

def login_user(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/')

    return render(request, 'login.html')

def logout_user(request):

    logout(request)

    return redirect('/')

def send_to_maintenance(request, scooter_id):

    scooter = get_object_or_404(Scooter, id=scooter_id)

    scooter.status = 'maintenance'

    scooter.save()

    employee = Employee.objects.first()

    if employee:

        Maintenance.objects.create(
            scooter=scooter,
            employee_embg=employee,
            scheduled_date=timezone.now(),
            completed_date=None,
            service_type='General Inspection',
            status='pending'
        )

    return redirect('/')

def simulate_movement(request, scooter_id):

    scooter = get_object_or_404(Scooter, id=scooter_id)

    if scooter.status != 'rented':

        return JsonResponse({
            'error': 'Scooter is not rented'
        })

    last_tracking = scooter.scootertracking_set.last()

    if last_tracking:

        lat_change = random.uniform(-0.005, 0.005)

        lng_change = random.uniform(-0.005, 0.005)

        new_lat = float(last_tracking.latitude) + lat_change

        new_lng = float(last_tracking.longitude) + lng_change

    else:

        new_location = random.choice(SKOPJE_ROUTES)

        new_lat = new_location[0]

        new_lng = new_location[1]

    current_zone = get_zone_for_location(new_lng)

    ScooterTracking.objects.create(
        scooter=scooter,
        latitude=new_lat,
        longitude=new_lng,
        zone=current_zone,
        timestamp=timezone.now()
    )

    return JsonResponse({
        'success': True,
        'latitude': new_lat,
        'longitude': new_lng
    })
