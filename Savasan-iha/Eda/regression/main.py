import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
import os

train_df = pd.read_csv("train.csv")
print(train_df.head())
train_row, train_col = train_df.shape
print(f"\nThere are {train_row} rows and {train_col} columns in train dataframe.")

test_df = pd.read_csv("test.csv")
print(test_df.head())
test_row, test_col = test_df.shape
print(f"\nThere are {train_row} rows and {train_col} columns in test dataframe")

# y sütununda NaN olan değerleri içeren satıları kaldırır.
train_df.drop(train_df[train_df.y.isnull()].index, inplace=True)

# .values.reshape(-1, 1), bu değerleri bir sütun vektörüne dönüştürür.
X_train = train_df["x"].values.reshape(-1, 1)
y_train = train_df["y"].values.reshape(-1, 1)
x_test = train_df["x"].values.reshape(-1, 1)
y_test = train_df["y"].values.reshape(-1, 1)

# sklearn kütüphenesinden model örneği oluşturulması.
reg = LinearRegression()
# Modelin veri setindeki ilişkinin öğrenilmesi sağlanır
reg.fit(X_train, y_train)
# x_test verisini modele verip, modelin tahmin ettiği y değerleri elde edilir
y_predictions = reg.predict(x_test)
mse = mean_squared_error(y_test, y_predictions)
print(f"The result of MSE is: {mse}")

# Plot the result
plt.scatter(X_train, y_train, color="blue")
plt.plot(x_test, y_predictions, color="black")
plt.show()
