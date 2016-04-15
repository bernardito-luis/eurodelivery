from django.contrib import admin

from delivery_tracker.models import (
    PurchaseOrder, Product, PurchaseOrderStatus, StatusLog
)

admin.site.register(PurchaseOrder)
admin.site.register(Product)
admin.site.register(PurchaseOrderStatus)
admin.site.register(StatusLog)
