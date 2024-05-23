from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django import forms
from django.contrib.auth.hashers import make_password, check_password

from store.models import Account, Book, Order, OrderItem

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Enter your password'}))


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)
    # phone = forms.CharField(max_length=11)

    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())




# Create your views here.
def index(request):
    accountID = request.session.get("account")

    books = Book.get_all_products()

    #return HttpResponse("Hello world")
    return render(request, "store/index.html", {
        "all_books" : books,
        "accountID" : accountID
    })


def login(request):
    # If we are already logged in
    accountID = request.session.get("account")
    if accountID:
        return HttpResponseRedirect(reverse("store:index"))

    if request.method == "GET":
        return render(request, "store/login.html", {
            "form" : LoginForm()
        })
    

    form = LoginForm(request.POST)

    # Validation
    if not form.is_valid():
        return render(request, "store/login.html", {
            "form" : form
        })
    
    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]
    account = Account.get_account_by_email(email)

    
    # Check if there is an account with the email in the database
    # or the password matches
    if not account or not check_password(password, account.password):
        return render(request, "store/login.html", {
            "form" : form,
            "error" : "Invalid account credentials."
        })

    # Login succesfull
    # Create a session
    request.session['account'] = account.id
    return HttpResponseRedirect(reverse("store:index"))



def signup(request):
    # If we are already logged in
    accountID = request.session.get("account")
    if accountID:
        return HttpResponseRedirect(reverse("store:index"))

    if request.method == "GET":
        accountID = request.session.get("account")
        return render(request, "store/signup.html", {
            "form": SignupForm(),
            "accountID": accountID
        })
    
    # POST

    # validation
    form = SignupForm(request.POST)
    if not form.is_valid():
        return render(request, "store/signup.html", {
            "form": form,     
        })


    # get the cleaned (proper termination of chars, no sql injection, etc) sent data
    first_name = form.cleaned_data["first_name"]
    last_name = form.cleaned_data["last_name"]
    # phone = form.cleaned_data["phone"]
    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]

    account = Account(first_name=first_name,
                        last_name=last_name,
                        phone=None,
                        email=email,
                        password=make_password(password))
    
    if account.isExists():
        form.add_error("email", "This account already exists.")

        return render(request, "store/signup.html", {
            "form": form,
        })
    
    account.register()
    request.session['account'] = account.id
    return HttpResponseRedirect(reverse("store:index"))

    

def search(request):
    request.POST.cleaned_data['']

    return HttpResponse("TODO: Implement search feature")


# When the user visited the /cart route
def cart(request):
    accountID = request.session.get("account")
    # If the user is not logged in
    if not accountID:
        return HttpResponseRedirect(reverse("store:login"))

    cart = request.session.get('cart')
    if not cart:
        cart = {}
    if request.method == "GET":

        
        # Calculate total price in cart
        cart_total_price = 0
        for cart_item in cart:
            cart_total_price = cart_total_price + cart[cart_item]['total_price_int']

        is_cart_empty = not cart
        return render(request, "store/cart.html", {
            "cart" : cart,
            "cart_total_price" : format(cart_total_price, ","),
            "accountID" : accountID,
            "cart_empty" : is_cart_empty
        })




    remove = request.POST.get('removeID')
    if remove:
        if cart and remove in cart:
            cart.pop(remove)
        
        request.session['cart'] = cart 
        return HttpResponseRedirect(reverse('store:cart'))

    orderID = request.POST.get('orderId')
    quantity = int(request.POST.get('quantity-input'))
    book = Book.get_book_by_id(orderID)
    
    prev_quantity = 0
    if orderID in cart:
        prev_quantity = cart[orderID]['quantity']

    total_quantity = quantity + prev_quantity
    total_price = book.price * total_quantity

    # Add an elipsis(...) to the title if it is too long
    title = (book.title[:60] + '...') if len(book.title) > 64 else book.title
    cart_item = {
        "product_title" : title,
        "author" : book.author,
        "image" : book.image.url,
        "price" : format(book.price, ","),
        "quantity" : total_quantity,
        "total_price" : format(total_price, ","),
        "total_price_int" : total_price,
    }

    cart[orderID] = cart_item
    request.session['cart'] = cart 


    return HttpResponseRedirect(reverse('store:cart'))
    
    

def book (request, bookID):
    accountID = request.session.get("account")

    book = Book.get_book_by_id(bookID)
    return render(request, "store/book.html", {
        "book" : book,
        "formated_price" : format(book.price, ","),
        "accountID" : accountID,
    })


def account(request):
    if request.method == "POST":
        return HttpResponseRedirect(reverse("store:index"))
    
    # Get
    return HttpResponse("TODO: Implement Acount")



def checkout(request):
    # If we are not logged in
    accountID = request.session.get("account")
    if not accountID:
        return HttpResponseRedirect(reverse("store:login"))

    # Get the cart
    cart = request.session['cart']
    if not cart:
        # Cart is empty
        return HttpResponseRedirect(reverse("store:index"))

    if request.method == "GET":
        # We only allow post method
        return HttpResponseRedirect(reverse("store:index"))



    # Purchase all of the items in the cart
    address = "Dimasarsarakan St. Batac City, Ilocos Norte, Philippines"
    account = Account.get_account_by_id(accountID)
    order = Order(
            customer=account,
            address=address,
            phone=account.phone,
            price=0 # Inititalize the total price to zero
            )

    order.save()
    total_price = 0

    for cart_item in cart:
        # Read the book in our cart from the database
        book = Book.get_book_by_id(cart_item)
        quantity = cart[cart_item]['quantity']

        # If quantity is in invalid state
        if quantity <= 0:
            return HttpResponseRedirect(reverse('store:index'))

        order_item_price = quantity * book.price
        order_item = OrderItem(product=book,
                               quantity=quantity,
                               price=order_item_price)


        total_price += book.price * quantity
        order_item.save()

        # Add to order
        order.items.add(order_item.id)
    
    order.price = total_price
    order.save()

     # Clear cart
    request.session['cart'] = {} 
    return HttpResponseRedirect(reverse('store:purchases'))

        


def purchases(request):
    # If we are not logged in
    accountID = request.session.get("account")
    if not accountID:
        return HttpResponseRedirect(reverse("store:login"))

    account = Account.get_account_by_id(accountID)
    
    all_orders = account.order.all().order_by('datetime')
    
    print(all_orders)

    return render(request, 'store/purchases.html', {
        'accountID' : accountID,
        'orders' : all_orders,
    })


def logout(request): 
    request.session.clear() 
    return HttpResponseRedirect(reverse("store:index")) 