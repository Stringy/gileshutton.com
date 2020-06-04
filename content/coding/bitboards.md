---
title: "bitboards"
date: 2020-05-31
draft: true
tags: ["coding", "chess", "bitboards"]
categories: ["code"]
summary: ""
---

How 64 bits can significantly improve engine performance.

<!--more-->

Bitboards[^1]. Magical, wonderful bitboards. When I came across this technique whilst developing my first 
Chess engine I was blown away by the simplicity of it. There have been a few times in my career where I've 
looked at someone's solution to a problem and thought "Of course, that's such an obvious solution," and 
bitboards are one of those.

What is a bitboard? I hear you cry. Simply put, it is the use of a 64 bit integer to hold the state of a 
Chess board. 64 squares on the board match up to the 64 bits of the integer. Simple.

Each integer represents a single board position for specific type or types of piece. You could have a single 
bitboard representing all of the white pawns and another representing all moves that black rooks can currently 
make, for example.

The real "aha!" moment comes when you consider how you can operate on those bitboards to perform move generation 
or board evaluation. Say we have a white bishop on D4 and wish to calculate all black pieces attacked by that 
bishop. The naive approach, using some sort of board array would have you iterating over the squares on the 
board and seeing if that piece is attacked from a bishop on D4 (probably quite an expensive calculation in itself.)
and constructing individual move objects based on that calculation.

Instead, with bitboards, you simply XOR the integer that represents the attacks the white bishop can make with the 
integer that represents all the black pieces:

```
white bishop        Black Pieces        Attacked Black
attacks from D4                         pieces

0 0 0 0 0 0 0 0     1 1 1 1 1 1 1 1     0 0 0 0 0 0 0 0
1 0 0 0 0 0 1 0     1 0 0 1 1 0 1 1     0 0 0 0 0 0 0 0
0 1 0 0 0 1 0 0     0 1 0 0 0 1 0 0     0 1 0 0 0 1 0 0
0 0 1 0 1 0 0 0  ^  0 0 0 0 0 0 0 0  =  0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0     0 0 0 0 0 0 0 0     0 0 0 0 0 0 0 0
0 0 1 0 1 0 0 0     0 0 0 0 0 0 0 0     0 0 0 0 0 0 0 0
0 1 0 0 0 1 0 0     0 0 0 0 0 0 0 0     0 0 0 0 0 0 0 0
1 0 0 0 0 0 1 0     0 0 0 0 0 0 0 0     0 0 0 0 0 0 0 0
```

A single operation (and indeed a single amd64 instruction) can perform an incredible amount of work. 
I know what you're thinking now: surely this depends on a lot of work before hand to calculate masks 
for attacks and general movement? You're absolutely right. Most of this can be pregenerated though, 
and the simplicity of the bitboard operations still saves us time during move generation.

Take the white pawns as an example. We have a bitboard that contains all the white pawns in their starting position:

```
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
1 1 1 1 1 1 1 1
0 0 0 0 0 0 0 0
```

We have masks for the moves that they can make in each of those positions, but we need to somehow iterate 
over all of those board positions to get the masks. Once we have them all we can simply OR them together to 
get a bitboard that contains all the moves that the white pawns can make. Here's some python pseudocode:

```py
def get_white_pawn_moves(white_pawns):
    moves = 0
    for pawn in white_pawns:
        moves |= white_pawn_masks[board_index_of(pawn)]
    return moves
```

The crux of this method is that for loop - how do we iterate over a 64 bit integer? Well, in most languages you can't 
but what we can do is get the least significant bit of the bitboard and use that. By continually getting the LSB, 
processing that piece, and then turning that bit off, we can effectively iterate over a bitboard. 
Here's the pseudocode for the LSB use:

```py
def get_white_pawn_moves(white_pawns):
    moves = 0
    while white_pawns != 0:
        pawn = get_lsb(white_pawns)
        moves |= white_pawn_masks[board_index_of(pawn)]
        white_pawns ^= pawn
    return moves
```

This process is the same for all the non-sliding pieces; iterate over the board position, look up the square in a 
table and OR that mask with the current set of moves. Very simple, and very very quick. 

Since I've been writing my new chess engine in Rust, I have tried to take advantage of some of the high-level, zero-cost
abstractions that Rust provides. To solve the interger iteration problem, I have been able to implement the Iterator trait
for my bitboard type[^2]:

```rust
pub struct bitboard(u64);

impl bitboard {
    pub fn iter(&self) -> bitboardIter {
        bitboardIter(self, bitboard(0))
    }
}

pub struct bitboardIter<'a>(&'a bitboard, bitboard);

impl Iterator for BItboardIter<'_> {
    type Item = usize;

    fn next(&mut self) -> Option<Self::Item> {
        // copy of self.0 with bits that haven't been processed yet
        let tmp = *self.0 ^ self.1;
        if tmp != 0.into() {
            // get the next bit to process
            let lsb = tmp.lsb();

            // set that bit within the stored state
            self.1 ^= BIT_TABLE[lsb];
            Some(lsb)
        } else {
            None
        }
    }
}
```

The iterator contains a reference to a bitboard (the one we want to iterate over) and a separate bitboard to store
the already-processed bits. The advantage to doing this is not immediately obvious from the example pseudocode above,
but by creating an iterator we then open ourselves up to a wealth of extremely useful Iterator abstractions that can
be used during move generation. Not only can we iterate over all of the pieces on the board we can also iterate over
the bitboard that represents all their moves which means that construction of move structs is similarly speedy!
 
Having said all this, I haven't looked at the generated assembly to see just how zero-cost this abstraction is, 
but from my benchmarks it doesn't look like performance is particularly hampered. The ease of use is important and 
it can make the code far simpler to reason about.

Mask generation is the important part of bitboard usage. It _is_ computationally expensive, but it can all be performed
either before-hand (as in my Rust engine, where I've pregenerated everything and I'm linking them directly into the library)
or during engine initialisation (as in my Go engine.) Either method is similarly effective because ultimately the performance saving
you make during move generation and board evaluation is so significant, it massively out-weighs the downsides of having
to generate all those masks.

Next time, I'm going to talk about how this works with sliding pieces, where you need to work out when to stop sliding.
This is where the real magic happens, and I really do mean magic!

[^1]: https://www.chessprogramming.org/bitboards
[^2]: https://github.com/Stringy/rust-chess/blob/master/src/bitboard.rs#L194