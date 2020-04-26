import uuid
from datetime import date
import csv
import pandas as pd


def create_directory_name():
    """Return identifier for directories"""
    id_number = str(uuid.uuid1().int)
    # today = date.today()
    # date_today = today.strftime("%b-%d-%Y-")
    # return date_today + id_number
    return id_number


def open_file(file_name, rows=1):
    """Return head of file (rows number)"""
    # Generator won't load whole file into memory
    csv_gen = (row for row in open(file_name))
    head = []
    for i in range(rows):
        try:
            head.append(next(csv_gen))
        except StopIteration:
            break
    return head


def is_allowed_file(file_name, return_dataframe=False):
    """By default performs quick check on a file. If return_dataframe==True returns pandas dataframe from file"""

    # Use nums to filter out non-number columns
    nums = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    lines = open_file(file_name)

    if not lines:
        return False, "File is empty"

    lines = ''.join(lines)
    try:
        # Try to detect csv separator.
        dialect = csv.Sniffer().sniff(lines, delimiters=',|;\t')

    except Exception:
        # print("Couldn't recognize column delimiter. Maybe it's a one column file?")

        try:
            df = pd.read_csv(file_name).head()
            filtered_df = df.select_dtypes(include=nums)
        except Exception:
            return False, "Cant process. Bad file structure"

        else:
            if filtered_df.empty:
                return False, "File doesn't any numeric columns"

            else:
                # OK
                if return_dataframe:
                    df = pd.read_csv(file_name)
                    df = df.select_dtypes(include=nums)
                    return df
                else:
                    return True, "One column file"

    else:
        df = pd.read_csv(file_name, sep=dialect.delimiter).head()
        filtered_df = df.select_dtypes(include=nums)

        if filtered_df.empty:
            return False, "File doesn't contain numeric columns"

        elif len(filtered_df.columns) > 2:
            return False, "File contains too many numeric columns"

        else:
            # OK
            if return_dataframe:
                df = pd.read_csv(file_name, sep=dialect.delimiter)
                df = df.select_dtypes(include=nums)
                return df
            else:
                return True, f"CSV File. Found delimiter:'{dialect.delimiter}'"


if __name__ == "__main__":
    pass

