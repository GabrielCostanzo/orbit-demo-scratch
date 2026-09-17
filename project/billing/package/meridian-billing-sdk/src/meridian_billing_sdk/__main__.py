"""Preview a batch of invoices."""

import argparse

from meridian_billing_sdk import read_invoices, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("invoices", help="invoice JSON file")
    args = parser.parse_args()
    try:
        invoices = read_invoices(args.invoices)
        print(summary(invoices))
    except (OSError, ValueError) as error:
        parser.exit(1, f"meridian-invoices: {error}\n")


if __name__ == "__main__":
    main()
