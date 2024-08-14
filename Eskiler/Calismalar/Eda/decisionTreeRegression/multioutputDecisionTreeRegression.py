import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import DecisionTreeRegressor

# Create a random dataset
rng = np.random.RandomState(1)
X = np.sort(200 * rng.rand(100, 1) - 100, axis=0)
y = np.array([np.pi * np.sin(X).ravel(), np.pi * np.cos(X).ravel()]).T
y[::5, :] += 0.5 - rng.rand(20, 2)

regr_d2 = DecisionTreeRegressor(max_depth=2)
regr_d5 = DecisionTreeRegressor(max_depth=5)
regr_d8 = DecisionTreeRegressor(max_depth=8)

regr_d2.fit(X, y)
regr_d5.fit(X, y)
regr_d8.fit(X, y)

# Predict
X_test = np.arange(-100.0, 100.0, 0.01)[:, np.newaxis]
y_d2 = regr_d2.predict(X_test)
y_d5 = regr_d5.predict(X_test)
y_d8 = regr_d8.predict(X_test)

plt.figure()
# c : noktaların rengini belirler
# s : noktaların boyutunu belirler
# edgecolor : noktaların kenar rengini belirler
plt.scatter(y[:, 0], y[:, 1], c="navy", s=25, edgecolors="black", label="data")
plt.scatter(y_d2[:, 0], y_d2[:, 1], c="cornflowerblue", s=25, edgecolors="black", label="d2")
plt.scatter(y_d5[:, 0], y_d5[:, 1], c="red", s=25, edgecolors="black", label="d5")
plt.scatter(y_d8[:, 0], y_d8[:, 1], c="orange", s=25, edgecolors="black", label="d8")

# sınırları belirler
plt.xlim([-6, 6])
plt.ylim([-6, 6])
# eksene isim verir
plt.xlabel("target 1")
plt.ylabel("target 2")
# grafiğe başlık koyar
plt.title("Multi-output Decision Tree Regression")
# dataları açıklar
plt.legend(loc="best")
plt.show()