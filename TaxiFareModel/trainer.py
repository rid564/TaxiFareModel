# imports
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from TaxiFareModel.utils import compute_rmse 
from TaxiFareModel.data import get_data, clean_data
from sklearn.model_selection import train_test_split
from TaxiFareModel.encoders import DistanceTransformer, TimeFeaturesEncoder
from sklearn.linear_model import LinearRegression

class Trainer():
    def __init__(self, X, y):
        """
            X: pandas DataFrame
            y: pandas Series
        """
        self.pipeline = None
        self.X = X
        self.y = y

    def set_pipeline(self):

        dist_pipe = Pipeline([
        ('dist_trans', DistanceTransformer()),
        ('stdscaler', StandardScaler())
        ])

        time_pipe = Pipeline([
        ('time_enc', TimeFeaturesEncoder('pickup_datetime')),
        ('ohe', OneHotEncoder(handle_unknown='ignore'))
        ])

        preproc_pipe = ColumnTransformer([
        ('distance', dist_pipe, ["pickup_latitude", "pickup_longitude", 'dropoff_latitude', 'dropoff_longitude']),
        ('time', time_pipe, ['pickup_datetime'])
        ], remainder="drop")
        
        pipe = Pipeline([
        ('preproc', preproc_pipe),
        ('linear_model', LinearRegression())
        ])
        self.pipeline = pipe
        return self.pipeline
        
    
    
    def run(self):
        """set and train the pipeline"""
        self.pipeline.fit(self.X, self.y)
        return self.pipeline
        
        

    def evaluate(self, X_test, y_test):
        """evaluates the pipeline on df_test and return the RMSE"""
        y_pred = self.pipeline.predict(X_test)
        rmse = compute_rmse(y_pred, y_test)
        return rmse


if __name__ == "__main__":
    # get data
    df = get_data()
    clean_df = clean_data(df)
    y = clean_df["fare_amount"]
    X = clean_df.drop("fare_amount", axis=1)

    # hold out
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15)
    trainer =  Trainer(X_train, y_train)

    # build pipeline
    trainer.set_pipeline()

    # train the pipeline
    trainer.run()

    # evaluate the pipeline
    rmse = trainer.evaluate(X_val, y_val)
    print(rmse)
