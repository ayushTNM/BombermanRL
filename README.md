BombermanRL
===========

We explore the extent to which RL can be applied to the bomberman problem that is traditionally solved with A* and BFS.

What is new and interesting about this project is not just that we found some interesting results, our game also looks good.

Setup
-----
This project does require at least Python 3.9, probably even 3.10.

The setup is simple:

```bash
$ git clone git@github.com:ayushTNM/BombermanRL.git   # assuming SSH is set up
$ cd BombermanRL
$ python3 -m venv venv                                # create a virtual environment
$ source venv/bin/activate                            # activate virtual environment
(venv) $ pip install -r requirements.txt
(venv) $ cd src
(venv) $ python3 menu.py -h
```

This will show all of the parameters you can change from the CLI.

To run the file with default parameters, just type:

```bash
(venv) $ python3 menu.py
```

Some fundamental parameters to look into:

```bash
-o [plotname]        # store the learning curves as a plot
-m                   # flag to turn on menu (if you want to play yourself)
```

Demo
----

**5x5 with 6 crates**

<fig>
<img src="https://github.com/ayushTNM/BombermanRL/blob/main/assets/readme/5x6c.gif" width="512" height="512" alt="5x5 6c demo"/>
</fig>

**5x5 with 7 crates**

<fig>
<img src="https://github.com/ayushTNM/BombermanRL/blob/main/assets/readme/5x7c.gif" width="512" height="512" alt="5x5 6c demo"/>
</fig>

**8x8 with 6 crates**

<fig>
<img src="https://github.com/ayushTNM/BombermanRL/blob/main/assets/readme/8x6c.gif" width="512" height="512" alt="5x5 6c demo"/>
</fig>


**9x9 with 4 crates**

<fig>
<img src="https://github.com/ayushTNM/BombermanRL/blob/main/assets/readme/9x4c.gif" width="512" height="512" alt="5x5 6c demo"/>
</fig>
  
**10x10 with 6 crates**

<fig>
<img src="https://github.com/ayushTNM/BombermanRL/blob/main/assets/readme/10x6c.gif" width="512" height="512" alt="5x5 6c demo"/>
</fig>
