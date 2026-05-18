from django.contrib import admin
from .models import *

admin.site.register(Station)
admin.site.register(Zone)
admin.site.register(Scooter)
admin.site.register(ScooterTracking)
admin.site.register(Reservation)
admin.site.register(Rental)
admin.site.register(Payment)
admin.site.register(Penalty)
admin.site.register(Employee)
admin.site.register(Maintenance)