---
title: "Intentions"
date: 2020-05-28T12:59:44+01:00
draft: false
tags: ["coding", "chess"]
categories: ["code"]
summary: ""
images: ["img/coding/chess.jpg"]
---

Since the coding section is currently empty, I thought I'd write a quick blurb about
what I intend to publish in this section and what form that'll be. 

<!--more-->

Ever since university I've had an interest in computer Chess. I admired from a distance
the likes of Deep Blue, Stockfish, and more recently AlphaZero. For my university dissertation
in my final year, I wrote one for myself. 

Written in Go[^1], it was quite simple, quite naive, and unsurprisingly flawed. One of the 
more interesting bugs was that the AI would occasionally decide that moving its opponents 
pieces was the best move for the given board state. I never got to the bottom of it, but 
it did rear its ugly head in the middle of a live demo that I gave to my supervisor as part
of the final assessment. Still, I got a decent grade in spite of this!

I've decided to revisit that project in my spare time, this time jumping on the band-wagon
and writing the thing in Rust[^2]. I have made some good progress so far, though it's currently
just a port from my Go version, with added Rust idioms and abstractions.

To start with, I intend to write about Chess in this coding section. I want to give an overview 
of powerful features of Rust that make Chess programming easier, and I want to discuss some of
the techniques that I'm using in my Rust Chess engine.

I think I'll start in the coming week by going over Bitboards, one of the most impressive
and powerful techniques I've seen for Chess programming.


[^1]: https://github.com/Stringy/go-chess 

[^2]: https://github.com/Stringy/rust-chess (WIP)

