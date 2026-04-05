---
title: Activation Functions in TensorFlow
description: "Perceptron is a simple algorithm which, given an input vector x of m values (x1, x2, ..., xm), outputs either 1 (ON) or 0 (OFF), and we define its function as follows: Here, ω is a vector of weights, …"
publishDate: 2017-10-15
coverImage: https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/sigmoid.png
lang: en
draft: false
---

Perceptron is a simple algorithm which, given an input vector x of m values (x1, x2, ..., xm), outputs either 1 (ON) or 0 (OFF), and we define its function as follows:

![perceptron.equation](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/perceptron-equation.png)
![dot.product](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/dot-product.png)

Here, ω is a vector of weights, ωx is the dot product, and b is the bias. This equation reassembles the equation for a straight line. If x lies above this line, then the answer is positive, otherwise it is negative. However, ideally we are going to pass training data and let the computer to adjust weight and bias in such a way that the errors produced by this neuron will be minimized. The learning process should be able to recognize small changes that progressively teach our neuron to classify the information as we want. In the following image we don't have "small changes" but a big change, and the neuron is not able to learn in this way because ω and bias will not converge into the optimal values to minimize errors.

![perceptron](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/perceptron.png)

Tangent to this function indicates that our neuron is learning; and, as we deduct from this, the tangent in x\=0 is INFINITE. This is not possible in real scenarios because in real life all we learn step\-by\-step. In order to make our neuron learn, we need something to progressively change from 0 to 1: a continuous (and derivative) function.
When we start using neural networks we use activation functions as an essential part of a neuron. This activation function will allow us to adjust weights and bias.

In TensorFlow, we can find the activation functions in the neural network (nn) library.
## Activation Functions

### Sigmoid

![sigmoid.equation](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/sigmoid-equation.png)
![sigmoid](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/sigmoid.png)

Mathematically, the function is continuous. As we can see, the sigmoid has a behavior similar to perceptron, but the changes are gradual and we can have output values different than 0 or 1\.

Example:

```
>>> import tensorflow as tf
>>> sess = tf.Session()
>>> x = tf.lin_space(-3., 3., 24)
>>> print(sess.run(tf.nn.sigmoid(x)))
 
```

The sigmoid function is the most common activation function; however, this is not often used because of the tendency to 0\-out the backpropagation terms during training.
### ReLU (Rectified Linuear Unit)

![relu.equation](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/relu-equation.png)
![relu](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/relu.png)

This function has become very popular because it generates very good experimental results. The best advantage of ReLUs is that this function accelerates the convergence of SGD (stochastic gradient descent, which indicates how fast our neuron is learning), compared to Sigmoid and tanh functions.

This strength is, at the same way, the main weakness because this "learning speed" can make the neuron's weights to be updated and oscillating from the optimal values and never activate on any point. For example, if the learning rate is too high, the half of neurons can be "dead", but if we set a proper value then our networks will learn, but this will be slower than we expect.

Example:

```
>>> import tensorflow as tf
>>> sess = tf.Session()
>>> x = tf.lin_space(-3., 3., 24)
>>> print(sess.run(tf.nn.relu(x)))
 
```

### ReLU6

![relu6.equation](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/relu6-equation.png)
![relu6](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/relu6.png)

It seems this function was introduced in "[Convolutional Deep Belief Networks on CIFAR\-10](http://www.cs.utoronto.ca/~kriz/conv-cifar10-aug2010.pdf)" (page 2\). Its main advantage, compared to simple ReLU, is that it is computationally faster and does not suffer from vanishing (infinitesimally near zero) or exploding values. As you can be figuring out, it will be used in Convolutional Neural Networks and Recurrent Neural Networks.

Example:

```
>>> import tensorflow as tf
>>> sess = tf.Session()
>>> x = tf.lin_space(-3., 9., 24)
>>> print(sess.run(tf.nn.relu6(x)))
 
```

### Hyperbolic Tangent

![tanh](https://images.alexisalulema.com/blog/activation-functions-in-tensorflow/tanh.png)

This function is very similar to sigmoid, except that instead of having a range between 0 and 1, it has a range between \-1 and 1\. Sadly, it has the same vanishing problem than Sigmoid.

Example:

```
>>> import tensorflow as tf
>>> sess = tf.Session()
>>> x = tf.lin_space(-5., 5., 24)
>>> print(sess.run(tf.nn.tanh(x)))
 
```

## Conclusion

These activation functions help us to introduce nonlinearities in neural networks; if its range is between 0 and 1 (sigmoid), then the graph can only output values between 0 and 1\.

We have some other activation functions implemented by TensorFlow, like softsign, softplus, ELU, cReLU, but most of them are not so frequently used, and the ithers are variations to the already explained functions. With the exception of dropout (which is not precisely an activation function but it will be heavily used in backpropagation, and I will explain it later), we have covered all stuff for this topic in TensorFlow. See you next time!
