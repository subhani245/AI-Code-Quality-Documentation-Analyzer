import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

data = [
    [5,0,0,1,0,9],
    [50,2,5,0,2,3],
    [20,1,2,1,1,6],
    [10,0,0,2,0,8],
    [80,4,10,0,4,2]
]

df = pd.DataFrame(data, columns=[
"num_lines",
"num_loops",
"num_prints",
"num_functions",
"bad_variable_usage",
"score"
])

X = df.drop("score",axis=1)
y = df["score"]

model = RandomForestRegressor()

model.fit(X,y)

joblib.dump(model,"model.pkl")

print("Model trained successfully")