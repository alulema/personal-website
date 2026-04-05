---
title: Java Streams API in brief
description: "First, let’s define what a stream is in Java 8: a sequence of functions, actions, inputs, and outputs (better defined as a “pipeline”). Streams API provides functional-style operations to transform th…"
publishDate: 2017-07-20
tags:
  - data-science
  - java
  - streams-api
lang: en
draft: false
---

First, let’s define what a stream is in Java 8: a sequence of functions, actions, inputs, and outputs (better defined as a “pipeline”). Streams API provides functional\-style operations to transform these sequences; sources for them can contain arrays, collections, files, etc. In general terms, streams are [Monads](https://en.wikipedia.org/wiki/Monad_(functional_programming)):

*"Monads represent computations to be executed in a sequential (or parallel, in Java Streams) structure."*

Streams API is a great starting point for data preparation, and, if we compare it with its Python equivalents, Java provides us a very strong alternative for Data Science, as follows:
- As a typed\-language, the compiler can detect error and bugs.
- Java bytecode is faster than scripting languages as R or Python
- Versions of libraries in projects can be easily maintained with Maven or Gradle
- Common big data frameworks such as Apache Hadoop or Spark are written in Java or JVM languages.
- Creating models in Java makes easier to integrate them to production systems, which usually are written in Java or similar languages.

Let’s start some examples defining a simple Car class:

```
class Car {
     private final String name;
     private final Country origin;
 
     Car(String name, Country origin) {
         this.name = name;
         this.origin = origin;
     }
 
     public String getName() { return name; }
     public Country getOrigin() { return origin; }
 }
 
 final class Country {
     private final int value;
     private final String name;
 
     public static Country GERMANY = new Country(1, "GERMANY");
     public static Country US = new Country(2, "US");
     public static Country UK = new Country(3, "UK");
     public static Country INDIA = new Country(4, "INDIA");
     public static Country JAPAN = new Country(5, "JAPAN");
 
     private Country(int value, String name) {
         this.value = value;
         this.name = name;
     }
 
     public int getValue() { return value; }
     public String getName() { return name; }
 }
```

Streams API usually works with collections, so a useful method to convert an array into a collection is ***Arrays.stream***:

```
Car[] cars = {
        new Car("GM", Country.US),
        new Car("Cadillac", Country.US),
        new Car("BMW", Country.GERMANY),
        new Car("Mercedes Benz", Country.GERMANY),
        new Car("Toyota", Country.JAPAN),
        new Car("Mazda", Country.JAPAN),
        new Car("Honda", Country.JAPAN),
        new Car("Mahindra", Country.INDIA),
        new Car("Land Rover", Country.UK)
};

List<Car> list = Arrays.asList(cars);
Stream<Car> stream = list.stream();
```

***Streams are not reusable***, so they have to be recreated in order to start a new processing pipeline, because of this I’m going to be using ***list.stream()*** in all the examples as follows:

```
List<String> germanCars = list.stream()
        .filter(x -> x.getOrigin().equals(Country.GERMANY))
        .map(Car::getName)
        .collect(Collectors.toList());
```

This piece of code shows some useful Stream functions:
### 1\. Filtering.

It directly works on the stream, and receives a lambda function to evaluate the filter, it returns a filtered Stream
### 2\. Mapping

It provides a useful way of selecting a specific data member of Car class, and “maps” the stream of Cars into a stream of Strings.
### 3\. Collecting

It performs a data transformation into lists, sets, strings, etc, using Collectors class, which provides useful transformation methods, just like Collectors.toList()

```
Three more examples:
String rawSentence = list.stream()
        .map(Car::getName)
        .collect(Collectors.joining(","));
```

```
Set<String> countries = list.stream()
        .map(Car::getOrigin)
        .map(Country::getName)
        .collect(Collectors.toSet());
```

```
Map<Country, List<Car>> groupByCountry = list.stream()
        .collect(Collectors.groupingBy(Car::getOrigin));
System.out.println(groupByCountry.get(Country.JAPAN).stream()
        .map(Car::getName)
        .collect(Collectors.toList()));
```

In this last two examples, we can see that we can operate on a stream over and over again, and it creates the “pipelines” we mentioned before.

There is a useful ***toMap()*** collector that can index a collection using some fields. For example, if we want to get a map from Car names to Car objects, it can be achieved using the following code:

```
Map<String, Car> tokenToWord = list.stream()
        .collect(Collectors.toMap(Car::getName, Function.identity()));
```

Streams API provides streams of primitives (ints, doubles, and others), they have basic statistical methods such as ***sum***, ***max***, ***min***, ***average***, or ***summaryStatistics***. For example:

```
int maxNameLength = list.stream()
        .mapToInt(x -> x.getName().length())
        .max().getAsInt();
```

#### *Custom Collectors*

We can also define our own collector by using ***Collector*** class which requires to pass a supplir class, accumulator, combiner and finisher method, for example:

```
Collector<Car, StringJoiner, String> carsCollector =
     Collector.of(
         () -> new StringJoiner(", "),
         (joiner, car) -> joiner.add(car.getName().toUpperCase()),
         StringJoiner::merge,
         StringJoiner::toString);
 
 String names = list.stream().collect(carsCollector);
```

### 4\. Parallelizing

Streams can be execute in parallel taking advantage of the available physical CPU cores. Streams use a common ForkJoinPool, we can check the size of the underlying thread\-pool by using ForkJoinPool.commonPool (7 threads in my PC). For example:

```
ForkJoinPool commonPool = ForkJoinPool.commonPool();
 System.out.println("Threads: " + commonPool.getParallelism());
 int[] firstLengths = list.parallelStream()
         .filter(w -> w.getOrigin().equals(Country.JAPAN))
         .map(Car::getName)
         .mapToInt(String::length)
         .sequential()
         .sorted()
         .limit(2)
         .toArray();
 System.out.println(Arrays.toString(firstLengths));
```

### 5\. I/O

Finally, we can use Java I/O library, for example, using files to be represented as a stream of lines using ***Reader.lines()*** method.

```
InputStream fStream = Main.class.getResourceAsStream("text.txt");
 InputStreamReader fReader = new InputStreamReader(fStream, StandardCharsets.UTF_8);
 
 try (Stream<String> lines = new BufferedReader(fReader).lines()) {
     double average = lines
             .flatMap(line -> Arrays.stream(line.split(" ")))
             .map(String::toLowerCase)
             .mapToInt(String::length)
             .average().getAsDouble();
     System.out.println("average token length: " + average);
 }
```

### Conclusion

Streams are a very powerful feature introduced in Java 8 (and to be extended soon in Java 9\), very useful to process data for Data Science in Java. There are much more useful methods in Streams, which  More examples in the future.

Go to GitHub Repo: <https://github.com/alulema/JavaDS.01>
