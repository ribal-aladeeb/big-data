# Add this for dumb relative imports
import sys
sys.path.append(".")


import importlib
from src import utils
from src.preprocessing import step2_feature_engineering as feature_eng

from pyspark.rdd import RDD
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
import json
import copy as cp

from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import BinaryClassificationEvaluator,MulticlassClassificationEvaluator


def driver(takeSample=False):

    # Pre-process features
    data_df, features = feature_eng.preprocess_features(takeSample=takeSample)

    # Split the data into training and test sets (30% held out for testing)
    (trainingData, testData) = data_df.randomSplit([0.7, 0.3])

    # Assemble all features in a vector using Vector Assembler
    # map it to new column named features
    vector_assembler = VectorAssembler(
        inputCols=features, outputCol="features")

    # Train a RandomForest model.
    rf = RandomForestClassifier(
        labelCol="TARGET", featuresCol="features", numTrees=100, maxDepth=10)

    # Chain vector_assembler and forest in a Pipeline
    pipeline = Pipeline(stages=[vector_assembler, rf])

    # Train model.  This also runs the indexers.
    model = pipeline.fit(trainingData)

    # Make predictions.
    predictions = model.transform(testData)
    predictions.select('TARGET', 'rawPrediction','prediction','probability').show(20)

    # Select (prediction, true label) and compute test error
    evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", labelCol="TARGET", metricName='areaUnderROC')
    multi_class_evaluator = MulticlassClassificationEvaluator(predictionCol="prediction", labelCol="TARGET", metricName="f1")
    areaUnderRoc = evaluator.evaluate(predictions)
    f1 = multi_class_evaluator.evaluate(predictions)
    print(f"Area Under ROC = {areaUnderRoc}")
    print(f"F1 = {f1}")

if __name__ == '__main__':
    driver()
