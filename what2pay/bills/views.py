from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

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


from django.shortcuts import render, redirect
from .forms import BillUploadForm
from .models import Bill
import pytesseract
from PIL import Image
import re

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

def home(request):
    # print('hi')
    bill_image = None
    items = []

    if request.method == 'POST':
        # print('yo')
        form = BillUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print("very valid")
            bill = form.save(commit=False)
            bill.user = request.user  # Assuming the user is logged in
            bill.save()

            bill_image = bill.image

            # Perform OCR on the uploaded image
            image = Image.open(bill.image.path)
            ocr_text = pytesseract.image_to_string(image)

            # print(ocr_text)

            # Parse the OCR text to extract items and prices
            items = parse_ocr_text(ocr_text)
        else:
            # print("not so valid")
            print(form.errors)
    else:
        
        form = BillUploadForm()

    return render(request, 'bills/home.html', {
        'form': form,
        'bill_image': bill_image,
        'items': items
    })



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

