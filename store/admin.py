from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models


# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('>10', "Ok"),
            ('0', 'Fail')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '>10':
            return queryset.filter(inventory__gt=10)
        elif self.value() == '0':
            return queryset.filter(inventory=0)


# --------------------------------------------------------------------------------------------------------------------
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {'slug': ['title']}
    actions = ['clear_inventory']
    list_display = ['id', 'title', 'unit_price', 'inventory_status', 'collection']
    list_per_page = 10
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(request, f'{update_count} products were successfully updated.', messages.ERROR)


# --------------------------------------------------------------------------------------------------------------------
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith']

    @admin.display(ordering='orders')
    def orders(self, customer):
        url3 = (reverse('admin:store_order_changelist')
                + '?'
                + urlencode({
                    'customer__id': customer.id
                }))
        return format_html('<a href="{}" >{}</a>', url3, customer.orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders=Count('order'))


# --------------------------------------------------------------------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0
    min_num = 1
    max_num = 5


# --------------------------------------------------------------------------------------------------------------------
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    list_display = ['id', 'placed_at', 'customer', 'cus_num', 'payment_status']
    list_per_page = 10
    search_fields = ['customer__first_name']
    @admin.display(ordering='cus_num')
    def cus_num(self, order):
        url2 = (reverse('admin:store_orderitem_changelist')
                + '?'
                + urlencode({
                    'order__id': order.id
                })
                )
        return format_html('<a href="{}" >{}</a>', url2, order.cus_num)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(cus_num=Count('orderitem'))


# --------------------------------------------------------------------------------------------------------------------
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
                reverse('admin:store_product_changelist')
                + '?'
                + urlencode({
            'collection__id': str(collection.id)
        })
        )
        return format_html('<a href="{}" >{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))


# --------------------------------------------------------------------------------------------------------------------
@admin.register(models.OrderItem)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'order']
    list_per_page = 10
    ordering = ['id']
