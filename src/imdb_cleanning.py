import pyspark.sql.functions as f
import pyspark.sql.types as t
from unidecode import unidecode
from variables import FILE_PATHS

@f.udf(returnType=t.StringType())
def unidecode_udf(string) : 
    if not string : 
        return None 
    else :
        return unidecode(string)


class ImdbCleaner : 

    def __init__(self, spark_session) :

        self.spark = spark_session
        self.read_options = {
            "header" : True,
            "sep" : "\t"
        }

    def read_data(self) : 

        self.df_basics = (
            self.spark
            .read
            .format('csv')
            .options(**self.read_options)
            .load(FILE_PATHS['basics'])
        )

        self.df_ratings = (
            self.spark
            .read
            .format("csv")
            .options(**self.read_options)
            .load(FILE_PATHS['ratings'])
        )

    def data_cleanning(self) : 

        self.df_cleaned = self.df_basics

        #integer columns 
        int_cols = ['startYear','endYear','runtimeMinutes','isAdult']
        #cleanning integers
        for c in int_cols :
            self.df_cleaned = (
                self.df_cleaned
                .withColumn(c, f.col(c).cast('int'))
            )

        #string columns
        str_cols = ['primaryTitle','originalTitle','titleType']
        for c in str_cols : 
            self.df_cleaned = (
                self.df_cleaned
                .withColumn(c,unidecode_udf(f.col(c)))
            )


        #Limpezas específicas
        self.df_cleaned = (
            self.df_cleaned
            .replace("\\N",None)
            .withColumn("genres",f.split(f.col("genres"),","))
        )


    def join_data(self):

        self.df_final = (
            self.df_cleaned
            .join(self.df_ratings, ['tconst'])    
        )


    def write_data(self) : 
        (
            self.df_final
            .write
            .format("parquet")
            .mode("overwrite")
            .save('/content/drive/MyDrive/igti_bootcamps/eng_dados_cloud/mod3/title_basics_with_rating')
        )

    def clean(self) : 

        self.read_data()
        self.data_cleanning()
        self.join_data()
        self.write_data()
