from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from cart.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product



def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number= body['orderID'])
    #store transactions inside payment model
    payment = Payment(
        user = request.user,
        payment_id = body['tranID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],    
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    
    #move products to products table
    
    cart_items = CartItem.objects.filter(user=request.user)
    for items in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.is_ordered = True
        orderproduct.save()
        
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        
    
    #reduce quantity from stock
    
    # product = Product.objects.get(id=item.id)
    # product.stock -= item.quantity
    # product.save()
    #clear the cart table after payment
    #send email of products purchased to customer
    #
    
    
    return render(request,'orders/payments.html')

# Create your views here.
@csrf_exempt
def place_order(request, total=0, quantity=0,):
    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user,)
    cart_count = cart_items.count()
    form = OrderForm()
    if cart_count <=0:
        return redirect('store') 
         
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
        
    if request.method == "POST": 
        form = OrderForm(request.POST)
        if form.is_valid():
            #store billing info
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')     
            data.save()
                      
            #this gives an order id through the use of the pk
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user = current_user, is_ordered = False, order_number = order_number)
            context = {
                'order':order,
                'cart_items' : cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,   
            }
            return render(request,'orders/payments.html', context)  
    else:
        return redirect('checkout')

    
   
        
        
        
        
    
    
