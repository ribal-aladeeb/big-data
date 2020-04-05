from src.runners import random_forest
from src.runners import decision_tree
from src.runners import linear_support_vector_machine
from src.runners import naive_bayes
from src.runners import knn
import sys

drivers = [
    random_forest.driver,
    decision_tree.driver,
    linear_support_vector_machine.driver,
    naive_bayes.driver,
    knn.driver
]

if __name__ == '__main__':
    try:
        runner = sys.argv[1] # str
    except Exception as e:
        runner = 'random_forest'

    try:
        takeSample = sys.argv[2] == "sample"  # True if we write sample
    except Exception as e:
        takeSample = False

    print(f"Runner = {runner}", f"Take Sample = {takeSample}")
    if runner == 'all':
        for driver in drivers:
            try:
                driver(takeSample)
            except:
                print(f"{driver} failed to execute.")
    else:
        driver = getattr(globals()[runner], 'driver')
        driver(takeSample=takeSample)

