---
title: "Cross-Platform Communications: gRPC Server and Client: .NET Core"
description: "When we are developing web solutions consisting of several projects, it is very common communicate between each other, and the common solutions are proprietary solutions (like .NET Remoting), or stand…"
publishDate: 2017-03-10
tags:
  - .net-core
  - c#
  - vscode
lang: en
draft: false
---

When we are developing web solutions consisting of several projects, it is very common communicate between each other, and the common solutions are proprietary solutions (like .NET Remoting), or standard solutions like REST or SOAP. Recently, I discovered gRPC as the Google solution for Cross\-Platform communications, allowing the developers to communicate applications. The advantage of gRPC is that it doesn't use message formats which need to assemble JSON or XML (and it makes a bigger message, sometimes). Instead of this, gRPC uses Protocol Buffers to define binary messages to be interchanged between the parts.

At this time, I start with .NET Core, and you can see the details for creating server and client:

GitHub Repository: https://github.com/alexis\-dotnet/Dotnet.Grpc

protoc command: protoc \-I\=pb \-\-csharp\_out\=Messages pb/messages.proto \-\-grpc\_out\=Messages \-\-plugin\=protoc\-gen\-grpc\=/Users/\_your username\_/.nuget/packages/Grpc.Tools/1\.1\.0/tools/macosx\_x64/grpc\_csharp\_plugin
chmod 755 generateCerts.sh

Links:
gRPC: http://www.grpc.io/
Protocol Buffers: https://developers.google.com/protocol\-buffers/
SSH Keys Generation: http://stackoverflow.com/a/37739265

https://youtu.be/s374fFZuZbo
