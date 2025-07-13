from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from datetime import timedelta, timezone as dt_timezone
import random
from faker import Faker
from crm.models import Customer, Order, OrderItem 
fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with test data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        self.seed_customers()
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
    
    # def seed_customers(self, num=10):
    #     for _ in range(num):
    #         customer = Customer.objects.create(
    #             first_name=fake.first_name(),
    #             last_name=fake.last_name(),
    #             email=fake.unique.email(),
    #             phone_number=fake.phone_number(),
    #             created_at=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=dt_timezone.utc),
    #         )

    #         self.create_orders(customer, num_orders=random.randint(1, 5))
    def seed_customers(self, customer=None):
        customer = Customer.objects.first()  # or use get(pk=...) if you know the ID
    
        # Set date to exactly one year ago
        one_year_ago = timezone.now() - timedelta(days=365)

        # Create the order manually
        order = Order.objects.create(
            customer=customer,
            order_number="ORD123456789",
            status='completed',
            created_at=one_year_ago,
            updated_at=one_year_ago
        )
    # def create_orders(self, customer, num_orders=2):
    #     for _ in range(num_orders):
    #         created_at = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=dt_timezone.utc)
    #         order = Order.objects.create(
    #             customer=customer,
    #             order_number=fake.unique.bothify(text="ORD#######"),
    #             status=random.choice(['active', 'completed', 'cancelled']),
    #             created_at=created_at,
    #             updated_at=created_at + timedelta(days=random.randint(0, 30))
    #         )
    #         self.create_order_items(order)

    # def create_order_items(self, order, num_items=None):
    #     if num_items is None:
    #         num_items = random.randint(1, 4)

    #     for _ in range(num_items):
    #         OrderItem.objects.create(
    #             order=order,
    #             product_name=fake.word().capitalize(),
    #             quantity=random.randint(1, 5),
    #             price=round(random.uniform(10.0, 1000.0), 2)
    #         )
