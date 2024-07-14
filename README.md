# Setup and running
1. install pyenv and install python 3.11.9
```terminal
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate
make install
make test
make run
```

## What is this?
* I was following along with the book "Writing An Interpreter In Go" but kept getting confused by go code
    * No null or optional type?
    * Why is type casting done like this?
    * Why do you write tests like this??
    * Why single letter variables?
* So I decided to switch to python and folow along