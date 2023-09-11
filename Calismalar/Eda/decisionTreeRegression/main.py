from sklearn import tree

X = [[0, 0], [2, 2]]
y = [0.5, 2.5]

clf = tree.DecisionTreeRegressor()
clf = clf.fit(X, y)

print(clf.predict([[3, 3]]))