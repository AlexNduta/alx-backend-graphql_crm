import graphene
from graphene_django.types import DjangoObjectType
from crm.models import Product 
from datetime import datetime

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += 10  # Simulate restocking
            product.save()
            updated_products.append(product)

        return UpdateLowStockProducts(
            updated_products=updated_products,
            message=f"{len(updated_products)} products updated at {datetime.now()}"
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
schema = graphene.Schema(mutation=Mutation)

# class Query(graphene.ObjectType):
#     hello = graphene.String(default_value="Hello, GraphQL!")

# schema = graphene.Schema(query=Query)