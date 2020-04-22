import uuid
from datetime import date
import csv


def create_directory_name():
    """Return identifier for directories"""
    id_number = str(uuid.uuid1().int)
    today = date.today()
    date_today = today.strftime("%b-%d-%Y-")
    #return date_today + id_number
    return id_number

def allowed_file(uploaded_file):
    return True
    # try:
    #     with uploaded_file as csvfile:
    #         start = csvfile.read(4096)
    #
    #         # isprintable does not allow newlines, printable does not allow umlauts...
    #         if not all([c in string.printable or c.isprintable() for c in start]):
    #             return False
    #         dialect = csv.Sniffer().sniff(start)
    #         return True
    # except csv.Error:
    #     # Could not get a csv dialect -> probably not a csv.
    #     return False