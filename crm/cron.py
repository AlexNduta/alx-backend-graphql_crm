import datetime
from itertools import product
import sys
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport, post



def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_entry = f"{timestamp} CRM is alive\n"
    log_path = "/tmp/crm_heartbeat_log.txt"

    # Log the heartbeat
    with open(log_path, "a") as log_file:
        log_file.write(log_entry)

    # Optional: Check GraphQL hello query
    try:
        response = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        ).execute(gql("{ hello }"))
        if response:
            print("GraphQL endpoint is responsive.")
    except Exception as e:
        response = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        ).execute(gql("{ hello }"))
        print(f"Error checking GraphQL endpoint: {e}")
        sys.exit(1)
        
    print("CRM heartbeat logged successfully.")


def update_low_stock():
    url = "http://localhost:8000/graphql/"
    query = '''
    mutation {
        updateLowStockProducts {
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    '''

    try:
        # response = requests.post(url, json={'query': query})
        transport = RequestsHTTPTransport(
            url=url,
            use_json=True,
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        response = client.execute(gql(query))
        data = response
        if "errors" in data:
            log_msg = f"{datetime.now()} - GraphQL Error: {data['errors']}\n"
        else:
            result = data['data']['updateLowStockProducts']
            log_msg = f"{datetime.now()} - {result['message']}\n"
            for p in result['updatedProducts']:
                log_msg += f" - {p['name']} updated to stock: {p['stock']}\n"

    except Exception as e:
        log_msg = f"{datetime.now()} - Exception occurred: {e}\n"

    with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
        log_file.write(log_msg)
