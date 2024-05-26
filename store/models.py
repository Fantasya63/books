from django.db import models
from django.shortcuts import get_object_or_404
import datetime

# Create your models here.
class Account(models.Model):
    first_name = models.CharField(max_length=64) 
    last_name = models.CharField(max_length=64) 
    phone = models.CharField(max_length=16, blank=True, null=True) 
    email = models.EmailField() 
    password = models.CharField(max_length=32) 
    
    # to save the data 
    def register(self): 
        self.save() 
  
    @staticmethod
    def get_account_by_email(email): 
        try: 
            return Account.objects.get(email=email) 
        except: 
            return False
    
    def get_account_by_id(id):
        try: 
            return Account.objects.get(id=id) 
        except: 
            return False

    def isExists(self): 
        if Account.objects.filter(email=self.email): 
            return True
  
        return False


from django.db import models 
  
  
class Category(models.Model): 
    name = models.CharField(max_length=64) 
  
    @staticmethod
    def get_all_categories(): 
        return Category.objects.all() 
  
    def __str__(self): 
        return self.name 


class Book(models.Model):
    title = models.CharField(max_length=256)
    # description = models.CharField(max_length=3000, default='', blank=True, null=True)
    description = models.TextField(max_length=3000, default='', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1) 
    
    genre = models.CharField(max_length=64, default='', blank=True, null=True)
    isbn = models.IntegerField(blank=False, null=True)
    
    author = models.CharField(max_length=64, default='', blank=True, null=True )
    publisher = models.CharField(max_length=64, default='', blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)

    price = models.IntegerField(blank=False, null=True)    
    image = models.ImageField(upload_to='uploads/products/')


    @staticmethod
    def get_book_by_id(ids): 
        return get_object_or_404(Book, pk=ids)
  
    @staticmethod
    def get_all_products(): 
        return Book.objects.all() 
  
    @staticmethod
    def get_all_products_by_categoryid(category_id): 
        if category_id: 
            return Book.objects.filter(category=category_id) 
        else: 
            return Book.get_all_products()

    
class OrderItem(models.Model):
    product = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, related_name='OrderItem')
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()


class Order(models.Model): 
    items = models.ManyToManyField(OrderItem, related_name='order')
    # product = models.ForeignKey(Book, on_delete=models.CASCADE, default='')
    customer = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name='order', null=True)
    price = models.IntegerField()
    address = models.CharField(max_length=64, default='', blank=True) 
    phone = models.CharField(max_length=16, default='', blank=True) 
    datetime = models.DateTimeField(default=datetime.datetime.today)
    status = models.BooleanField(default=False) 
  
    def placeOrder(self): 
        self.save() 
  
    @staticmethod
    def get_orders_by_customer(customer_id): 
        return Order.objects.filter(customer=customer_id).order_by('-date')
