
from django.urls import path
import myapp.views
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
]
 