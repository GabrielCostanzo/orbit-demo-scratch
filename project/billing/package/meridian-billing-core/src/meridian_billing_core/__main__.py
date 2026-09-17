import argparse

from meridian_billing_core import process
from meridian_billing_sdk import summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Process the demo invoices into ledger entries.")
    parser.add_argument("invoices", help="invoice JSON file")
    args = parser.parse_args()
    try:
        invoices, entries = process(args.invoices)
        debit = sum(entry.debit_cents for entry in entries)
        credit = sum(entry.credit_cents for entry in entries)
        print(summary(invoices))
        print(f"{len(entries)} ledger entries · debit ${debit // 100}.{debit % 100:02d} = credit ${credit // 100}.{credit % 100:02d}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"meridian-billing: {error}\n")


if __name__ == "__main__":
    main()
