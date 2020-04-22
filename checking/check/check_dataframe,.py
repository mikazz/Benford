import numpy as np
import pandas as pd
import sys
import math
from collections import defaultdict
import matplotlib.pyplot as plt


def load_data(filename, var):
    df = pd.read_csv(filename)
    data = df[var]
    print(data)
    return df, data


df, data = load_data("census_2009.txt", 2)


# Headers
#print(list(df.columns.values))

# # Data exploratory
# df.describe()
# df.info()
# df.describe().transpose
# print(df.isnull().sum())



