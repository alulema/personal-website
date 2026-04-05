---
title: Classification Loss Functions (Part II)
description: "In my previous post, I mentioned 3 loss functions, which are mostly intended to be used in Regression models. This time, I’m going to talk about Classification Loss Functions, which are going to be us…"
publishDate: 2017-12-15
tags:
  - loss-function
coverImage: https://images.alexisalulema.com/blog/classification-loss-functions-part-ii/screen-shot-2017-12-15-at-7-49-45-pm.png
lang: en
draft: false
---

In my previous post, I mentioned 3 loss functions, which are mostly intended to be used in Regression models. This time, I’m going to talk about Classification Loss Functions, which are going to be used to evaluate loss when predicting categorical outcomes.

Let’s consider the following vector to help us to show how loss functions behave:

```
import tensorflow as tf

sess = tf.Session()

x_function = tf.linspace(-3., 5., 500)
target = tf.constant(1.)
targets = tf.fill(, 1.)
```

## Hinge Loss Function

This function is used for training classifiers, most notably for SVM (Support Vector Machine). It is defined by the following:

![Screen Shot 2017-12-15 at 7.47.13 PM](https://images.alexisalulema.com/blog/classification-loss-functions-part-ii/screen-shot-2017-12-15-at-7-47-13-pm.png)

The central idea is to compute a loss between with two target classes, 1 and \-1\.

```
hinge_loss = tf.maximum(0., 1. - tf.multiply(target, x_function))
hinge_out = sess.run(hinge_loss)
```

## Sigmoid Cross\-Entropy Loss Function

This loss function can be used in machine learning for classification and optimization, it is referred as the logistic loss function, and can be used, for example, when we are classifying between two classes 0 or 1\. TensorFlow internally performs this function, but mathematically it is defined as the following:

![Screen Shot 2017-12-15 at 7.47.46 PM](https://images.alexisalulema.com/blog/classification-loss-functions-part-ii/screen-shot-2017-12-15-at-7-47-46-pm.png)![Screen Shot 2017-12-15 at 7.48.12 PM](https://images.alexisalulema.com/blog/classification-loss-functions-part-ii/screen-shot-2017-12-15-at-7-48-12-pm.png)

```
cross_entropy_sigmoid_loss = tf.nn.sigmoid_cross_entropy_with_logits(logits=x_function, labels=targets)
cross_entropy_sigmoid_out = sess.run(cross_entropy_sigmoid_loss)
```

## Weighted Cross Entropy Loss Function

This is a weighted version of the previous loss function, as we assign a weight on the positive target. For example, we can provide a weight of 0\.5, as follows.

```
weight = tf.constant(0.5)
cross_entropy_weighted_loss = tf.nn.weighted_cross_entropy_with_logits(x_function, targets, weight)
cross_entropy_weighted_out = sess.run(cross_entropy_weighted_loss)
```

Let’s plot these loss functions!

```
import matplotlib.pyplot as plt

x_array = sess.run(x_function)
plt.plot(x_array, hinge_out, 'b-', label='Hinge Loss')
plt.plot(x_array, cross_entropy_sigmoid_out, 'k-.', label='Cross Entropy Sigmoid Loss')
plt.plot(x_array, cross_entropy_weighted_out, 'g:', label='Weighted Cross Enropy Loss (x0.5)')
plt.ylim(-1.5, 3)
plt.legend(loc='lower right', prop={'size': 11})
plt.show()
```

![Screen Shot 2017-12-15 at 7.49.45 PM](https://images.alexisalulema.com/blog/classification-loss-functions-part-ii/screen-shot-2017-12-15-at-7-49-45-pm.png)
## Conclusions

- Hinge Loss Function is great for SVM, but it is affected by outliers.
- Cross Entropy Loss is very stable on training models, but it is less robust and can be affected on big data.
