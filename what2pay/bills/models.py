from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bills/')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Bill by {self.user.username if self.user else 'Anonymous'} at {self.created_at}"

class Item(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buyers = models.ManyToManyField(User, related_name='purchased_items')

    def split_cost(self):
        return self.price / self.buyers.count()



# import uuid
# from django.db import models
# from django.contrib.auth.models import User

# # class Bill(models.Model):
# #     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # No user required
# #     image = models.ImageField(upload_to='bills/', null=True, blank=True)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique identifier

# #     def __str__(self):
# #         return f"Bill by {self.user.username if self.user else 'Anonymous'} at {self.created_at}"



# # class Item(models.Model):
# #     bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
# #     description = models.CharField(max_length=255)
# #     price = models.DecimalField(max_digits=10, decimal_places=2)
# #     buyers = models.ManyToManyField(User, related_name='purchased_items')

# #     def split_cost(self):
# #         if self.buyers.count() > 0:
# #             return self.price / self.buyers.count()
# #         return self.price  # If no buyers, full price is not split



# class Bill(models.Model):
#     # We will not require user here, setting it to optional
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     image = models.ImageField(upload_to='bills/', null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Bill at {self.created_at}"

# class Item(models.Model):
#     bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
#     description = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.description} - ${self.price}"
