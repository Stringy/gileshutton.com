---
title: "Tinker"
date: 2022-01-08T15:01:56Z
draft: false
tags: ["coding", "tinker", "godot", "gamedev"]
categories: ["code"]
summary: "A new project and a cautionary tale about decision paralysis."
---

Recently I got a new job. This is perhaps not the most interesting piece of information in
the world, but it was long overdue and in fact only the second job I've had out of university.
Again, not that interesting, but it gave me a few weeks of nothing between the two jobs and 
to fill the time I started working on a little game.

It started with an idea that I had rolling around my head for a few years. I wanted a 
2D top-down survival / exploration game. The natural progression of that is some kind of
procedurally generated world, possibly infinite, and then some survival mechanics and
a reason for the player to actually play the game. My first thought was Minecraft but 2D. Not 
the most original idea in the world, and probably way too much scope for a first game!

First decision in any game dev project is always the technology you use to build the game. This
is not an unfamiliar dilema for me. On more than one occasion I've tried to make a game and have
been paralysed by the decision of which engine or framework or whatever to use. Maybe I should
write the whole thing from scratch? maybe I should use Unity? or Unreal? or SDL2? in C? in C++?
in Rust? I hear pygame is good for getting something working quickly, and Python is very easy to
work with. Argh. This time was no exception, though I started out really strong.

I decided to use Godot[^1]. The speed at which I was able to get something simple up and running
was astonishing. In the first day I had a simple player-controlled character (using the Godot icon
as the sprite, for simplicity) moving around on small grass world. Over the next week I went from
that simple attempt all the way up to infinite terrain, character animations, an inventory system,
health, hunger, thirst, eating food, and dropping items. It was fantastic.

{{< video "/video/tinker-first.webm" "Humble Beginnings." >}}

Godot comes with such an incredible toolkit of useful functionality, through its intuitive node 
system. You can just chuck a bunch of nodes into a scene and a game falls out the other side. 
Every time I thought it was missing something, a little googling showed that there was some 
node or some mechanism that did all this for me. Things like Y-sorting sprites to give the 
illusion of depth, or adding smoothing to the camera. Even the somewhat esoteric scripting 
language, GDScript, grew on me as I used it. Given its usecase it's extremely well designed, 
and provides all the features you need to build the kinds of game logic you require.

{{< video "/video/tinker-with-features.webm" "Trees, grass, animations, the works." >}}

And then, a month or two into development, I hit a wall.

I was trying to add trees to the terrain generator and I'd iterated on the trees themselves a
bit, taking them from "stamps" on the tilemap to their own distinct objects (in Godot, these 
are instances of scene trees.) Everything was working, but on my infinite terrain, performance was
taking a huge hit every time the game needed to generate a new region of the map. Cue massive churn,
and flip flopping between technologies every other day.

First, I thought "surely GDScript is the bottle neck, I'll rewrite this in Rust for speed and safety!"
So I did. I spent the day getting familiar with godot-rust[^2] and then went to town converting some
of my scripts to Rust. Initially, life was good. I got to use Rust again and it *must* be faster, right?
But no, of course it was about the same, but I'd wasted all that time converting all the scripts. Not to
mention the additional overhead of writing this kind of functionality in a much stricter language.

Strike 1. So I went back to GDScript and tried to find out how I could improve the generation. The original
implementation waited for the player to move far enough away from the center of the current region and then 
generated a new region around the player. How could I improve that performance? After a bit of thought I decided
that I could generate terrain in the background, with the main thread sending jobs (just regions of the map)
to the generator, and then picking them up later on. Took me only an hour or so to get that up and running in
GDScript, but I was getting occasional SEGFAULTs. Not good. But you know what claims to have excellent memory 
and thread safety? Rust. So back on the bandwagon I go, this time rolling in some async for good measure. This
implementation took much longer to build and I spent most of my time fighting the Godot bindings rather than 
building my game or fixing my terrain generation. Strike 2.

{{< video "/video/tinker-object-cull.webm" "Basic object culling and triggered terrain generation." >}}

A smarter developer than me would go back to the GDScript, spend some time debugging, figure out what the 
problem was, and then continue with adding game features. I am not that smart. I packed it all in and started
working on my own engine. Luckily, it didn't get very far, but I was going to write it in Rust with ECS architecture
and my own custom resource loading, and sensible async right from the start. But then I started to burn out. I spent
so trying to build the same things that Godot gave me for free, instead of building game features and progressing 
the project. Strike 3. 

I stopped working on it for a week or so at that point. Too much churn, too little progress. And somewhat inevitably,
I find myself back where I started, using Godot and GDScript, but creating features for the game and making some 
forward progress. I think on a project like this, momentum is so important to keep the project alive and to stay motivated.
Plenty of other people have expressed this far better than me[^3] [^4], but for myself: churn on game features, not on technology or engine choice or language or whatever. Keep up the momentum.

Turns out the terrain generation SEGFAULTs were caused by my attempts to update the `TileMap` from the generation
thread, mostly because I misunderstood Godot signal behaviour. Very simple to fix as it turns out, and 
now the terrain is generating at a smooth 60 fps, even with thousands of terrain objects.

Anyway, I hear bevy[^5] is the latest awesome technology in Rust gamedev so perhaps I should check it out ... ?


[^1]: https://godotengine.org/
[^2]: https://github.com/godot-rust/godot-rust
[^3]: https://www.youtube.com/watch?v=VvHw7JP47ts
[^4]: https://geometrian.com/programming/tutorials/write-games-not-engines/
[^5]: https://bevyengine.org/
