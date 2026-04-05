---
title: Linear Least Squares Regression with TensorFlow
description: "Linear Least Squares Regression is by far the most widely used regression method, and it is suitable for most cases when data behavior is linear. By definition, a line is defined by the following equa…"
publishDate: 2018-01-18
tags:
  - linear-regression
coverImage: https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/linear_regression.png
lang: en
draft: false
---

Linear Least Squares Regression is by far the most widely used regression method, and it is suitable for most cases when data behavior is linear. By definition, a line is defined by the following equation:

![LSER_01](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/lser_01.png)

For all data points (xi, yi) we have to minimize the sum of the squared errors:

![LSER_02](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/lser_02.png)

This is the equation we need to solve for all data points:

![LSER_03](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/lser_03.png)

The solution for this equation is A (I’m not going to show how this solution is found, but you can see it in [Wikipedia](https://en.wikipedia.org/wiki/Linear_least_squares_(mathematics)), and some code in several programming languages as well), which is defined by:

![LSER_04](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/lser_04.png)

Now, let’s see the implementation with TensorFlow:

```
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

sess = tf.Session()
x_vals = np.linspace(0, 10, num=100)
y_vals = x_vals + np.random.normal(loc=0, scale=1, size=100)

x_vals_column = np.transpose(np.matrix(x_vals))
ones_column = np.transpose(np.matrix(np.repeat(1, repeats=100)))
X = np.column_stack((x_vals_column, ones_column))
Y = np.transpose(np.matrix(y_vals))

X_tensor = tf.constant(X)
Y_tensor = tf.constant(Y)

tX_X = tf.matmul(tf.transpose(X_tensor), X_tensor)
tX_X_inv = tf.matrix_inverse(tX_X)
product = tf.matmul(tX_X_inv, tf.transpose(X_tensor))
A = tf.matmul(product, Y_tensor)
A_eval = sess.run(A)

m_slope = A_eval
b_intercept = A_eval
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

slope (m): 1\.0108287140073253
intercept (b): 0\.14322921334345343

![linear_regression](https://images.alexisalulema.com/blog/linear-least-squares-regression-with-tensorflow/linear_regression.png)

As you can see, the implementation is just executing basic matrix operations, the advantage of using TensorFlow in this case is that we can add this process to a more complex graph.
