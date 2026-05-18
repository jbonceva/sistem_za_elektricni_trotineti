from django.db import models
from django.contrib.auth.models import User

#
# class User(models.Model):
#
#     username = models.CharField(
#         max_length=100,
#         primary_key=True
#     )
#
#     first_name = models.CharField(max_length=100)
#
#     last_name = models.CharField(max_length=100)
#
#     birth_day = models.DateField()
#
#     email = models.EmailField()
#
#     user_type = models.CharField(max_length=50)
#
#     def __str__(self):
#         return self.username


class Station(models.Model):

    name = models.CharField(max_length=100)

    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Zone(models.Model):

    name = models.CharField(max_length=100)

    price_per_min = models.FloatField()

    description = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.name


class Scooter(models.Model):

    model = models.CharField(max_length=100)

    battery_level = models.IntegerField()

    year = models.IntegerField()

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE
    )

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    def __str__(self):
        return self.model


class ScooterTracking(models.Model):

    latitude = models.FloatField()

    longitude = models.FloatField()

    timestamp = models.DateTimeField()

    scooter = models.ForeignKey(
        Scooter,
        on_delete=models.CASCADE
    )

    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"


class Reservation(models.Model):

    username = models.ForeignKey(User, on_delete=models.CASCADE)

    scooter = models.ForeignKey(
        Scooter,
        on_delete=models.CASCADE
    )

    reserved_from = models.DateTimeField()

    reserved_until = models.DateTimeField()

    status = models.CharField(max_length=50)

    def __str__(self):
        return str(self.id)


class Rental(models.Model):

    username = models.ForeignKey(User, on_delete=models.CASCADE)

    scooter = models.ForeignKey(
        Scooter,
        on_delete=models.CASCADE
    )

    location = models.ForeignKey(
        ScooterTracking,
        on_delete=models.SET_NULL,
        null=True
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    distance_km = models.FloatField()

    total_price = models.FloatField()

    status = models.CharField(max_length=50)

    discount_percent = models.IntegerField()

    def __str__(self):
        return str(self.id)


class Payment(models.Model):

    rental = models.ForeignKey(
        Rental,
        on_delete=models.CASCADE
    )

    username = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.FloatField()

    payment_method = models.CharField(
        max_length=50
    )

    status = models.CharField(max_length=50)

    def __str__(self):
        return str(self.id)


class Penalty(models.Model):

    username = models.ForeignKey(User, on_delete=models.CASCADE)

    rental = models.ForeignKey(
        Rental,
        on_delete=models.CASCADE
    )

    reason = models.CharField(
        max_length=255
    )

    amount = models.FloatField()

    status = models.CharField(max_length=50)

    def __str__(self):
        return self.reason


class Employee(models.Model):

    embg = models.CharField(
        max_length=20,
        primary_key=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(max_length=20)

    salary = models.FloatField()

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.first_name


class Maintenance(models.Model):

    scooter = models.ForeignKey(
        Scooter,
        on_delete=models.CASCADE
    )

    employee_embg = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    scheduled_date = models.DateTimeField()

    completed_date = models.DateTimeField(
        null=True,
        blank=True
    )

    service_type = models.CharField(
        max_length=100
    )

    status = models.CharField(max_length=50)

    def __str__(self):
        return self.service_type