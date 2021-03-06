# Add this for dumb relative imports
import sys
sys.path.append(".")

from pyspark.rdd import RDD
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
import os

def dump(rdd, fn="out"):
    if isinstance(rdd, DataFrame):
        rdd = rdd.rdd
    with open(fn, 'w+') as f:
        text = rdd.map(lambda row: str(row) + "\n").reduce(lambda row1,row2: row1+ row2)
        f.write(text)
    return True

def init_spark():
    spark = SparkSession \
        .builder \
        .appName("Home Credit Loan Job") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()
    return spark

def get_project_root_dir() -> str:
    # because the root of the project contains the .git/ repo
    while not os.path.isdir('.git/'):
        if os.getcwd() == '/':
            print('\nYou are trying to get the root folder of the big data project')
            print('but you are running this script outside of the project.')
            print('Navigate to your big data directory and try again')
            exit(1)
        else:
            os.chdir('..')
    if sys.platform == "linux":
        return f'{os.getcwd()}/'
    elif sys.platform == "win32":
        return f'{os.getcwd()}/'
    else:
        raise OSError("Not implemented for Mac OS")
        return f'file://{os.getcwd()}/' # change for mac
