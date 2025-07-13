import graphene
from crm.schema import Query as CrmQuery, Mutation as CrmMutation

class Query(CrmQuery, graphene.ObjectType):
    pass

class Mutation(CrmMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
