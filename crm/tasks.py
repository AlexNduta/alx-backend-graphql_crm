from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql/',
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """)

    try:
        result = client.execute(query)

        report = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: "
            f"{result['totalCustomers']} customers, "
            f"{result['totalOrders']} orders, "
            f"{result['totalRevenue']} revenue\n"
        )

    except Exception as e:
        report = f"{datetime.now()} - GraphQL Error: {e}\n"

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(report)
