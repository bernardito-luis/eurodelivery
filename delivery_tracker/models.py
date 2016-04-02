from django.db import models


class UserRegistrationLink(models.Model):
    created_date = models.DateTimeField()
    user = models.ForeignKey('auth.User')
    slug = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'user_registration_link'


class PurchaseOrderStatus(models.Model):
    # Table init
    # statuses = (
    #   "Черновик", "Отменено", "Запрошено", "Ожидает оплаты",
    #   "Заказ исполнятеся", "Ожидается послупление на склад",
    #   "Частично получено", "Получено насклад")
    # [PurchaseOrderStatus.objects.create(description=s) for s in statuses]
    description = models.CharField(max_length=64)

    class Meta:
        db_table = 'purchase_order_status'


class PurchaseOrder(models.Model):
    user = models.ForeignKey('auth.User')
    status = models.ForeignKey(PurchaseOrderStatus)
    shipping_cost = models.FloatField(default=0)
    coupon = models.CharField(max_length=64)
    user_comment = models.CharField(max_length=255)
    admin_comment = models.CharField(max_length=255)

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
    discount_in_shop = models.CharField(max_length=64, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'product'
