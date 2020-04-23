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
        # print("File is empty")
        return False

    lines = ''.join(lines)
    try:
        # Try to detect csv separator.
        dialect = csv.Sniffer().sniff(lines, delimiters=',|;\t')
        # if dialect.delimiter:
        # print(f"Found delimiter:'{dialect.delimiter}'")

    except Exception:
        # print("Couldn't recognize column delimiter. Maybe it's a one column file?")

        try:
            df = pd.read_csv(file_name).head()
            filtered_df = df.select_dtypes(include=nums)
        except Exception:
            # print("Cant process. Bad file structure")
            return False

        else:
            if filtered_df.empty:
                # print("File doesn't any numeric columns")
                return False
            else:
                # print("Accepted")
                if return_dataframe:
                    df = pd.read_csv(file_name)
                    df = df.select_dtypes(include=nums)
                    # print(df)
                    return df
                else:
                    return True

    else:
        df = pd.read_csv(file_name, sep=dialect.delimiter).head()
        filtered_df = df.select_dtypes(include=nums)

        if filtered_df.empty:
            # print("File doesn't contain numeric columns")
            return False
        elif len(filtered_df.columns) > 2:
            # print("File contains too many numeric columns")
            return False
        else:
            # print("Accepted")
            if return_dataframe:
                df = pd.read_csv(file_name, sep=dialect.delimiter)
                df = df.select_dtypes(include=nums)
                # print(df)
                return df
            else:
                return True



if __name__ == "__main__":
    pass
    #is_allowed_file("../../checking/check/PythonStackTraces.txt")
    #is_allowed_file("../../checking/check/empty.txt")
    #is_allowed_file("../../checking/check/Illinois_votes.txt")
    #is_allowed_file("../../checking/check/no_nums.txt")
    #is_allowed_file("../../checking/check/cenzo.txt")

