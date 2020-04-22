import csv
import string

# sniffer = csv.Sniffer()
# dialect = sniffer.sniff('quarter, dime, nickel, penny')
# print(dialect.delimiter)


def allowed_file(unknown_file):
    try:
        start = unknown_file.read(4096)

        # isprintable does not allow newlines, printable does not allow umlauts...
        if not all([c in string.printable or c.isprintable() for c in start]):
            return False
        dialect = csv.Sniffer().sniff(start)
        return True
    except csv.Error:
        # Could not get a csv dialect -> probably not a csv.
        return False


print(allowed_file("census_2009.csv"))