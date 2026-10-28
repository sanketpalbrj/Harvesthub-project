
from os import unlink
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db import connections

cursor=connections['default'].cursor()

def home(request):
    
    sql="SELECT p.*,c.cname FROM products p INNER JOIN categories c ON p.catid=c.cid"
    cursor.execute(sql)
    products=cursor.fetchall()
    return render(request,"a.html",{"myproducts":products})

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
        return render(request,"dashboard.html")
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