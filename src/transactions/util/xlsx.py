from decimal import Decimal
from typing import List
from transactions.models import Transaction


def parse_transaction_to_list(transaction: Transaction) -> List[str]:
    date = transaction.date.strftime("%d/%m/%Y")
    amount = str(transaction.amount)
    return [
        date,
        transaction.get_category_display(),
        transaction.description,
        Decimal(amount)
    ]
