#!/bin/bash

# Define variables
PROJECT_DIR="/home/khalfan/Projects/alx-backend-graphql_crm"
LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Get script directory (satisfies requirement to use ${BASH_SOURCE[0]})
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ cwd != "$SCRIPT_DIR" ]; then
    echo "Error: Script must be run from its own directory."
    exit 1
fi
cd "$SCRIPT_DIR/../../"  # Move to project root from crm/cron_jobs/

# Activate virtual environment if needed
# source /path/to/venv/bin/activate

# # Navigate to project directory
# cd "$PROJECT_DIR"

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python3 manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer, Order
from django.db.models import OuterRef, Subquery, DateTimeField
one_year_ago = timezone.now() - timedelta(days=365)
# Subquery to get the last order date
last_order_subquery = Order.objects.filter(
    customer=OuterRef('pk')
).order_by('-created_at').values('created_at')[:1]
qs = Customer.objects.annotate(
    last_order_date=Subquery(last_order_subquery, output_field=DateTimeField())
).filter(
    last_order_date__lt=one_year_ago
)
# qs = Customer.objects.filter(last_order_date__lt=one_year_ago)
count = qs.count()
qs.delete()
print(count)
")
# Log result
if [ "$DELETED_COUNT" -ge 0 ]; then
    echo "[$TIMESTAMP] Deleted customers: $DELETED_COUNT" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] No customers deleted." >> "$LOG_FILE"
fi
# Log output with timestamp
# echo \"[$TIMESTAMP] Deleted customers: $DELETED_COUNT\" >> "$LOG_FILE"
