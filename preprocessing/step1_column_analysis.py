from pyspark.rdd import RDD
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
import json
import copy as cp
import os

'''
This script counts the number of missing values for each column of each file in
the training set and outputs a report to 'missing_values.json'. Keep in mind
that this can take ~7min.
'''


def get_project_root_dir():
    # because the root of the project contains the .git/ repo
    while not os.path.isdir('.git/'):
        if os.getcwd() is '/':
            print('\nYou are trying to get the root folder of the big data project')
            print('but you are running this script outside of the project.')
            print('Navigate to your big data directory and try again')
            exit(1)
        else:
            os.chdir('..')

    return os.getcwd()


project_root = get_project_root_dir()

filenames = [
    'bureau_balance.csv',
    'bureau.csv',
    'credit_card_balance.csv',
    'installments_payments.csv',
    'POS_CASH_balance.csv',
    'previous_application.csv',
    'HomeCredit_columns_description.csv',
    'application_train.csv',
]
json_output_file = 'missing_values.json'
csv_output_file = 'missing_values.csv'

# Initialize a spark session.


def init_spark():
    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()
    return spark


def driver():
    report = analyse_columns_in_all_data_files(filenames)

    json_string = json.dumps(report, indent=True)
    with open(json_output_file, 'w') as file:
        file.write(json_string)

    generate_csv_from_json(json_output_file, csv_output_file)

    print(f'View {json_output_file} and {csv_output_file} for result')


def find_missing_by_column(data, column):
    total_records = data.count()
    count_missing = data.where(f"{column} is null").count()
    percent = round(count_missing/total_records*100, 2)
    return (count_missing, percent)


def generate_dict_of_missing_values(filename):
    spark = init_spark()
    data = spark.read.csv(filename, header=True)
    columns = data.columns
    report = {"columns": {}, "complete_features": 0}
    iteration = 0

    for feature in columns:
        iteration += 1
        absolute, percent = find_missing_by_column(data, feature)
        report["columns"][feature] = {
            "missing_values": absolute,
            "percentage": percent
        }
        if absolute == 0:
            report["complete_features"] += 1

        # printing progress given that script can take ~7min to run
        progress = iteration/len(columns)*100
        if iteration % 5 == 0:
            print(f"progress: {round(progress,1)}%")

    return report


def analyse_columns_in_all_data_files(filenames):
    final_report = {}
    for file in filenames:
        file_path = f'{project_root}{file}'
        print(f'generating report for file: {file}')
        final_report[file] = generate_dict_of_missing_values(file_path)
    return final_report


def generate_csv_from_json(json_filename: str, output_file):

    text: str = ',Filename, Column Name, Missing Values, Percentage Missing\n'
    count = 0
    with open(json_filename) as report_file:

        report: dict = json.loads(report_file.read())
        filenames: list = sorted(report.keys())

        for file in filenames:

            columns = sorted(
                report[file]["columns"], key=lambda column: report[file]["columns"][column]["missing_values"])

            for column in columns:
                count += 1
                missing_values = str(
                    report[file]["columns"][column]["missing_values"])

                percent = str(report[file]["columns"][column]["percentage"])
                text += f'{count}, {file}, {column}, {missing_values}, {percent}\n'

    with open(output_file, 'w') as file:
        file.write(text)


driver()
