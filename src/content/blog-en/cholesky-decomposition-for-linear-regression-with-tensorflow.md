---
title: Cholesky Decomposition for Linear Regression with TensorFlow
description: "Although Linear Least Squares Regression is simple and precise, it can be inefficient when matrices get very large. Cholesky decomposition is another approach to solve matrices efficiently by Linear L…"
publishDate: 2018-01-20
tags:
  - linear-regression
coverImage: https://images.alexisalulema.com/blog/cholesky-decomposition-for-linear-regression-with-tensorflow/screen-shot-2018-01-20-at-8-45-10-pm.png
lang: en
draft: false
---

Although [Linear Least Squares Regression](http://alexisalulema.com/2018/01/18/linear-least-squares-regression-with-tensorflow/) is simple and precise, it can be inefficient when matrices get very large. Cholesky decomposition is another approach to solve matrices efficiently by Linear Least Squares, as it decomposes a matrix into a lower and upper triangular matrix (L and LT). Finally, linear regression with Cholesky decomposition is similar to Linear Least Squares reduced to solving a system of linear equations:

![LSER_03](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/lser_03.png)
![Screen Shot 2018-01-20 at 8.45.10 PM](https://images.alexisalulema.com/blog/cholesky-decomposition-for-linear-regression-with-tensorflow/screen-shot-2018-01-20-at-8-45-10-pm.png)
Cholesky Decomposition is already implemented in TensorFlow (which should be applied to XTX), nevertheless, you can see how this matrix can be found in the following link: [Cholesky Decomposition](https://rosettacode.org/wiki/Cholesky_decomposition).

Now, let's see how to implement it with TensorFlow:

```
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

sess = tf.Session()

x_vals = np.linspace(start=0, stop=10, num=100)
y_vals = x_vals + np.random.normal(loc=0, scale=1, size=100)

x_vals_column = np.transpose(np.matrix(x_vals))
ones_column = np.transpose(np.matrix(np.repeat(a=1, repeats=100)))
X = np.column_stack((x_vals_column, ones_column))
Y = np.transpose(np.matrix(y_vals))
X_tensor = tf.constant(X)
Y_tensor = tf.constant(Y)

tX_X = tf.matmul(tf.transpose(X_tensor), X_tensor)
L = tf.cholesky(tX_X)
tX_Y = tf.matmul(tf.transpose(X_tensor), Y)
sol1 = tf.matrix_solve(L, tX_Y)
sol2 = tf.matrix_solve(tf.transpose(L), sol1)

solution_eval = sess.run(sol2)
m_slope = solution_eval
b_intercept = solution_eval
print('slope (m): ' + str(m_slope))
print('intercept (b): ' + str(b_intercept))

best_fit = []
for i in x_vals:
    best_fit.append(m_slope * i + b_intercept)

plt.plot(x_vals, y_vals, 'o', label='Data')
plt.plot(x_vals, best_fit, 'r-', label='Linear Regression', linewidth=3)
plt.legend(loc='upper left')
plt.show()
```

slope (m): 1\.0830263227926582
intercept (b): \-0\.3348165868955632

![linear_regression](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/linear_regression.png)

As you can see, this solution is very similar to Linear Least Squares, but this decomposition is sometimes much more efficient and numerically stable.
