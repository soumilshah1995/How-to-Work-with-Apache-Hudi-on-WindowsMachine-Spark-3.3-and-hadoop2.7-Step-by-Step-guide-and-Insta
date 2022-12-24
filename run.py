"""

Install
https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop2.tgz

hadoop2.7
https://github.com/soumilshah1995/winutils/blob/master/hadoop-2.7.7/bin/winutils.exe

pyspark --packages org.apache.hudi:hudi-spark3.3-bundle_2.12:0.12.1 --conf 'spark.serializer=org.apache.spark.serializer.KryoSerializer'

VAR
SPARK_HOME
HADOOP_HOME


PATH
`%HAPOOP_HOME%\bin`
`%SPARK_HOME%\bin`

Complete Tutorials on HUDI
https://github.com/soumilshah1995/Insert-Update-Read-Write-SnapShot-Time-Travel-incremental-Query-on-APache-Hudi-transacti/blob/main/hudi%20(1).ipynb
"""

try:

    import os
    import sys
    import uuid

    import pyspark
    from pyspark.sql import SparkSession
    from pyspark import SparkConf, SparkContext
    from pyspark.sql.functions import col, asc, desc
    from pyspark.sql.functions import col, to_timestamp, monotonically_increasing_id, to_date, when
    from pyspark.sql.functions import *
    from pyspark.sql.types import *
    from datetime import datetime
    from functools import reduce
    from faker import Faker
    from faker import Faker

    import findspark


except Exception as e:
    pass

SUBMIT_ARGS = "--packages org.apache.hudi:hudi-spark3.3-bundle_2.12:0.12.1 pyspark-shell"
os.environ["PYSPARK_SUBMIT_ARGS"] = SUBMIT_ARGS
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

findspark.init()

spark = SparkSession.builder\
    .config('spark.serializer', 'org.apache.spark.serializer.KryoSerializer') \
    .config('className', 'org.apache.hudi') \
    .config('spark.sql.hive.convertMetastoreParquet', 'false') \
    .config('spark.sql.extensions', 'org.apache.spark.sql.hudi.HoodieSparkSessionExtension') \
    .config('spark.sql.warehouse.dir', 'file:///C:/tmp/spark_warehouse') \
    .getOrCreate()


global faker

faker = Faker()


class DataGenerator(object):

    @staticmethod
    def get_data():
        return [
            (
                x,
                faker.name(),
                faker.random_element(elements=('IT', 'HR', 'Sales', 'Marketing')),
                faker.random_element(elements=('CA', 'NY', 'TX', 'FL', 'IL', 'RJ')),
                faker.random_int(min=10000, max=150000),
                faker.random_int(min=18, max=60),
                faker.random_int(min=0, max=100000),
                faker.unix_time()
            ) for x in range(2)
        ]


data = DataGenerator.get_data()

columns = ["emp_id", "employee_name", "department", "state", "salary", "age", "bonus", "ts"]
spark_df = spark.createDataFrame(data=data, schema=columns)
print(spark_df.show())

db_name = "hudidb"
table_name = "hudi_table"
recordkey = 'emp_id'
precombine = 'ts'

path = "file:///C:/tmp/spark_warehouse"
method = 'upsert'
table_type = "COPY_ON_WRITE"

hudi_options = {
    'hoodie.table.name': table_name,
    'hoodie.datasource.write.recordkey.field': 'emp_id',
    'hoodie.datasource.write.table.name': table_name,
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'ts',
    'hoodie.upsert.shuffle.parallelism': 2,
    'hoodie.insert.shuffle.parallelism': 2
}

print("*"*55)
print("overwrite")
print("*"*55)

spark_df.write.format("hudi"). \
    options(**hudi_options). \
    mode("overwrite"). \
    save(path)

print("*"*55)
print("READ")
print("*"*55)
read_df = spark.read. \
    format("hudi"). \
    load(path)
print(read_df.show())


