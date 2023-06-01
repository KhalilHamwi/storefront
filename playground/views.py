from django.db.models import Sum, Count
from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product, Customer, Collection, OrderItem, Order


def say_hello(request):
    # collection = Collection(pk=13)
    # collection.title = 'Dota'
    # collection.featured_product_id = None
    # collection.delete()
    # Collection.objects.filter(id__gt=10).delete()
    # collections = Collection.objects.all()
    res = Order.objects.filter(customer__id=1).aggregate(count=Count('id'))
    print('res=', res)
    return render(request, 'hello.html', {'name': 'Mosh', 'res': res})
