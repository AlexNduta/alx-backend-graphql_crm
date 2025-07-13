import graphene
from .models import Product, Customer, Order  # Ensure all models are imported
from graphene_django.types import DjangoObjectType

# Product GraphQL Type
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")


# Mutation: Update Low Stock Products
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            message=f"{len(updated)} product(s) restocked."
        )


# CRM Report Queries
class Query(graphene.ObjectType):
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()

    def resolve_total_customers(self, info):
        return Customer.objects.count()

    def resolve_total_orders(self, info):
        return Order.objects.count()

    def resolve_total_revenue(self, info):
        return sum(order.total_amount for order in Order.objects.all())


# Root Mutation
class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

