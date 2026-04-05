---
title: Understanding Variables and Placeholders in TensorFlow
description: "Usually, when we start using TensorFlow, it's very common to think that defining variables is just as trivial as a HelloWorld program, but understanding how variables (and placeholders) work under the…"
publishDate: 2017-10-11
lang: en
draft: false
---

Usually, when we start using TensorFlow, it's very common to think that defining variables is just as trivial as a HelloWorld program, but understanding how variables (and placeholders) work under the hood is very important to understand more complex concepts because those concepts heavily use variables/placeholders; and, if we don't understand the information flow between variables, it could be harder to have a clear idea of the implemented algorithms in TensorFlow.

**Variables** are the parameters of the algorithm. The main way to create a variable is by using the *Variable()* function, although, we still need to initialize it. Initializing is what puts the variable with the corresponding methods on the computational graph.

```
seq = tf.linspace(0., 7, 8)
seq_var = tf.Variable(seq)

# Initialize variables in session
sess = tf.Session()
initialize_op = tf.global_variables_initializer()
sess.run(initialize_op)
```

While each variable has an *initializer()* method, the most common way to do this is to use the function *global\_variables\_initializer()*. This function creates an operation in the graph that initializes all variables. Nevertheless, we can initialize variables depending on the results of initializing another variable, as follows:

```
sess = tf.Session()
first_var = tf.Variable(tf.lin_space(0., 7, 8), name='1st_var')
sess.run(first_var.initializer)
# first_var: <tf.Variable '1st_var:0' shape=(8,), dtype=float32_ref>

# second_var dimensions depends on first_var
second_var = tf.Variable(tf.zeros_like(first_var), name='2nd_var')
sess.run(second_var.initializer)
# second_var: <tf.Variable '2nd_var:0' shape=(8,), dtype=float32_ref>
```

**Placeholders** are just holding the position for data to be fed into the graph. To put a placeholder in the graph, we must perform at least one operation on the placeholder.

```
sess = tf.Session()
x = tf.placeholder(tf.float32, shape=)
# y is the operation to run on x placeholder
y = tf.identity(x)

# x_vals is data to feed into the x placeholder
x_vals = np.random.rand(2, 2)
# Runs y operation
sess.run(y, feed_dict={x: x_vals})
```

TensorFlow will not return a self\-referenced placeholder in the feed dictionary.

With these concepts clear, we can move forward with TensorFlow. See you next time with more TF!
