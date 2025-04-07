import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline to be used in Jupyter Notebook


# Read the house data into a data frame
df = pd.read_csv('streams.csv')

# Target variable = viewer count
# Features to predict variable = all other variables
target = df.iloc[:, 10].name

# Take only relevant columns

df = df[['viewer_count','started_at', 'is_mature', ]]
df['is_mature'] = df['is_mature'].astype(int)

# Change date time format to numeric
df['started_at'] = pd.to_datetime(df['started_at'])
df['started_at'] = pd.to_numeric(df['started_at'], downcast='integer')

print(df.head())
print(df.describe())

# Correlations of features with target variable
correlations = df.corr()
print(correlations['viewer_count'])

#nomralize functions
df.iloc[:, 1:] = ((df - df.mean())/df.std())
X = df.iloc[:, 1:]
ones = np.ones([len(df), 1])
X = np.concatenate((ones, X), axis=1)
y = df.iloc[:, 0:1].values

features = df.iloc[:, 1:].columns.tolist()
len_of_features = len(features)

theta = np.zeros([1, len_of_features + 1])

# Store target
target = y

# Define computecost function
def computecost(X, y, theta):
    H = X @ theta.T
    J = np.power((H - y), 2)
    sum = np.sum(J)/(2 * len(X))
    return sum

# Set iterations and alpha (learning rate)
alpha = 0.01
iterations = 500

# Define gradientdescent function
def gradientdescent(X, y, theta, iterations, alpha):
    cost = np.zeros(iterations)
    for i in range(iterations):
        H = X @ theta.T
        theta = theta - (alpha/len(X)) * np.sum(X * (H - y), axis=0)
        cost[i] = computecost(X, y, theta)
    return theta, cost


# Do Gradient Descent and print final theta
final_theta, cost = gradientdescent(X, y, theta, iterations, alpha)
print("Final theta is:", final_theta)

# Compute and print final cost
final_cost = computecost(X, y, final_theta)
print("Final Viewers is:", final_cost)

# Plot Iterations vs. Cost
fig_2, ax = plt.subplots(figsize=(10, 8))
ax.plot(np.arange(iterations), cost, 'r')
ax.set_xlabel('Iterations')
ax.set_ylabel('Viewers')
ax.set_title('Iterations vs. Viewers')
plt.show()

predictions = X @ final_theta.T
print(str(predictions[3].round(2)))