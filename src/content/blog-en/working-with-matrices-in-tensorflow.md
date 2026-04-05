---
title: Working with Matrices in TensorFlow
description: "Matrices are the basic elements we use to interchange data through computational graphs. In general terms, a tensor can de defined as a matrix, so you can refer to Declaring tensors in TensorFlow in o…"
publishDate: 2017-10-12
lang: en
draft: false
---

Matrices are the basic elements we use to interchange data through computational graphs. In general terms, a tensor can de defined as a matrix, so you can refer to Declaring tensors in TensorFlow in order to see the options you have to create matrices.

Let's define the matrices we are going to use in the examples:

```
import tensorflow as tf
import numpy as np

sess = tf.Session()

identity_matrix = tf.diag()
mat_A = tf.truncated_normal(, dtype=tf.float32)
mat_B = tf.constant(, , , , ])
mat_C = tf.random_normal(, mean=0, stddev=1.0)
mat_D = tf.convert_to_tensor(np.array(, , ]))
```

### Matrix Operations

Addition and substraction are simple operations that can be performed by '\+' and '\-' operators, or by *tf.add()* or *tf.subtract()*.

```
# A + B
>>> print(sess.run(mat_A + mat_B))
>>> print(sess.run(tf.add(mat_A, mat_B)))
 
 
 
 
 ]
```

```
# B - B
>>> print(sess.run(mat_B - mat_B))
>>> print(sess.run(tf.subtract(mat_B, mat_B)))
 
 
 
 
 ]
```

Matrices multiplication must follow the following rule:

![matmult](https://images.alexisalulema.com/blog/working-with-matrices-in-tensorflow/matmult.png)

If this rule is accomplished, then we can perform multiplication.

*tf.matmul()* performs this operation; as an option, previously we can transpose or adjointe (conjugate and transpose), and optionally we can mark any matrix as sparsed. For example:

```
# B * Identity
>>> print(sess.run(tf.matmul(mat_B, identity_matrix, transpose_a=True, transpose_b=False)))
 
 ]
```

### Other operations

```
# Transposed C
>>> print(sess.run(tf.transpose(mat_C)))
 
```

```
# Matrix Determinant D
>>> print(sess.run(tf.matrix_determinant(mat_D)))
 3.267
```

```
# Matrix Inverse D
>>> print(sess.run(tf.matrix_inverse(mat_D)))
 
 
 ]
```

```
# Cholesky decomposition
>>> print(sess.run(tf.cholesky(identity_matrix)))
 
 
 
 
 ]
```

```
# Eigen decomposition
>>> print(sess.run(tf.self_adjoint_eig(mat_D)))
 (array(), array(,
 ,
 ]))
```

### Element\-wise Operations

```
# A * B (Element-wise)
>>> print(sess.run(tf.multiply(mat_A, mat_B)))
```

```
# A % B (Element-wise)
>>> print(sess.run(tf.div(, )))
 
```

```
# A / B (Element-wise)
>>> print(sess.run(tf.truediv(, )))
 
```

```
# A / B Floor-approximation (Element-wise)
>>> print(sess.run(tf.floordiv(, )))
 
```

```
# A/B Remainder (Element-wise)
>>> print(sess.run(tf.mod(, )))
 
```

### Cross\-product

```
>>> print(sess.run(tf.cross(, )))
 array(, dtype=int32)
```

We've completed all theoretical prerequisites for TensorFlow. Once we understand matrices, variables and placeholders, we can continue with Core TensorFlow. See you next time!
