from django.contrib import admin
from django.urls import path

from scooters.views import (
    home,
    scooter_detail,
    reserve_scooter,
    reservations,
    cancel_reservation,
    delete_reservation,
    start_ride,
    rides,
    end_ride,
    my_rides,
    instant_ride,
    register_user,
    login_user,
    logout_user,
    payment,
    send_to_maintenance,
    simulate_movement,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', home, name='home'),

    path(
        'scooter/<int:scooter_id>/',
        scooter_detail,
        name='scooter_detail'
    ),

    path(
        'reserve/<int:scooter_id>/',
        reserve_scooter,
        name='reserve_scooter'
    ),

    path(
        'reservations/',
        reservations,
        name='reservations'
    ),

    path(
        'cancel-reservation/<int:reservation_id>/',
        cancel_reservation,
        name='cancel_reservation'
    ),

    path(
        'delete-reservation/<int:reservation_id>/',
        delete_reservation,
        name='delete_reservation'
    ),

    path(
        'start-ride/<int:reservation_id>/',
        start_ride,
        name='start_ride'
    ),

    path(
        'rides/',
        rides,
        name='rides'
    ),

    path(
        'end-ride/<int:ride_id>/',
        end_ride,
        name='end_ride'
    ),

    path(
        'my-rides/',
        my_rides,
        name='my_rides'
    ),

    path(
        'instant-ride/<int:scooter_id>/',
        instant_ride,
        name='instant_ride'
    ),

    path(
        'payment/<int:scooter_id>/',
        payment,
        name='payment'
    ),

    path(
        'register/',
        register_user,
        name='register'
    ),

    path(
        'login/',
        login_user,
        name='login'
    ),

    path(
        'logout/',
        logout_user,
        name='logout'
    ),

    path(
        'send-to-maintenance/<int:scooter_id>/',
        send_to_maintenance,
        name='send_to_maintenance'
    ),

    path(
        'simulate-movement/<int:scooter_id>/',
        simulate_movement,
        name='simulate_movement'
    ),
]
