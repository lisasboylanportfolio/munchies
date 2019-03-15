from django.db import models 

#migration is a change to your database 
#python3 manage.py makemigration restaurants/name_of_app after creating new modes - MAKES the change in the file
#python3 manage.py migrate actually runs it to update database 

class Restaurants(models.Model):
    #    restaurant_id = models.CharField(max_length=100)
    name         = models.CharField(max_length=100)
    address      = models.CharField(max_length=100)
    city         = models.CharField(max_length=100)
    city_id      = models.CharField(max_length=100)
    zipcode      = models.IntegerField()
    cuisine      = models.CharField(max_length=100)
    user_rating  = models.FloatField(null=True, blank=True, default=None)
    num_votes    = models.IntegerField()
    average_cost = models.IntegerField()
    longitude    =  models.DecimalField(max_digits=5, decimal_places=3)
    latitude     =  models.DecimalField(max_digits=5, decimal_places=3)


