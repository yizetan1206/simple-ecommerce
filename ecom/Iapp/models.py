from django.db import models
from django.db.models.fields.files import ImageField
from django.utils import timezone
from django.contrib.auth.models import User



class UsersAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'users_address'


class ProductsCategories(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'products_categories'

    def __str__(self):
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ProductsCategories, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'products'
    
    def __str__(self):
        return f'{self.name}'



class Products_variation(models.Model):
    parent = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
    id = models.CharField(primary_key=True, max_length=20, blank=True)
    features = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'products_variation'

    def __str__(self): 
        return f'{self.id}'
    


class ProductsImages(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='Iapp/image')

    class Meta:
        db_table = 'products_images'



# class Reviews(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
#     product = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
#     ratings = models.IntegerField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'reviews'


class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Products_variation, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart'
        unique_together = (('user', 'product','order'),)


# class OrdersPayment(models.Model):
#     order = models.ForeignKey(Orders, on_delete=models.CASCADE, blank=True, null=True)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     provider = models.CharField(max_length=255, blank=True, null=True)
#     status = models.CharField(max_length=50, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'orders_payment'


# class OrderedItems(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
#     product = models.ForeignKey(Products, on_delete=models.CASCADE, blank=True, null=True)
#     quantity = models.IntegerField(blank=True, null=True)
#     order = models.ForeignKey(Orders, on_delete=models.CASCADE, blank=True, null=True)
#     status = models.CharField(max_length=50, blank=True, default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'ordered_items'


