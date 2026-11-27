
from django.urls import path
from myapp import views
import myapp.views
from myapp.views import custlogin, regcust, clogout

urlpatterns = [
  path("",myapp.views.home),
  path("about/",myapp.views.about),
  path("dashboard/",myapp.views.dashboard),
  path("addcategory/",myapp.views.addcategory),
  path("inscategory/",myapp.views.inscategory),
  path("listcategories/",myapp.views.listcategories),
  path("delcat/<int:catid>",myapp.views.delcat),
  path("editcat/<int:catid>",myapp.views.editcat),
  path("updatecat/",myapp.views.updatecat),
  path("addproduct/",myapp.views.addproduct),
  path("insproduct/",myapp.views.insproduct),
  path("listproducts/",myapp.views.listproducts),
  path("delete_product/<int:productid>",myapp.views.delete_product),
  path("adminlogin/",myapp.views.adminlogin),
  path("logout/",myapp.views.logout),
  path("edit_product/<int:productid>",myapp.views.edit_product),
  path("updproduct/",myapp.views.updproduct),
  path('logincust/', myapp.views.custlogin, name='logincust'),
  path('regcust/', myapp.views.regcust, name='regcust'),
  path('clogout/', myapp.views.clogout, name='clogout'),
  path('prediction/', myapp.views.prediction, name='prediction'),
  path("analyze/",myapp.views.analyze),
  path("cart/", myapp.views.cart, name="cart"),
  path("addtocart/",myapp.views.addtocart , name="addtocart"),
  path("updatecart/", myapp.views.updatecart, name="updatecart"),
  path("removecart/<int:cartid>/", myapp.views.removecart, name="removecart"),
  path('checkout/', myapp.views.checkout, name='checkout'),
  path('placeorder/', myapp.views.placeorder, name='placeorder'),
  path('ordersuccess/<int:order_id>/', myapp.views.ordersuccess, name='ordersuccess'),
  path('pendingorders/', views.pendingorders, name='pendingorders'),
  path('allorders/', views.allorders, name='allorders'),
  path('orderdetails/<int:order_id>/', views.orderdetails, name='orderdetails'),
  path('updateorderstatus/', views.updateorderstatus, name='updateorderstatus'),
  path('marketplace/', views.marketplace, name='marketplace'),
  path('myorders/', myapp.views.myorders, name='myorders'),
]
 