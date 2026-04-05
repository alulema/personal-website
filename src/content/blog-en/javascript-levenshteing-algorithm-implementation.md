---
title: JavaScript Levenshtein Algorithm Implementation
description: "class LevenshteinModel { compute(first: string, second: string): number { if (first.length == 0) return second.length; if (second.length == 0) return first.length; let current = 1; let previous = 0; l…"
publishDate: 2021-09-08
tags:
  - javascript
  - levenshtein
lang: en
draft: false
---

```
class LevenshteinModel {

    compute(first: string, second: string): number {
        if (first.length == 0)
            return second.length;

        if (second.length == 0)
            return first.length;

        let current = 1;
        let previous = 0;
        let r: number[][] = [[], []];

        for (let i = 0; i <= second.length; i++)
            r[previous][i] = i;

        for (let i = 0; i < first.length; i++) {
            r[current][0] = i + 1;

            for (let j = 1; j <= second.length; j++) {
                const cost = (second[j - 1] === first[i]) ? 0 : 1;
                r[current][j] = Math.min(
                    r[previous][j] + 1, 
                    r[current][j - 1] + 1, 
                    r[previous][j - 1] + cost);
            }

            previous = (previous + 1) % 2; 
            current = (current + 1) % 2;
        }

        const weight = r[previous][second.length];
        return weight;
    }
}

```
