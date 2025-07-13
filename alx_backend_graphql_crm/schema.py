from graphene import ObjectType
from graphene import String, Int, Field, List
from graphene import Schema
from graphene import Mutation, InputObjectType


from graphene import ObjectType, String, Int, Field, List, Schema, Mutation, InputObjectType, ID, Decimal, DateTime
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
import graphene
import re

from crm.models import Customer, Product, Order
from graphene_django import DjangoObjectType

# === GraphQL Types ===
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# === Input Types ===
class CreateCustomerInput(InputObjectType):
    name = String(required=True)
    email = String(required=True)
    phone = String()

class CreateProductInput(InputObjectType):
    name = String(required=True)
    price = Decimal(required=True)
    stock = Int(default_value=0)

class CreateOrderInput(InputObjectType):
    customer_id = ID(required=True)
    product_ids = List(ID, required=True)
    order_date = DateTime()

# === Mutations ===

class CreateCustomer(Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = Field(CustomerType)
    message = String()

    def mutate(root, info, input):
        if input.phone and not re.match(r'^(\+?\d{10,15}|(\d{3}-\d{3}-\d{4}))$', input.phone):
            raise graphene.GraphQLError("Invalid phone format.")

        if Customer.objects.filter(email=input.email).exists():
            raise graphene.GraphQLError("Email already exists.")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(Mutation):
    class Arguments:
        input = List(CreateCustomerInput, required=True)

    customers = List(CustomerType)
    errors = List(String)

    def mutate(root, info, input):
        created = []
        errors = []

        for i, data in enumerate(input):
            try:
                if data.phone and not re.match(r'^(\+?\d{10,15}|(\d{3}-\d{3}-\d{4}))$', data.phone):
                    raise ValidationError("Invalid phone format.")

                if Customer.objects.filter(email=data.email).exists():
                    raise ValidationError("Email already exists.")

                customer = Customer(name=data.name, email=data.email, phone=data.phone)
                customer.full_clean()
                customer.save()
                created.append(customer)
            except Exception as e:
                errors.append(f"Entry {i}: {str(e)}")

        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = Field(ProductType)

    def mutate(root, info, input):
        if input.price <= 0:
            raise graphene.GraphQLError("Price must be a positive number.")
        if input.stock < 0:
            raise graphene.GraphQLError("Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock
        )
        return CreateProduct(product=product)

class CreateOrder(Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = Field(OrderType)

    def mutate(root, info, input):
        if not input.product_ids:
            raise graphene.GraphQLError("At least one product must be selected.")

        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise graphene.GraphQLError("Invalid customer ID.")

        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise graphene.GraphQLError("One or more product IDs are invalid.")

        total_amount = sum(product.price for product in products)
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.products.set(products)
        return CreateOrder(order=order)

# === Query and Mutation Entry Point ===

class Query(ObjectType):
    hello = String(greetings=String(default_value="Hello, GraphQL!"))

    def resolve_hello(self, info, greetings):
        return f"{greetings}!"

class Mutation(ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# You can now import this Query and Mutation into your main schema

class Query(ObjectType):
    hello = String(greetings=String(default_value="Hello, GraphQL"))

    def resolve_hello(self, info, greetings):
        return f"{greetings}!"

# schema = Schema(query=Query)
schema = graphene.Schema(query=Query, mutation=Mutation)