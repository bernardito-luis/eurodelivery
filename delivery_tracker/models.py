from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail


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
    'deleted': 9,
}
ARCHIVE_STATUS = (
    2,
    8,
)


class PurchaseOrderStatus(models.Model):
    # Table init
    # statuses = (
    #   "Черновик", "Отменено", "Запрошено", "Ожидает оплаты",
    #   "Заказ исполнятеся", "Ожидается послупление на склад",
    #   "Частично получено", "Получено на склад", "Удалено")
    # [PurchaseOrderStatus.objects.create(description=s) for s in statuses]
    description = models.CharField(max_length=64)

    def __str__(self):
        return str(self.id) + ': ' + self.description

    class Meta:
        db_table = 'purchase_order_status'


class PurchaseOrder(models.Model):
    user = models.ForeignKey('auth.User')
    status = models.ForeignKey(PurchaseOrderStatus)
    shipping_cost = models.FloatField(default=0)
    fee = models.FloatField(default=CURRENT_FEE)
    coupon = models.CharField(max_length=64, null=True, blank=True)
    discount = models.FloatField(default=0)
    user_comment = models.CharField(
        max_length=255, null=True, blank=True, default=''
    )
    admin_comment = models.CharField(
        max_length=255, null=True, blank=True, default=''
    )

    @property
    def product_qty(self):
        return Product.objects.filter(purchase_order=self).count()

    @property
    def complex_price(self):
        products_price = sum(
            p.sum_price for p in Product.objects.filter(purchase_order=self)
        )
        return products_price + self.shipping_cost + self.fee - self.discount

    def __str__(self):
        return 'Order id: ' + str(self.id)

    class Meta:
        db_table = 'purchase_order'


class StatusLog(models.Model):
    date_modified = models.DateTimeField(auto_now=True)
    purchase_order = models.ForeignKey(PurchaseOrder)
    status = models.ForeignKey(PurchaseOrderStatus)

    def __str__(self):
        return '%s | Заказ #%d статус: %s' % (
            self.date_modified.strftime('%Y-%m-%d %H:%M:%S'),
            self.purchase_order_id,
            self.status.description
        )

    class Meta:
        db_table = 'status_log'


@receiver(pre_save)
def order_pre_save(sender, instance, *args, **kwargs):
    if sender == PurchaseOrder:
        if not instance.id:
            # new order
            return

        new_status = instance.status
        order = PurchaseOrder.objects.get(id=instance.id)
        old_status = order.status
        if old_status != new_status:
            # send mail to admin
            send_mail(
                'Смена статуса заказа',
                'Статус заказа №%d изменился с %s на %s '
                '(пользователь %s)' % (
                    instance.id, old_status, new_status,
                    instance.user.username
                ),
                settings.EMAIL_HOST_USER,
                [User.objects.get(id=1).email, ],
                fail_silently=False,
            )
            # send mail to user
            send_mail(
                'Смена статуса заказа',
                'Статус заказа №%d изменился с %s на %s' % (
                    instance.id, old_status, new_status),
                settings.EMAIL_HOST_USER,
                [instance.user.username, ],
                fail_silently=False,
            )
            StatusLog.objects.create(
                purchase_order=order,
                status=new_status
            )


class Product(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, blank=True, null=True)
    user = models.ForeignKey('auth.User')
    shop_link = models.CharField(max_length=1024, blank=True, null=True)
    product_link = models.CharField(max_length=1024, blank=True, null=True)
    vendor_code = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=32, blank=True, null=True)
    size = models.CharField(max_length=32, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discount_code = models.CharField(max_length=64, blank=True, null=True)
    discount_in_shop = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    @property
    def sum_price(self):
        return self.quantity * self.price - self.discount_in_shop

    @property
    def shop_link_trimmed(self):
        if len(self.shop_link) >= 77:
            return self.shop_link[:77] + '...'
        return self.shop_link

    def __str__(self):
        return 'id_' + str(self.id) + ' ' + self.name

    class Meta:
        db_table = 'product'
