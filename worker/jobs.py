import sys
import math
from collections import defaultdict
import matplotlib.pyplot as plt
import os
import pathlib
from file_utils import is_allowed_file
from pymongo import MongoClient

UPLOAD_FOLDER = "uploads"

# Benford's Law percentages for leading digits 1-9
BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]

LOG = {}

# Connecting to MongoDB
client = MongoClient('mongodb', 27017)

# Getting a Database
db = client['app']

# Create Collection Inside MongoDB Database
if not db['result_collection']:
    db.create_collection("result_collection")
else:
    result_collection = db['result_collection']


def load_data(filename):
    """Open a text file & return a list of strings. (lines) """
    df = is_allowed_file(file_name=filename, return_dataframe=True)
    df = df.dropna()
    # Get column name
    column_name = list(df)[0]
    # Transform pandas dataframe to list
    data_list = df[column_name].tolist()
    # Transform elements to ints and later strings
    data_list = [str(int(i)) for i in data_list]
    return data_list


def count_first_digits(data_list):
    """Count 1st digits in list of numbers; return counts & frequency."""
    first_digits = defaultdict(int)  # default value of int is 0
    for sample in data_list:
        if sample == '':
            continue
        try:
            int(sample)
        except ValueError as e:
            # print(e, file=sys.stderr)
            # print("Samples must be integers. Exiting.", file=sys.stderr)
            sys.exit(1)
        first_digits[sample[0]] += 1

        # check for missing digits
    keys = [str(digit) for digit in range(1, 10)]
    for key in keys:
        if key not in first_digits:
            first_digits[key] = 0

    data_count = [v for (k, v) in sorted(first_digits.items())]
    total_count = sum(data_count)
    data_pct = [(i / total_count) * 100 for i in data_count]
    return data_count, data_pct, total_count


def get_expected_counts(total_count):
    """Return list of expected Benford's Law counts for total sample count."""
    return [round(p * total_count / 100) for p in BENFORD]


def chi_square_test(data_count, expected_counts):
    """Return boolean on chi-square test (8 degrees of freedom & P-val=0.05)."""
    chi_square_stat = 0  # chi square test statistic
    for data, expected in zip(data_count, expected_counts):
        chi_square = math.pow(data - expected, 2)
        chi_square_stat += chi_square / expected

    # print("\nChi-squared Test Statistic = {:.3f}".format(chi_square_stat))
    # print("Critical value at a P-value of 0.05 is 15.51.")
    LOG['chi-squared_test_statistic'] = chi_square_stat
    LOG['critical_value_at_p-value_of_0,05'] = "15.51."

    return chi_square_stat < 15.51


def create_bar_chart_image(data_pct, save_path):
    """Make bar chart of observed vs expected 1st digit frequency in percent."""
    fig, ax = plt.subplots()

    index = [i + 1 for i in range(len(data_pct))]  # 1st digits for x-axis

    # text for labels, title and ticks
    fig.canvas.set_window_title('Percentage First Digits')
    ax.set_title('Data vs. Benford Values', fontsize=15)
    ax.set_ylabel('Frequency (%)', fontsize=16)
    ax.set_xticks(index)
    ax.set_xticklabels(index, fontsize=14)

    # build bars
    rects = ax.bar(index, data_pct, width=0.95, color='black', label='Data')

    # attach a text label above each bar displaying its height
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height,
                '{:0.1f}'.format(height), ha='center', va='bottom',
                fontsize=13)

    # plot Benford values as red dots
    ax.scatter(index, BENFORD, s=150, c='red', zorder=2, label='Benford')

    # Hide the right and top spines & add legend
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.legend(prop={'size': 15}, frameon=False)

    # plt.show()
    plt.savefig(save_path)


def run_benford_job(directory_name):
    """Check conformance of numerical data to Benford's Law."""

    plot_save_path = os.path.join("images", f"{directory_name}.png")

    # Load data
    directory_path = os.path.join(UPLOAD_FOLDER, directory_name)
    filename = list(pathlib.Path(directory_path).glob('*.txt'))
    if not filename:
        filename = list(pathlib.Path(directory_path).glob('*.csv'))

    filename = filename[0]  # There should be only one file

    try:
        data_list = load_data(filename)

    except IOError as e:
        return "Unable to load"

    data_count, data_pct, total_count = count_first_digits(data_list)
    expected_counts = get_expected_counts(total_count)

    # print(f"\nobserved counts = {data_count}")
    # print(f"expected counts = {expected_counts}\n")

    LOG['observed_counts'] = data_count
    LOG['expected_counts'] = expected_counts

    # print("First Digit Probabilities:")
    first_digit_probabilities = {}

    for i in range(1, 10):
        # print("{}: observed: {:.3f}  expected: {:.3f}".format(i, data_pct[i - 1] / 100, BENFORD[i - 1] / 100))

        observed = data_pct[i - 1] / 100
        expected = BENFORD[i - 1] / 100

        first_digit_probabilities[str(i)] = [{"observed": observed}, {"expected": expected}]

    LOG['first_digit_probabilities'] = first_digit_probabilities

    # H0: Observed and theoretical distributions are the same

    if chi_square_test(data_count, expected_counts):
        # print("Observed distribution matches expected distribution.")
        LOG['result'] = "Observed distribution matches expected distribution."

    else:
        # print("Observed distribution does not match expected.", file=sys.stderr)
        LOG["result"] = "Observed distribution does not match expected."

    # Insert into database
    post = {"key": str(directory_name), "data": LOG}
    result_collection.insert_one(post)

    create_bar_chart_image(data_pct=data_pct, save_path=plot_save_path)
