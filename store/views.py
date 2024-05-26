from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

from store.models import Account, Book, Order, OrderItem

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder' : 'Enter your password'}))


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=64, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=64, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
    # phone = forms.CharField(max_length=11)

    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))




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
    search = request.POST.get('search')

    search_result = Book.objects.filter(
        Q(title__icontains=search) | Q(isbn__iexact=search) | Q(author__icontains=search)
    )



    return render(request, "store/search.html", {
        "search_querry" : search,
        "search_result" : search_result,
    })


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


    return HttpResponseRedirect(reverse('store:index'))
    
    

def book (request, bookID):
    accountID = request.session.get("account")

    book = Book.get_book_by_id(bookID)
    return render(request, "store/book.html", {
        "book" : book,
        "formated_price" : format(book.price, ","),
        "accountID" : accountID,
    })





class EditAccountForm(forms.Form):


    first_name = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'}))
    last_name = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'}))
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'placeholder': 'Enter Phone Number'}))

    email = forms.EmailField(disabled=True, required=False)


    current_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder' : 'Enter Current password (Leave blank to keep unchanged)'}))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder' : 'Enter New Password'}))
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder' : 'Confirm New Password'}))


def view_account(request):
    accountID = request.session.get("account")

    # If the user is not logged in
    if not accountID:
        return HttpResponseRedirect('store/login.html')

    my_account = Account.get_account_by_id(accountID)

    initial_values_table = {
        "first_name" : my_account.first_name,
        'last_name' : my_account.last_name,
        'phone' : my_account.phone,
        'email' : my_account.email,
    }

    
    edit_form = EditAccountForm(initial=initial_values_table)
    

    # Get
    if request.method == "GET":
        return render(request, 'store/account.html', {
            'accountID' : accountID,
            'account' : my_account,
            'edit_form' : edit_form,
        })
    
    # POST
    form = EditAccountForm(request.POST)
    if not form.is_valid():
        return render(request, "store/account.html", {
            'accountID' : accountID,
            'account' : my_account,
            'edit_form' : form,    
        })


    # get the cleaned (proper termination of chars, no sql injection, etc) sent data
    first_name = form.cleaned_data["first_name"]
    last_name = form.cleaned_data["last_name"]
    phone = form.cleaned_data["phone"]
    email = form.cleaned_data["email"]
    
    my_account.first_name = first_name
    my_account.last_name = last_name
    my_account.phone = phone


    current_password = form.cleaned_data['current_password']
    new_password = form.cleaned_data['new_password']
    confirm_password = form.cleaned_data['confirm_password']

    if current_password or new_password or confirm_password:
        if not check_password(current_password, my_account.password):
            return render(request, 'store/account.html', {
                'accountID': accountID,
                'account' : my_account,
                'edit_form' : form,
                'error' : "Incorrect Password."
            })
        
        if new_password != confirm_password:
             return render(request, 'store/account.html', {
                'accountID': accountID,
                'account' : my_account,
                'edit_form' : form,
                'error' : "Password do not match"
            })
        
        my_account.password = make_password(new_password)
    
    my_account.save()
    return HttpResponseRedirect(reverse('store:account'))
        
        


    


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
    
    all_orders = account.order.all().order_by('-datetime')
    
    print(all_orders)

    return render(request, 'store/purchases.html', {
        'accountID' : accountID,
        'orders' : all_orders,
    })


def logout(request): 
    request.session.clear() 
    return HttpResponseRedirect(reverse("store:index")) 