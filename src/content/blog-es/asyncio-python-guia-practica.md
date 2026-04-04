---
title: Asyncio en Python — Guía Práctica
description: Una inmersión profunda en la librería asyncio de Python, cubriendo corutinas, event loops, tasks y patrones del mundo real para aplicaciones de alto rendimiento.
publishDate: 2024-03-15
tags:
  - python
  - asyncio
  - performance
  - backend
lang: es
draft: false
---

## Por qué importa la programación asíncrona

Las aplicaciones modernas pasan la mayor parte del tiempo *esperando* — bases de datos, APIs externas, I/O de archivos. El código síncrono tradicional bloquea el hilo completo durante estas esperas. Asyncio permite hacer trabajo útil mientras se espera.

## Coroutinas vs Hilos

Una coroutina es una función que puede pausar y reanudar su ejecución. A diferencia de los hilos, las coroutinas se programan cooperativamente — ceden el control explícitamente, lo que significa sin condiciones de carrera y mínimo overhead.

```python
import asyncio

async def obtener_datos(url: str) -> dict:
    # Simula una llamada HTTP asíncrona
    await asyncio.sleep(1)
    return {"url": url, "datos": "..."}
```

## Ejecutar Coroutinas Concurrentemente

El verdadero poder viene de ejecutar múltiples coroutinas a la vez:

```python
async def main():
    tasks = [
        obtener_datos("https://api.ejemplo.com/usuarios"),
        obtener_datos("https://api.ejemplo.com/posts"),
        obtener_datos("https://api.ejemplo.com/comentarios"),
    ]
    resultados = await asyncio.gather(*tasks)
    return resultados

asyncio.run(main())
```

Esto ejecuta las tres solicitudes concurrentemente, reduciendo el tiempo total de 3s a ~1s.

## Integración con FastAPI

FastAPI está construido sobre asyncio. Cualquier ruta definida con `async def` se beneficia automáticamente:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/usuarios/{user_id}")
async def obtener_usuario(user_id: int):
    usuario = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    return usuario
```

## Conclusión

Asyncio no es siempre la herramienta correcta — las tareas intensivas en CPU aún necesitan hilos o multiprocesamiento. Pero para cargas de trabajo intensivas en I/O, ofrece mejoras significativas de rendimiento con código limpio y legible.
