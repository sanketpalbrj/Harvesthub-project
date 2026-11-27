
from os import unlink
import os
from django.conf.locale import fr
import requests
from django.shortcuts import render,redirect
from django.http import HttpResponse, request
from django.db import connections
from django.contrib import messages
import django.http
from django.http import JsonResponse
from urllib.parse import urlparse
from joblib import load
model=load("fertilizer.joblib")


cursor = connections['default'].cursor()

def home(request):       
    sql="SELECT p.*,c.cname FROM products p INNER JOIN categories c ON p.catid=c.cid"
    cursor.execute(sql)
    products=cursor.fetchall()
    weather = None
    custid=request.session.get('custid')
    if custid:
            cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [custid])
            row=cursor.fetchone()
            if row and (row[0] or row[1]):
              weather = get_weather_data(row[0], row[1])
    print("WEATHER DATA PASSED TO TEMPLATE:", weather)
    return render(request,"a.html",{"myproducts":products,"weather": weather})

def about(request):
   
    n=request.POST['sname']
    g=request.POST['gender']
    s=request.POST['stream']
    myfile=request.FILES["simg"]
    with open("static/std_image/"+myfile.name,"wb+") as destination:
        for chunk in myfile.chunks():
            destination.write(chunk)
    return HttpResponse(n+" "+g+" "+s)


def dashboard(request):
    if "adminname" in request.session:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM morder WHERE order_status='Delivered'")
            total_revenue=cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM morder WHERE order_status NOT IN ('Delivered','Cancelled')")
            total_upcoming_revenue=cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM morder")
            total_orders=cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM morder WHERE order_status='Pending'")
            total_pending_orders=cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM products")
            total_products=cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM categories")
            total_categories=cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM morder WHERE order_status='Shipped'")
            total_shipped_orders=cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM morder WHERE order_status='Delivered'")
            total_completed_orders=cursor.fetchone()[0]

        context={
            'total_revenue': total_revenue,
            'total_upcoming_revenue': total_upcoming_revenue,
            'total_orders': total_orders,
            'total_pending_orders': total_pending_orders,
            'total_products': total_products,
            'total_categories': total_categories,
            'total_shipped_orders':total_shipped_orders,
            'total_completed_orders':total_completed_orders

        }

        return render(request,"dashboard.html",context)
    else:
        return redirect("/adminlogin/")

def addcategory(request):
    if "adminname" in request.session:
        return render(request,"addcategory.html")
    else:
        return redirect("/adminlogin/") 

def inscategory(request):
    
    catn=request.POST['catname']
    ins="INSERT INTO categories SET cname='"+catn+"'"
    cursor.execute(ins)
    return redirect("/listcategories/")


def listcategories(request):
    if "adminname" in request.session:
        sql="SELECT * FROM categories"
        cursor.execute(sql)
        cats=cursor.fetchall()
        return render(request,"listcategories.html",{"mycat":cats})
    else:
        return redirect("/adminlogin/")    

def delcat(request,catid):
    delc="DELETE FROM categories WHERE cid='"+str(catid)+"'"
    cursor.execute(delc)
    return redirect("/listcategories/")

def editcat(request,catid):
    sql="SELECT * FROM categories WHERE cid='"+str(catid)+"'"
    cursor.execute(sql)
    cat=cursor.fetchone()
    return render(request,"editcategory.html",{"mycat":cat})


def updatecat(request):
    catid=request.POST['catid']
    catn=request.POST['catname']
    up="UPDATE categories SET cname='"+catn+"' WHERE cid='"+str(catid)+"'"
    cursor.execute(up)
    return redirect("/listcategories/")

def addproduct(request):
    if "adminname" in request.session:
        sql="SELECT * FROM categories"
        cursor.execute(sql)
        cats=cursor.fetchall()
        return render(request,"addproduct.html",{"mycats":cats})
    else:
        return redirect("/adminlogin/")

def insproduct(request):
    productname=request.POST['productname']
    productprice=request.POST['productprice']
    catid=request.POST['category']
    productimage=request.FILES["productimage"]
    productdetails=request.POST['productdetails']
    with open("static/product_img/"+productimage.name,"wb+") as destination:
        for chunk in productimage.chunks():
            destination.write(chunk)
    ins="INSERT INTO products SET productname='"+productname+"',productprice='"+str(productprice)+"',catid='"+str(catid)+"',productimage='"+productimage.name+"',productdetails='"+productdetails+"'"
    cursor.execute(ins)
    return redirect("/listproducts/")

def listproducts(request):
    if "adminname" in request.session:
        sql="SELECT p.*,c.cname FROM products p INNER JOIN categories c ON p.catid=c.cid"
        cursor.execute(sql)
        products=cursor.fetchall()
        return render(request,"listproducts.html",{"myproducts":products})
    else:
        return redirect("/adminlogin/")

def delete_product(request,productid):
    selectp="SELECT * FROM products WHERE productid='"+str(productid)+"'"
    cursor.execute(selectp)
    product=cursor.fetchone()
    unlink("static/product_img/"+product[4])
    delp="DELETE FROM products WHERE productid='"+str(productid)+"'"
    cursor.execute(delp)
    return redirect("/listproducts/")

def adminlogin(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        sql="SELECT * FROM admin WHERE admin_email='"+email+"' AND admin_pass='"+password+"'"
        cursor.execute(sql)
        admin=cursor.fetchone()
        if admin:
            request.session["adminname"]=admin[1]
            return redirect("/dashboard/")
        else:
            return render(request,"adminlogin.html",{"msg":"Invalid Email or Password"})

    else:   
        return render(request,"adminlogin.html")


def logout(request):
    request.session.flush()
 
    return redirect("/adminlogin/")    



def edit_product(request,productid):
    sql="SELECT * FROM products WHERE productid='"+str(productid)+"'"
    cursor.execute(sql)
    product=cursor.fetchone()
    sql2="SELECT * FROM categories"
    cursor.execute(sql2)
    cats=cursor.fetchall()
    return render(request,"editproduct.html",{"myproduct":product,"mycats":cats})

def updproduct(request):
    productid=request.POST['productid']
    productname=request.POST['productname']
    productprice=request.POST['productprice']
    catid=request.POST['category']
    productdetails=request.POST['productdetails']

    if "productimage" in request.FILES:
        productimage=request.FILES["productimage"]
        with open("static/product_img/"+productimage.name,"wb+") as destination:
            for chunk in productimage.chunks():
                destination.write(chunk)
        ins="UPDATE products SET productname='"+productname+"',productprice='"+str(productprice)+"',catid='"+str(catid)+"',productimage='"+productimage.name+"',productdetails='"+productdetails+"' WHERE productid='"+str(productid)+"'"
        cursor.execute(ins)
    else:
        ins="UPDATE products SET productname='"+productname+"',productprice='"+str(productprice)+"',catid='"+str(catid)+"',productdetails='"+productdetails+"' WHERE productid='"+str(productid)+"'"
        cursor.execute(ins)    
    return redirect("/listproducts/")

def regcust(request):
    if request.method == "POST":
        custfirstname = request.POST.get('custfirstname', '').strip()
        custlastname = request.POST.get('custlastname', '').strip()
        custemail = request.POST.get('custemail', '').strip()
        custpassword = request.POST.get('custpassword', '')
        custphone = request.POST.get('custphone', '').strip()
        custpincode = request.POST.get('custpincode', '').strip()
        custcity = request.POST.get('custcity', '').strip()
        custstate = request.POST.get('custstate', '').strip()
        address = request.POST.get('address', '').strip()

        # 1. Duplicate email check
        cursor.execute("SELECT custid FROM customer WHERE custemail = %s", [custemail])
        if cursor.fetchone():
            return JsonResponse({"success": False, "field": "email", "error": "Email address is already registered"})

        # 2. Duplicate phone check
        cursor.execute("SELECT custid FROM customer WHERE custphone = %s", [custphone])
        if cursor.fetchone():
            return JsonResponse({"success": False, "field": "phone", "error": "Mobile number is already registered"})

        # 3. Insert new customer with structured address
        cursor.execute(
            """INSERT INTO customer 
               (custfirstname, custlastname, custemail, custphone, custpassword, address, pincode, city, state)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [custfirstname, custlastname, custemail, custphone, custpassword, address, custpincode, custcity, custstate]
        )

        # 4. Auto-login and store pincode/city in session for weather detection
        cursor.execute("SELECT custid, custfirstname, pincode, city FROM customer WHERE custemail = %s", [custemail])
        customer = cursor.fetchone()

        if customer:
            request.session["custid"] = customer[0]
            request.session["custname"] = customer[1].split()[0]
            request.session["custpincode"] = customer[2]
            request.session["custcity"] = customer[3]

        return JsonResponse({"success": True})

    return render(request, "/?show_register=1") 

def custlogin(request):
    if request.method == "POST":
        custemail = request.POST.get("custemail", "")
        custpassword = request.POST.get("custpassword", "")

        # Parameterized query prevents SQL errors/injection
        cursor.execute(
            "SELECT * FROM customer WHERE custemail = %s AND custpassword = %s",
            [custemail, custpassword]
        )
        customer = cursor.fetchone()

        if customer:
            full_name = customer[1]
            first_name = full_name.split()[0]

            request.session["custname"] = first_name
            request.session["custid"] = customer[0]
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})

    # If someone visits /custlogin/ directly in the browser, send them home with the login modal open
    return redirect("/?show_login=1")

def clogout(request):
    request.session.flush()
    messages.info(request, "Logged out successfully.")
    return redirect("/") 

def prediction(request):
    if "custid" in request.session:

        weather = {}
        cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [request.session["custid"]])
        row = cursor.fetchone()
        if row and (row[0] or row[1]):
            weather = get_weather_data(row[0], row[1])
        print("WEATHER DATA PASSED TO TEMPLATE:", weather)
        return render(request, "pred.html", {"weather": weather})
    else:
        return redirect("/custlogin/")


def analyze(request):
    if "custid" in request.session:
            weather = {}
            cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [request.session["custid"]])
            row = cursor.fetchone()
            if row and (row[0] or row[1]):
                weather = get_weather_data(row[0], row[1])
            print("WEATHER DATA PASSED TO TEMPLATE:", weather)
            return render(request, "result.html",{"weather": weather})
    if request.method == "POST":

        Crop_Type = int(request.POST.get('Crop_Type'))
        Soil_Type = int(request.POST.get('Soil_Type'))

        Nitrogen = int(float(request.POST.get('Nitrogen')))
        Phosphorous = int(float(request.POST.get('Phosphorous')))
        Potassium = int(float(request.POST.get('Potassium')))

        Temparature = int(float(request.POST.get('Temparature')))
        Humidity = int(float(request.POST.get('Humidity')))
        Moisture = int(float(request.POST.get('Moisture')))

        # Convert all values into a list
        input_data = [Temparature, Humidity, Moisture, Soil_Type, Crop_Type, Nitrogen, Potassium, Phosphorous]

        yp=model.predict([input_data])

        sql="SELECT p.*,c.cname FROM products p INNER JOIN categories c ON p.catid=c.cid WHERE p.productname='"+str(yp[0])+"'"
        cursor.execute(sql)
        products=cursor.fetchall()

    
        return render(request,"result.html",{ "myproducts": products},)
    return redirect("/prediction/")


def cart(request):
    if "custid" in request.session:
        custid=request.session["custid"]
        sql="SELECT c.*,p.productname,p.productimage FROM cart c INNER JOIN products p ON c.productid=p.productid WHERE c.custid='"+str(custid)+"'"
        cursor.execute(sql)
        cart_items=cursor.fetchall()
        total_price = sum(float(item[3]) * int(item[4]) for item in cart_items)

        weather = {}
        if custid:
            cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [custid])
            row = cursor.fetchone()
            if row and (row[0] or row[1]):
                weather = get_weather_data(row[0], row[1])
        print("WEATHER DATA PASSED TO TEMPLATE:", weather)
        return render(request, "cart.html", {
            "mycart": cart_items,
            "total_price": total_price,
            "weather": weather,
        })
    else:
        return redirect("/?show_login=1")  # Redirect to login modal if not logged in

def addtocart(request):
    if "custid" in request.session:
        custid=request.session["custid"]
        productid=request.POST['productid']
        price=request.POST['price']
        qty=request.POST['qty']

        cursor.execute(
            "SELECT cart_id, qty FROM cart WHERE custid = %s AND productid = %s",
            [custid, productid]
        )
        existing_item = cursor.fetchone()
        if existing_item:
            # 2. Already in cart -> add to existing quantity
            cart_id = existing_item[0]
            new_qty = int(existing_item[1]) + int(qty)
            cursor.execute(
                "UPDATE cart SET qty = %s WHERE cart_id = %s",
                [new_qty, cart_id]
            )
        else:
            # 3. Not in cart -> insert new row
            cursor.execute(
                "INSERT INTO cart (custid, productid, price, qty) VALUES (%s, %s, %s, %s)",
                [custid, productid, price, qty]
            )
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("/?show_login=1")
    

def updatecart(request):
    if "custid" in request.session:
        cartid=request.POST['cartid']
        quantity=request.POST['quantity']
        update="UPDATE cart SET qty='"+str(quantity)+"' WHERE cart_id='"+str(cartid)+"'"
        cursor.execute(update)
        return redirect("/cart/")
    else:
        return redirect("/custlogin/")

def removecart(request, cartid):
    if "custid" in request.session:
        delete="DELETE FROM cart WHERE cart_id='"+str(cartid)+"'"
        cursor.execute(delete)
        return redirect("/cart/")
    else:
        return redirect("/custlogin/")  

def checkout(request):
    if 'custid' not in request.session:
        return redirect('/?show_login=1')  # Redirect and open login modal if logged out

    custid = request.session['custid']
    cursor = connections['default'].cursor()

    # 1. Fetch Cart Items
    # Tuple indices: 0:cart_id, 1:custid, 2:productid, 3:price, 4:qty, 5:pname, 6:pimg
    cursor.execute("""
        SELECT c.cart_id, c.custid, c.productid, p.productprice, c.qty, p.productname, p.productimage 
        FROM cart c 
        JOIN products p ON c.productid = p.productid 
        WHERE c.custid = %s
    """, [custid])
    mycart = cursor.fetchall()

    if not mycart:
        return redirect('/cart/')  # Prevent checkout on empty cart

    # Calculate Grand Total
    grand_total = sum(float(item[3]) * int(item[4]) for item in mycart)

    # 2. Fetch Customer Details including pincode (5), city (6), and state (7)
    cursor.execute("""
        SELECT custfirstname, custlastname, custemail, custphone, address, pincode, city, state 
        FROM customer 
        WHERE custid = %s
    """, [custid])
    customer = cursor.fetchone()

    weather = {}
    if custid:
        cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [custid])
        row = cursor.fetchone()
        if row and (row[0] or row[1]):
            weather = get_weather_data(row[0], row[1])
    print("WEATHER DATA PASSED TO TEMPLATE:", weather)

    context = {
        'mycart': mycart,
        'grand_total': grand_total,
        'customer': customer,
        "weather": weather,
    }

    return render(request, 'checkout.html', context)
    

    


def placeorder(request):
    if request.method == 'POST' and 'custid' in request.session:
        custid = request.session['custid']
        total_amount = request.POST.get('total_amount')

        # Capture recipient & structured address from checkout form
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        recipient_name = f"{fname} {lname}".strip()
        recipient_phone = request.POST.get('phone', '').strip()

        street = request.POST.get('shipping_address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        full_address = f"{street}, {city}, {state} - {pincode}"

        payment_method = request.POST.get('payment_method', 'COD')

        cursor = connections['default'].cursor()

        # 1. Fetch current cart items
        cursor.execute("""
            SELECT c.productid, p.productprice, c.qty 
            FROM cart c 
            JOIN products p ON c.productid = p.productid 
            WHERE c.custid = %s
        """, [custid])
        cart_items = cursor.fetchall()

        if not cart_items:
            return redirect('/cart/')

        # 2. Insert into `morder` table with recipient & full shipping address
        cursor.execute("""
            INSERT INTO morder 
            (custid, order_status, total_amount, recipient_name, recipient_phone, shipping_address, payment_method) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [custid, 'Pending', total_amount, recipient_name, recipient_phone, full_address, payment_method])

        # Get the newly generated order_id
        order_id = cursor.lastrowid

        # 3. Insert each item into `suborder` table
        for item in cart_items:
            productid = item[0]
            price = item[1]
            qty = item[2]
            cursor.execute(
                "INSERT INTO suborder (order_id, productid, price, qty) VALUES (%s, %s, %s, %s)",
                [order_id, productid, price, qty]
            )

        # 4. Clear the user's cart after order placement
        cursor.execute("DELETE FROM cart WHERE custid = %s", [custid])

        return redirect(f'/ordersuccess/{order_id}/')

    return redirect('/checkout/')


def ordersuccess(request, order_id):
    return render(request, 'order_success.html', {'order_id': order_id})

def pendingorders(request):
    cursor = connections['default'].cursor()
    cursor.execute("""
        SELECT m.order_id,
               COALESCE(NULLIF(m.recipient_name, ''), c.custfirstname) AS disp_fname,
               CASE WHEN m.recipient_name IS NOT NULL AND m.recipient_name != '' THEN '' ELSE c.custlastname END AS disp_lname,
               COALESCE(NULLIF(m.recipient_phone, ''), c.custphone) AS disp_phone,
               COALESCE(NULLIF(m.shipping_address, ''), CONCAT_WS(', ', c.address, c.city, c.state, c.pincode)) AS disp_address,
               m.order_date,
               m.total_amount,
               m.order_status
        FROM morder m
        JOIN customer c ON m.custid = c.custid
        WHERE m.order_status = 'Pending'
        ORDER BY m.order_date DESC
    """)
    orders = cursor.fetchall()
    return render(request, 'pending_orders.html', {'orders': orders, 'page_title': 'Pending Orders'})


def allorders(request):
    cursor = connections['default'].cursor()
    cursor.execute("""
        SELECT m.order_id,
               COALESCE(NULLIF(m.recipient_name, ''), c.custfirstname) AS disp_fname,
               CASE WHEN m.recipient_name IS NOT NULL AND m.recipient_name != '' THEN '' ELSE c.custlastname END AS disp_lname,
               COALESCE(NULLIF(m.recipient_phone, ''), c.custphone) AS disp_phone,
               COALESCE(NULLIF(m.shipping_address, ''), CONCAT_WS(', ', c.address, c.city, c.state, c.pincode)) AS disp_address,
               m.order_date,
               m.total_amount,
               m.order_status
        FROM morder m
        JOIN customer c ON m.custid = c.custid
        ORDER BY m.order_date DESC
    """)
    orders = cursor.fetchall()
    return render(request, 'pending_orders.html', {'orders': orders, 'page_title': 'All Orders'})


def orderdetails(request, order_id):
    cursor = connections['default'].cursor()
    # 1. Master Order + Delivery Info (indices 0-8 match existing template; 9:payment_method, 10:ordered_by_name)
    cursor.execute("""
        SELECT m.order_id,
               COALESCE(NULLIF(m.recipient_name, ''), c.custfirstname) AS disp_fname,
               CASE WHEN m.recipient_name IS NOT NULL AND m.recipient_name != '' THEN '' ELSE c.custlastname END AS disp_lname,
               c.custemail,
               COALESCE(NULLIF(m.recipient_phone, ''), c.custphone) AS disp_phone,
               COALESCE(NULLIF(m.shipping_address, ''), CONCAT_WS(', ', c.address, c.city, c.state, c.pincode)) AS disp_address,
               m.order_date,
               m.total_amount,
               m.order_status,
               COALESCE(m.payment_method, 'COD') AS payment_method,
               CONCAT(c.custfirstname, ' ', c.custlastname) AS ordered_by
        FROM morder m
        JOIN customer c ON m.custid = c.custid
        WHERE m.order_id = %s
    """, [order_id])
    order = cursor.fetchone()

    # 2. Suborder items + Product Info
    cursor.execute("""
        SELECT s.suborder_id, p.productname, p.productimage, s.price, s.qty
        FROM suborder s
        JOIN products p ON s.productid = p.productid
        WHERE s.order_id = %s
    """, [order_id])
    items = cursor.fetchall()

    return render(request, 'order_details.html', {'order': order, 'items': items})


def updateorderstatus(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('order_status')
        
        cursor = connections['default'].cursor()
        cursor.execute(
            "UPDATE morder SET order_status = %s WHERE order_id = %s",
            [new_status, order_id]
        )
    return redirect(request.META.get('HTTP_REFERER', '/pendingorders/'))

def marketplace(request):
    if "custid" not in request.session:
        return redirect("/?show_login=1")

    custid = request.session["custid"]

    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT cid, cname FROM categories ORDER BY cname ASC")
        categories = cursor.fetchall()

        # 2. Check if a category filter (?cat=<id>) was clicked in the sidebar
        selected_cat = request.GET.get('cat')

        # Tuple indices: 0:productid, 1:productname, 2:productdetails, 3:productprice, 4:productimage
        if selected_cat:
            cursor.execute("""
                SELECT productid, productname, productdetails, productprice, productimage
                FROM products
                WHERE catid = %s
            """, [selected_cat])
        else:
            cursor.execute("""
                SELECT productid, productname, productdetails, productprice, productimage
                FROM products
            """)
        products = cursor.fetchall()

        # 3. Fetch cart count for the top navbar badge
        cursor.execute("SELECT COUNT(*) FROM cart WHERE custid = %s", [custid])
        cart_count = cursor.fetchone()[0]

        weather = {}
        cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [custid])
        row = cursor.fetchone()
        if row and (row[0] or row[1]):
            weather = get_weather_data(row[0], row[1])
        print("WEATHER DATA PASSED TO TEMPLATE:", weather)

    context = {
        'categories': categories,
        'products': products,
        'selected_cat': selected_cat,
        'cart_count': cart_count,
        "weather": weather,
    }
    return render(request, 'marketplace.html', context)


def get_weather_data(city, state):
    if not city and not state:
        return None

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("WeatherAPI error: WEATHER_API_KEY is missing.")
        return None

    location_parts = [part.strip() for part in (city, state, "India") if part and part.strip()]
    location_query = ", ".join(location_parts)

    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": location_query,
        "aqi": "no",
        "alerts": "no",
        "days": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if response.status_code == 200:
            forecast_days = []
            for day_item in data.get("forecast", {}).get("forecastday", []):
                forecast_days.append({
                    "date": day_item["date"],
                    "max_temp": day_item["day"]["maxtemp_c"],
                    "min_temp": day_item["day"]["mintemp_c"],
                    "humidity": day_item["day"]["avghumidity"],
                    "rain_chance": day_item["day"]["daily_chance_of_rain"],
                    "condition": day_item["day"]["condition"]["text"],
                    "icon": day_item["day"]["condition"]["icon"],
                    "precip_mm": day_item["day"]["totalprecip_mm"],
                })

            return {
                "city": data["location"]["name"],
                "region": data["location"]["region"],
                "temp_c": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "wind_kph": data["current"]["wind_kph"],
                "condition": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"],
                "forecast": forecast_days,
                "rain_chance": forecast_days[0]["rain_chance"] if forecast_days else None,
                "feels_like": data["current"]["feelslike_c"],
                "precip_mm": forecast_days[0]["precip_mm"] if forecast_days else None,
            }
        else:
            print("WeatherAPI HTTP error:", response.status_code, data)
    except Exception as e:
        print("WeatherAPI error:", e)

    return None

def weather(request):
    custid = request.session.get('custid')
    weather = None
    if custid:
        return redirect('/?show_login=1')  # Redirect to login modal if not logged in
    return redirect('/?show_weather=1')  # Redirect to home with weather modal open

def myorders(request):
    custid = request.session.get("custid")
    if not custid:
        return redirect("/?show_login=1")

    cursor = connections['default'].cursor()
    cursor.execute("""
        SELECT m.order_id,
                   m.order_date,
                   m.order_status,
                   s.suborder_id,
                   p.productname,
                   p.productimage,
                   s.price,
                   s.qty,
                   (s.price * s.qty) AS subtotal,
                   c.city,
                   c.state
            FROM morder m
            JOIN customer c ON m.custid = c.custid
            JOIN suborder s ON m.order_id = s.order_id
            JOIN products p ON s.productid = p.productid
            WHERE m.custid = %s
            ORDER BY m.order_date DESC, s.suborder_id ASC
        """, [custid])
    orders = cursor.fetchall()

    

    weather = {}
    cursor.execute("SELECT city, state FROM customer WHERE custid = %s", [custid])
    row = cursor.fetchone()
    if row and (row[0] or row[1]):
        weather = get_weather_data(row[0], row[1])
    print("WEATHER DATA PASSED TO TEMPLATE:", weather)

    return render(request, "myorders.html", {
        "orders": orders,
        "weather": weather,
    })