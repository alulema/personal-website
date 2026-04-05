---
title: Declaring tensors in TensorFlow
description: "[Requirement: Tensorflow and NumPy installed on Python +3.5] [Requirement: import tensorflow as tf] [Requirement: import numpy as np] Tensors are the primary data structure we use in TensorFlow, and, …"
publishDate: 2017-10-10
lang: en
draft: false
---

Tensors are the primary data structure we use in TensorFlow, and, as Wikipedia describes them, "tensors are geometric objects that describe linear relations between geometric vectors, scalars and other tensors". Tensors can be described as multidimensional arrays, embracing the concepts of scalar, vector and matrix, without taking in consideration the coordinate system

The tensor order is the number of indexes we need to specify one element; so, an scalar will be an order 0 tensor, a vector will be an order 1 tensor, a matriz an order 2 tensor, and so on.
![Order.3.Tensor](https://images.alexisalulema.com/blog/declaring-tensors-in-tensorflow/order-3-tensor.png)
Fig 1\. Order 3 Tensor

Now we know what a tensor is, I'm going to show you how we can declare tensors in TensorFlow.
### 1\. Fixed tensors

```
>>> zeros_tsr = tf.zeros(, dtype=tf.int32, name='zeros5x5')
>>> print(zeros_tsr)
Tensor("zeros5x5:0", shape=(5, 5), dtype=int32)
>>> tf.InteractiveSession().run(zeros_tsr)
array(,
       ,
       ,
       ,
       ])
```

```
>>> ones_tsr = tf.ones(, dtype=tf.float32, name='ones5x5')
>>> print(ones_tsr)
Tensor("ones5x5:0", shape=(5, 5), dtype=float32)
>>> tf.InteractiveSession().run(ones_tsr)
array(,
       ,
       ,
       ,
       ], dtype=float32)
```

```
>>> filled_tsr = tf.fill(, 123, name='filled123')
>>> print(filled_tsr)
Tensor("filled123:0", shape=(5, 5), dtype=int32)
>>> tf.InteractiveSession().run(filled_tsr)
array(,
      ,
      ,
      ,
      ])
```

```
>>> filled2_tsr = tf.constant(123, shape=, name='filled123_2', dtype=tf.int16)
>>> print(filled2_tsr)
Tensor("filled123_2:0", shape=(5, 5), dtype=int16)
>>> tf.InteractiveSession().run(filled2_tsr)
array(,
       ,
       ,
       ,
       ], dtype=int16)
```

```
>>> constant_tsr = tf.constant(, name='vector')
>>> print(constant_tsr)
Tensor("vector:0", shape=(3,), dtype=int32)
>>> tf.InteractiveSession().run(constant_tsr)
array()
```

### 2\. Copying dimensions

It is necessary to previously define tensors from which we are going to copy dimensions.

```
>>> zeros_similar = tf.zeros_like(constant_tsr)
>>> print(zeros_similar)
Tensor("zeros_like:0", shape=(3,), dtype=int32)
>>> tf.InteractiveSession().run(zeros_similar)
array()
```

```
>>> ones_similar = tf.ones_like(constant_tsr)
>>> print(ones_similar)
Tensor("ones_like:0", shape=(3,), dtype=int32)
>>> tf.InteractiveSession().run(ones_similar)
array()
```

### 3\. Sequence tensors

```
# This tensor defines 7 regular intervals between 0 and 2, 1st param should be float32/64
>>> linear_tsr = tf.linspace(0., 2, 7)
>>> print(linear_tsr)
Tensor("LinSpace_5:0", shape=(7,), dtype=float32)
>>> tf.InteractiveSession().run(linear_tsr)
array(, dtype=float32)
```

```
# This tensor defines 4 elements between 6 and 17, with a delta of 3
>>> int_seq_tsr = tf.range(start=6, limit=17, delta=3)
>>> print(int_seq_tsr)
Tensor("range_1:0", shape=(4,), dtype=int32)
>>> tf.InteractiveSession().run(int_seq_tsr)
array()
```

### 4\. Random tensors

```
# Random numbers from uniform distribution
>>> rand_unif_tsr = tf.random_uniform(, minval=0, maxval=1)
>>> print(rand_unif_tsr)
Tensor("random_uniform:0", shape=(5, 5), dtype=float32)
>>> tf.InteractiveSession().run(rand_unif_tsr)
array(,
       ,
       ,
       ,
       ], dtype=float32)
```

```
# Random numbers from normal distribution
>>> rand_normal_tsr = tf.random_normal(, mean=0.0, stddev=1.0)
>>> print(rand_normal_tsr)
Tensor("random_normal:0", shape=(5, 5), dtype=float32)
>>> tf.InteractiveSession().run(rand_normal_tsr)
array(,
       ,
       ,
       ,
       ], dtype=float32)
```

```
# Random numbers from normal distribution, limitating values within 2 SD from mean
>>> trunc_norm_tsr = tf.truncated_normal(, mean=0.0, stddev=1.0)
>>> print(trunc_norm_tsr)
Tensor("truncated_normal:0", shape=(5, 5), dtype=float32)
>>> tf.InteractiveSession().run(trunc_norm_tsr)
array(,
       ,
       ,
       ,
       ], dtype=float32)
```

```
# Shuffles existing tensor
>>> seq = tf.linspace(0., 7, 8)
>>> tf.InteractiveSession().run(seq)
array(, dtype=float32)
>>> tf.InteractiveSession().run(tf.random_shuffle(seq))
array(, dtype=float32)
```

```
# Randomicaly crops existing tensor to specified dimension
>>> tf.InteractiveSession().run(tf.random_crop(seq, ))
array(, dtype=float32)
```

### 5\. Converted from NumPy

```
>>> np_array = np.array(, ])
>>> np_tsr = tf.convert_to_tensor(np_array, dtype=tf.int32)
>>> print(np_tsr)
Tensor("Const:0", shape=(2, 2), dtype=int32)
>>> tf.InteractiveSession().run(np_tsr)
array(,
       ])
```

Once you have created your desired tensor, you should wrap it as a TensorFlow Variable, like this:

```
seq_var = tf.Variable(seq)
```

That's all for today. See you next time with more TensorFlow!
