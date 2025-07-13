#!/usr/bin/env python

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import sys

# Set up GraphQL client
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=False)

# Define date range
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Format dates in ISO 8601
start = start_date.isoformat()
end = end_date.isoformat()

# Define query (ensure your schema supports filtering by order_date)
query = gql("""
query GetRecentOrders($start: DateTime!, $end: DateTime!) {
  orders(orderDate_Gte: $start, orderDate_Lte: $end) {
    id
    customer {
      email
    }
  }
}
""")

# Run query
try:
    response = client.execute(query, variable_values={"start": start, "end": end})
    orders = response.get("orders", [])
except Exception as e:
    print(f"Error fetching orders: {e}")
    sys.exit(1)

# Log orders
timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
with open("/tmp/order_reminders_log.txt", "a") as log_file:
    for order in orders:
        log_file.write(f"{timestamp} Order ID: {order['id']}, Email: {order['customer']['email']}\n")

print("Order reminders processed!")
