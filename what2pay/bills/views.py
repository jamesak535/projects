from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .forms import BillUploadForm
from .models import Bill, Item
import pytesseract
from PIL import Image
import re
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    return render(request, 'login.html')


def parse_ocr_text(ocr_text):
    # print('hi')
    items = []
    lines = []

    # print("original text: ")
    # print(ocr_text)
    # print("end of the text")

    possibleName = []
    possiblePrice = []

    # this is a switch
    notPrice = 0

    # Split the OCR text into lines
    for line in ocr_text.split('\n'):
        if line:
            possibleLetter = ' '.join(line.split(' ')[0:-1])
            # last word of the line
            possibleNumber =  line.split(' ')[-1]
            try:
                # check if the last word is the price
                # print(possibleNumber)
                float(possibleNumber)
            except:
                # if it is not price, break out of the entire loop
                notPrice = 1
                break
            else:
                # if it is the price, add the name and price
                possibleName.append(possibleLetter)
                possiblePrice.append(possibleNumber)

    # this is where the last word was not the price
    if notPrice:
        # print('here')
        for line in ocr_text.split('\n'):
            if line:
                print(line)
                lines.append(line)

    if (len(possibleName) == 0):
        possibleName = lines[0:len(lines)//2]
        possiblePrice = lines[len(lines)//2:]

    # Keywords to skip in the OCR text
    keywords_to_skip = ['SUBTOTAL', 'Price (E)', 'TOTAL']

    item_num = 1
    totalPrice = 0
    for x in range(len(possibleName)):
        if not possibleName[x] or not possiblePrice[x] or any(keyword in possibleName[x] for keyword in keywords_to_skip) or any(keyword in possiblePrice[x] for keyword in keywords_to_skip):
            continue

        name = possibleName[x]
        price = possiblePrice[x]
        # print("name: ", name, "price: ", price)
        try:
            price = float(price)
        except:
            # print('there was an error')
            # if the price cant be read, set it to 0
            price = 0
        else:
            price = float(price)

        items.append({
            'number': item_num,  # Set the item number
            'name': name,
            'price': price
        })
        item_num += 1
        totalPrice += price

    # If no items are found, return a default message
    if not items:
        items.append({'number': '-', 'name': 'No items found', 'price': 'N/A'})
    # else:
    #     # if there a item, show total at the last row
    #     items.append({'number': '', 'name': 'Total', 'price': round(totalPrice, 2)})

    return items


def bill_upload_view(request):
    if request.method == 'POST':
        form = BillUploadForm(request.POST, request.FILES)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.user = request.user
            bill.save()
            # Process OCR here after saving the bill image
            image_path = bill.image.path
            ocr_text = pytesseract.image_to_string(Image.open(image_path))
            # print(ocr_text)
            # Process OCR result and create items for the bill
            # Extract items from OCR text here
            return redirect('bill_detail', bill_id=bill.id)
    else:
        form = BillUploadForm()
    return render(request, 'bill_upload.html', {'form': form})


# def home(request):
#     context = {}
#     return render(request, "bills/home.html")
# @login_required
# def home(request):
#     # print('hi')
#     bill_image = None
#     items = []

#     if request.method == 'POST':
#         # print('yo')
#         form = BillUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             # print("very valid")
#             bill = form.save(commit=False)
#             # bill.user = request.user  # Assuming the user is logged in
#             if request.user.is_authenticated:
#                 bill.user = request.user
#             else:
#                 bill.user = None
#             bill.save()

#             bill_image = bill.image

#             # Perform OCR on the uploaded image
#             image = Image.open(bill.image.path)
#             ocr_text = pytesseract.image_to_string(image)

#             # print(ocr_text)

#             # Parse the OCR text to extract items and prices
#             items = parse_ocr_text(ocr_text)
#         else:
#             # print("not so valid")
#             return redirect('login')
#             # print(form.errors)
#     else:
        
#         form = BillUploadForm()

#     return render(request, 'bills/home.html', {
#         'form': form,
#         'bill_image': bill_image,
#         'items': items
#     })

def home(request):
    bill_image = None
    items = []
    login_error = None
    form = BillUploadForm()  # Initialize form here

    if request.method == 'POST':
        if 'login' in request.POST:
            # Handle login
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Refresh the page after login
            else:
                login_error = 'Invalid login credentials'
        else:
            # Handle bill upload
            form = BillUploadForm(request.POST, request.FILES)
            if form.is_valid():
                bill = form.save(commit=False)
                if request.user.is_authenticated:
                    bill.user = request.user
                else:
                    bill.user = None
                bill.save()

                bill_image = bill.image

                # Perform OCR on the uploaded image
                image = Image.open(bill.image.path)
                ocr_text = pytesseract.image_to_string(image)

                # Parse the OCR text to extract items and prices
                items = parse_ocr_text(ocr_text)
            else:
                print(form.errors)

    return render(request, 'bills/home.html', {
        'form': form,
        'bill_image': bill_image,
        'items': items,
        'login_error': login_error
    })



@csrf_exempt
def update_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_number = data['item_number']
        field = data['field']
        value = data['value']

        # You can now update your database with the new value (e.g., update item name or price)
        print(f"Item {item_number} - Updating {field} to {value}")

        # Return a success response
        return JsonResponse({'status': 'success', 'item_number': item_number, 'field': field, 'value': value})

    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def add_row(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_number = data['item_number']
        name = data['name']
        price = data['price']

        # Add the new row to your database
        print(f"Adding new item {item_number}: {name} - {price}")

        return JsonResponse({'status': 'success', 'item_number': item_number})

    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def delete_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_number = data['item_number']

        # Remove the item from your database
        print(f"Deleting item {item_number}")

        return JsonResponse({'status': 'success', 'item_number': item_number})

    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def save_bill(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items_data = data.get('items', [])

        # Assuming the user is logged in
        bill = Bill(user=request.user)
        bill.save()

        # Save items
        for item_data in items_data:
            Item.objects.create(
                bill=bill,
                description=item_data['name'],
                price=item_data['price']
            )

        return JsonResponse({'status': 'success', 'url': bill.get_absolute_url()})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def bill_detail(request, unique_id):
    bill = get_object_or_404(Bill, unique_id=unique_id)

    if request.user.is_authenticated and request.user not in bill.users.all():
        bill.users.add(request.user)
    #     bill.save()

    items = bill.items.all()
    users = bill.users.all()
    # print(f"Users in bill: {users}")

    return render(request, 'bills/bill_detail.html', {
        'bill': bill,
        'items': items,
        'users': users,
    })


def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password', '')

        # Try to authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is None:
            # If user doesn't exist, create one
            user = User.objects.create_user(username=username)
            if password:
                user.set_password(password)
                user.save()
                user = authenticate(request, username=username, password=password)
            else:
                # Authenticate without a password
                user.backend = 'django.contrib.auth.backends.ModelBackend'

        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            return render(request, 'sign_in.html', {'error': 'Authentication failed.'})

    return render(request, 'sign_in.html')



# @login_required
# def toggle_item(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         item_id = data.get('item_id')
#         item = get_object_or_404(Item, id=item_id)
#         user = request.user

#         if user in item.buyers.all():
#             # Unmark the item
#             item.buyers.remove(user)
#             action = 'unmarked'
#         else:
#             # Mark the item
#             item.buyers.add(user)
#             action = 'marked'

#         return JsonResponse({'status': 'success', 'action': action})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# def bill_updates(request, unique_id):
#     bill = get_object_or_404(Bill, unique_id=unique_id)
#     items = bill.items.all()
#     items_data = []

#     for item in items:
#         buyers = [buyer.username for buyer in item.buyers.all()]
#         items_data.append({
#             'id': item.id,
#             'buyers': buyers
#         })

#     return JsonResponse({'items': items_data})


@require_POST
def toggle_item(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')
    username = data.get('username')

    item = get_object_or_404(Item, id=item_id)
    user = get_object_or_404(User, username=username)
    
    if user in item.buyers.all():
        item.buyers.remove(user)
    else:
        item.buyers.add(user)
    
    return JsonResponse({'status': 'success'})

    # try:
    #     item = Item.objects.get(id=item_id)
    #     user = User.objects.get(username=username)
        
    #     if user in item.buyers.all():
    #         item.buyers.remove(user)
    #     else:
    #         item.buyers.add(user)
        
    #     return JsonResponse({'status': 'success'})
    # except (BillItem.DoesNotExist, User.DoesNotExist):
    #     return JsonResponse({'status': 'error', 'message': 'Item or user not found'})

def bill_updates(request, unique_id):
    bill = get_object_or_404(Bill, unique_id=unique_id)
    items = bill.items.all()
    users = bill.users.all()
    items_data = []

    for item in items:
        buyers = [buyer.username for buyer in item.buyers.all()]
        items_data.append({
            'id': item.id,
            'buyers': buyers,
            'price': str(item.price)  # Convert to string to ensure JSON serialization
        })

    return JsonResponse({
        'items': items_data,
        'total': str(bill.total_price()),
        'users': [user.username for user in users]
    })


def logout_view(request):
    logout(request)
    return redirect(request.GET.get('next', '/'))



# def bill_detail(request, unique_id):
#     bill = get_object_or_404(Bill, unique_id=unique_id)
#     items = bill.items.all()
#     users = User.objects.filter(purchased_items__in=items).distinct()
#     return render(request, 'bills/bill_detail.html', {
#         'bill': bill,
#         'items': items,
#         'users': users,
#     })


@require_POST
def toggle_item(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')
    username = data.get('username')
    item = get_object_or_404(Item, id=item_id)
    user = get_object_or_404(User, username=username)
    
    if user in item.buyers.all():
        item.buyers.remove(user)
    else:
        item.buyers.add(user)
    
    return JsonResponse({'status': 'success'})