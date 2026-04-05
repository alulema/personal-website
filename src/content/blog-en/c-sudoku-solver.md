---
title: "C# Sudoku Solver"
description: "(GitHub Repo: https://github.com/alulema/SudokuSolverNet) I was revisiting a couple of basic AI concepts: Depth First Search and Constraint Propagation, and I found a very good explanation by Professo…"
publishDate: 2018-04-19
tags:
  - c#
coverImage: https://images.alexisalulema.com/blog/c-sudoku-solver/tree.png
lang: en
draft: false
---

(GitHub Repo: https://github.com/alulema/SudokuSolverNet)

I was revisiting a couple of basic AI concepts:  Depth First Search and Constraint Propagation, and I found a very good explanation by Professor Peter Norvig ([Solving Every Sudoku Puzzle](http://Peter Norvig)), I just want to add a couple of simple explanations for a better understanding of the concepts.
# Constraint Propagation

This technique is used to reduce the search space and make the problem easier to solve. In Sudoku domain, it means following the game rules and define the possible solutions to assign to each box in the table.
## Elimination Strategy.

The idea is to reduce the possible values to be assigned to a box. Just let me redefine the concepts for a better understanding.
### *Box.*

![box](https://images.alexisalulema.com/blog/c-sudoku-solver/box.png)

We have 81 boxes in the puzzle
### *Unit.*

 

Each box will be into 3 different units, each unit contains 9 boxes, each of them have different values, from 1 to 9\.
### *Peer.*

![peer](https://images.alexisalulema.com/blog/c-sudoku-solver/peer.png)

Each peer contains 21 boxes, and the box's value cannot be in any other element of this peer.

Considering this 3 concepts, the puzzle should be seen in this way:

![puzzle](https://images.alexisalulema.com/blog/c-sudoku-solver/puzzle.png)
## One\-Choice Strategy.

This strategy consists in seen the only choice to be accepted by a box in a unit. This helps to reduce the options in Elimination.

In the following image, we can see that number 4 can be assigned to only one cell.

![only-choice](https://images.alexisalulema.com/blog/c-sudoku-solver/only-choice.png)
# First Depth Search

This strategy will be applied after Constraint\-Propagation, and considering it didn't find a solution. It will be more CPU demanding, but it is the actually a basic approach; it doesn't prune any options at all. The only check it makes is that all the assigned values so far are consistent with each other.

This strategy can be described as a tree, where we try possible solutions by assigning the possible options to a box and checking one by one if it solves the puzzle re\-applying Constraint\-Propagation again with this testing value.

![tree](https://images.alexisalulema.com/blog/c-sudoku-solver/tree.png)

By using First Depth Search, this tree is navigated in the following order:
A\-B\-D\-E\-I\-J\-C\-F\-G\-H\-K\-L

You can think each leaf of this tree as:
*"Will it solve the puzzle?"*

In sudoku, we are going to start with the box with less options to be solved.

![depthfirstsearch](https://images.alexisalulema.com/blog/c-sudoku-solver/depthfirstsearch.png)

For example, in this unit, we can start with box with 56 as the probable choices, then we try to solve the puzzle with 5, if it is not solved we try with 6, and so on.
# C\# Solution

Professor Norvig implements the algoritms in Python, I've done this in C\# as I consider C\# is a little bit more clear than Python to understand how it works (it is just my opinion, maybe you find Python more clear).

```
class Program
{
    private static string[] _boxes;
    private static string _cols;
    private static string _rows;
    private static SortedList<string, string[]> _peers;
    private static List<string[]> _unitList;

    public static void Main(string[] args)
    {
        _cols = "123456789";
        _rows = "ABCDEFGHI";
        _boxes = Cross(_rows, _cols);

        var rowUnits = new List<string[]>();
        foreach (var c in _cols)
            rowUnits.Add(Cross(_rows, c.ToString()));

        var colUnits = new List<string[]>();
        foreach (var r in _rows)
            colUnits.Add(Cross(r.ToString(), _cols));

        var squareUnits = new List<string[]>();
        foreach (var rs in new[] { "ABC", "DEF", "GHI" })
            squareUnits.AddRange(new[] { "123", "456", "789" }.Select(cs => Cross(rs, cs)));

        _unitList = new List<string[]>();
        _unitList.AddRange(rowUnits);
        _unitList.AddRange(colUnits);
        _unitList.AddRange(squareUnits);

        var units = new SortedList<string, string[][]>();
        foreach (var s in _boxes)
            units.Add(s, _unitList.Where(x => x.Contains(s)).ToArray());

        _peers = new SortedList<string, string[]>();
        foreach (var s in _boxes)
        {
            var peer = new List();
            foreach (var row in units)
            {
                var elemStrings = row.Where(x => x != s).ToArray();
                foreach (var elem in elemStrings)
                {
                    if (!peer.Contains(elem))
                        peer.Add(elem);
                }
            }

            _peers.Add(s, peer.ToArray());
        }

        var hardPuzzle = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......";
        var puzzle = ".....97..4..1..3.8.1...89....9..42...8.23.179..26.7.833..7.16.......2...97..5..12";

        Console.WriteLine("**** SOLVING SIMPLE PUZZLE *****");
        Display(Eliminate(GridValuesExtended(puzzle)));
        var start = DateTime.Now;
        Search(GridValuesExtended(puzzle));
        var end = DateTime.Now;
        Console.WriteLine($"It took {end.Subtract(start).Seconds}.{end.Subtract(start).Milliseconds} seconds");

        Console.WriteLine("**** SOLVING HARD PUZZLE *****");
        Display(Eliminate(GridValuesExtended(hardPuzzle)));
        start = DateTime.Now;
        Search(GridValuesExtended(hardPuzzle));
        end = DateTime.Now;
        Console.WriteLine($"It took {end.Subtract(start).Seconds}.{end.Subtract(start).Milliseconds} seconds\n");
        Console.Read();
    }

    private static string[] Cross(string a, string b)
    {
        var results = new List();

        foreach (var charA in a)
            foreach (var charB in b)
                results.Add(charA + "" + charB);

        return results.ToArray();
    }

    private static SortedList<string, string> GridValues(string grid)
    {
        if (grid.Length != 81) return null;

        var dict = new SortedList<string, string>();
        foreach (var item in _boxes.Zip(grid.ToCharArray(), (a, b) => new { Box = a, Grid = b }))
            dict.Add(item.Box, item.Grid.ToString());

        return dict;
    }

    private static void Display(SortedList<string, string> values)
    {
        var width = 1 + (_boxes.Select(s => values.Length)).Max();
        var line = string.Join("+", Enumerable.Repeat(string.Join("", Enumerable.Repeat("-", width * 3)), 3));

        foreach (var row in _rows)
        {
            string gridLine = "";
            foreach (var col in _cols)
                gridLine += (values).CenterString(width) + (col == '3' || col == '6' ? "|" : "");

            Console.WriteLine(gridLine);

            if (row == 'C' || row == 'F')
                Console.WriteLine(line);
        }

        Console.WriteLine(line);
    }

    private static SortedList<string, string> GridValuesExtended(string grid)
    {
        var values = new List();
        string alldigits = "123456789";

        foreach (var c in grid)
        {
            if (c == '.')
                values.Add(alldigits);
            else if (alldigits.Contains(c))
                values.Add("" + c);
        }

        if (grid.Length != 81) return null;

        var dict = new SortedList<string, string>();
        foreach (var item in _boxes.Zip(values, (a, b) => new { Box = a, Grid = b }))
            dict.Add(item.Box, item.Grid);

        return dict;
    }

    private static SortedList<string, string> Eliminate(SortedList<string, string> values)
    {
        var solvedValues = values.Keys.Where(box => values.Length == 1).ToList();

        foreach (var box in solvedValues)
        {
            var digit = values;
            foreach (var peer in _peers)
            {
                if (digit != "")
                    values = values.Replace(digit, "");
            }
        }

        return values;
    }

    private static SortedList<string, string> OnlyChoice(SortedList<string, string> values)
    {
        foreach (var unit in _unitList)
        {
            foreach (var digit in "123456789")
            {
                var dplaces = unit.Where(box => values.Contains(digit)).ToList();

                if (dplaces.Count == 1)
                    values] = digit.ToString();
            }
        }

        return values;
    }

    private static SortedList<string, string> ReducePuzzle(SortedList<string, string> values)
    {
        var stalled = false;

        while (!stalled)
        {
            var solvedValuesBefore = values.Keys.Count(box => values.Length == 1);

            if (!values.Values.Any(x => x.Length > 1))
            {
                stalled = true;
                continue;
            }

            values = Eliminate(values);
            Display(values);
            Console.WriteLine();

            if (!values.Values.Any(x => x.Length > 1))
            {
                stalled = true;
                continue;
            }

            values = OnlyChoice(values);
            Display(values);
            Console.WriteLine();

            var solvedValuesAfter = values.Keys.Count(box => values.Length == 1);

            stalled = solvedValuesBefore == solvedValuesAfter;

            if (values.Keys.Count(box => values.Length == 0) > 0)
                return null;
        }

        return values;
    }

    private static SortedList<string, string> Search(SortedList<string, string> values)
    {
        values = ReducePuzzle(values);

        if (values == null)
            return null;

        if (_boxes.Select(s => values.Length == 1).All(x => x))
            return values; // solved

        var pairs = new SortedList<string, int>();
        foreach (var s in _boxes)
        {
            if (values.Length > 1)
                pairs.Add(s, values.Length);
        }

        string boxWithMinLength = null;
        int minLength = 0;
        foreach (var pair in pairs)
        {
            if (boxWithMinLength == null)
            {
                boxWithMinLength = pair.Key;
                minLength = pair.Value;
            }
            else
            {
                if (pair.Value < minLength)
                {
                    boxWithMinLength = pair.Key;
                    minLength = pair.Value;
                }
            }
        }

        foreach (var value in values)
        {
            var newSudoku = new SortedList<string, string>();

            foreach (var x in values)
                newSudoku.Add(x.Key, x.Value);

            newSudoku = "" + value;
            var attempt = Search(newSudoku);

            if (attempt != null)
                return attempt;
        }

        return null;
    }
}

```

```
public static class LocalExtensions
{
    public static string CenterString(this string stringToCenter, int totalLength)
    {
        return stringToCenter.PadLeft(((totalLength - stringToCenter.Length) / 2)
                                      + stringToCenter.Length)
            .PadRight(totalLength);
    }
}

```
