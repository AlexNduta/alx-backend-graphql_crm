from datetime import timedelta
from time import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    first_name = models.CharField(max_length=30, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=30, verbose_name=_("Last Name"))
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("Phone Number"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    def get_contact_info(self):
        return {
            "email": self.email,
            "phone_number": self.phone_number
        }
    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError(_("Email address is required."))
        super().save(*args, **kwargs)
        if not self.first_name or not self.last_name:
            raise ValueError(_("Both first name and last name are required."))
    def delete(self, *args, **kwargs):
        if self.orders.exists():
            raise ValueError(_("Cannot delete customer with existing orders."))
        super().delete(*args, **kwargs)
    @property
    def full_name(self):
        return self.get_full_name()
    @property
    def contact_info(self):
        return self.get_contact_info()
    @property
    def is_active(self):
        return self.orders.filter(status='active').exists()
    @property
    def order_count(self):
        return self.orders.count()
    @property
    def last_order_date(self):
        last_order = self.orders.order_by('-created_at').first()
        return last_order.created_at if last_order else None
    @property
    def recent_orders(self):
        return self.orders.order_by('-created_at')[:5]
    @property
    def has_orders(self):
        return self.orders.exists()
    @property
    def is_new_customer(self):
        return self.created_at >= timezone.now() - timedelta(days=30)

class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, verbose_name=_("Customer"))
    order_number = models.CharField(max_length=20, unique=True, verbose_name=_("Order Number"))
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active', verbose_name=_("Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} for {self.customer.get_full_name()}"
    def save(self, *args, **kwargs):
        if not self.order_number:
            raise ValueError(_("Order number is required."))
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        if self.status == 'active':
            raise ValueError(_("Cannot delete an active order."))
        super().delete(*args, **kwargs)
    @property
    def is_completed(self):
        return self.status == 'completed'
    @property
    def is_cancelled(self):
        return self.status == 'cancelled'
    @property
    def is_active(self):
        return self.status == 'active'
    @property
    def customer_full_name(self):
        return self.customer.get_full_name() if self.customer else None
    @property
    def customer_contact_info(self):
        return self.customer.get_contact_info() if self.customer else None  
    @property
    def days_since_created(self):
        return (timezone.now() - self.created_at).days if self.created_at else None
    @property
    def days_since_updated(self):
        return (timezone.now() - self.updated_at).days if self.updated_at else None
    @property
    def is_recent(self):
        return (timezone.now() - self.created_at).days <= 30 if self.created_at else False
    @property
    def is_old(self):
        return (timezone.now() - self.created_at).days > 30 if self.created_at else False
    @property
    def is_new_order(self):
        return self.created_at >= timezone.now() - timedelta(days=7) if self.created_at else False  
    @property
    def is_returning_customer(self):
        return self.customer.orders.filter(status='completed').count() > 1 if self.customer else False
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_("Order"))
    product_name = models.CharField(max_length=100, verbose_name=_("Product Name"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) in {self.order.order_number}"
    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            raise ValueError(_("Quantity must be greater than zero."))
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        if self.order.status == 'completed':
            raise ValueError(_("Cannot delete items from a completed order."))
        super().delete(*args, **kwargs)
    @property
    def total_price(self):
        return self.quantity * self.price if self.quantity and self.price else 0.0
    @property
    def is_discounted(self):
        return self.price < 100.0  # Example condition for discount
    @property
    def is_high_value(self):
        return self.price > 500.0  # Example condition for high value
    @property
    def is_low_value(self):
        return self.price < 50.0  # Example condition for low value
    @property
    def is_recent_item(self):
        return (timezone.now() - self.created_at).days <= 30 if self.created_at else False
    @property
    def is_old_item(self):
        return (timezone.now() - self.created_at).days > 30 if self.created_at else False
    @property
    def is_new_item(self):
        return self.created_at >= timezone.now() - timedelta(days=7) if self.created_at else False

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Product Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if self.price < 0:
            raise ValueError(_("Price cannot be negative."))
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        if self.stock > 0:
            raise ValueError(_("Cannot delete product with stock available."))
        super().delete(*args, **kwargs)
    @property
    def is_in_stock(self):
        return self.stock > 0
    @property
    def is_out_of_stock(self):
        return self.stock == 0
    @property
    def is_low_stock(self):
        return self.stock < 10