from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid

# class Bill(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='bills/')
#     created_at = models.DateTimeField(auto_now_add=True)
#     unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


#     def __str__(self):
#         return f"Bill by {self.user.username if self.user else 'Anonymous'} at {self.created_at}"
    
#     def get_absolute_url(self):
#         from django.urls import reverse
#         return reverse('bill_detail', args=[str(self.unique_id)])


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    users = models.ManyToManyField(User, related_name='bills')
    image = models.ImageField(upload_to='bills/')
    created_at = models.DateTimeField(auto_now_add=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Remove unique=True for now

    def __str__(self):
        return f"Bill by {self.user.username if self.user else 'Anonymous'} at {self.created_at}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('bill_detail', args=[str(self.unique_id)])
    
    def total_price(self):
        return sum(item.price for item in self.items.all())



class Item(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buyers = models.ManyToManyField(User, related_name='purchased_items')

    def split_cost(self):
        if self.buyers.count() > 0:
            return self.price / self.buyers.count()
        else:
            return self.price  # Or handle the division by zero as appropriate



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
