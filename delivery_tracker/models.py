from django.db import models


CURRENT_FEE = 5


class UserRegistrationLink(models.Model):
    created_date = models.DateTimeField()
    user = models.ForeignKey('auth.User')
    slug = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'user_registration_link'


PURCHASE_ORDER_STATUS = {
    'draft': 1,
    'canceled': 2,
    'ordered': 3,
    'waits_for_payment': 4,
    'in_progress': 5,
    'coming_to_storage': 6,
    'received_partially': 7,
    'received_to_stock': 8,
}


class PurchaseOrderStatus(models.Model):
    # Table init
    # statuses = (
    #   "Черновик", "Отменено", "Запрошено", "Ожидает оплаты",
    #   "Заказ исполнятеся", "Ожидается послупление на склад",
    #   "Частично получено", "Получено на склад")
    # [PurchaseOrderStatus.objects.create(description=s) for s in statuses]
    description = models.CharField(max_length=64)

    class Meta:
        db_table = 'purchase_order_status'


class PurchaseOrder(models.Model):
    user = models.ForeignKey('auth.User')
    status = models.ForeignKey(PurchaseOrderStatus)
    shipping_cost = models.FloatField(default=0)
    fee = models.FloatField(default=CURRENT_FEE)
    coupon = models.CharField(max_length=64, null=True, blank=True)
    discount = models.FloatField(default=0)
    user_comment = models.CharField(max_length=255, null=True, blank=True)
    admin_comment = models.CharField(max_length=255, null=True, blank=True)

    @property
    def product_qty(self):
        return Product.objects.filter(purchase_order=self).count()

    @property
    def complex_price(self):
        return 'to be implemented'

    class Meta:
        db_table = 'purchase_order'


class Product(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, blank=True, null=True)
    user = models.ForeignKey('auth.User')  # don't like this duplication...
    shop_link = models.CharField(max_length=1024, blank=True, null=True)
    product_link = models.CharField(max_length=1024)
    vendor_code = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=32)
    size = models.CharField(max_length=32)
    quantity = models.IntegerField()
    price = models.FloatField()
    discount_code = models.CharField(max_length=64, blank=True, null=True)
    discount_in_shop = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'product'
