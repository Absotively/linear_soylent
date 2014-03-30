# Soylent solver

A very rough linear solver for [soylent.](http://diy.soylent.me)

It reads json from diy.soylent.me on stdin and outputs a couple ascii tables and some other info on stdout.

It first attempts to find the cheapest recipe using the provided ingredients that fits the provided profile. If this fails because it is not possible to balance the recipe using the provided ingredients & profile, then it will find the least unbalanced recipe, using a "deviation" calculation similar to the one used by [2potatoes' genetic soylent solver](http://2potatoes.github.io/genetic-soylent/)

## Installation

Requires lpsolve and Python. Unfortunately, if you don't want to compile the lpsolve Python support yourself, you'll need Python 2.6, even though it's outdated. You'll also need to install the lpsolve library separately; on Windows, this means manually dropping the dll into C:\Windows\system32.

[Python 2.6 is here](https://www.python.org/download/releases/2.6.6)

[lpsolve is here.](http://sourceforge.net/projects/lpsolve/files/lpsolve/5.5.2.0/) The compiled Python support is in the archives with "Python2.6_exe" in their names. The library is in the archives with "dev" in their names.