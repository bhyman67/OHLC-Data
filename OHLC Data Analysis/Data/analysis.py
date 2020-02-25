
# going to use some of the statistical functions in numpy

import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as sts
import numpy as np

df = pd.read_csv('stock prices.csv')
# print(df)

priceAverage = np.mean(df['close'])
print(priceAverage)