# WSU Lookup

Bruteforces a [leaky WSU page](https://livingat.wsu.edu/cardinfo/deposit/default.aspx) to discover a student's name and birthday using only their WSU ID.

I do not endorse using this program for nefarious purposes, it is developed only as proof of an unintended feature of the WSU website which has existed for many years.

If any university staff want me to take this repo down, please email me.

## Usage

```bash
# main.py [-h] [--quiet] ids [ids ...]
docker run --rm -it $(docker build -q .) 11525552
# That was my ID, but I'm out of the system so it doesn't work
```

## TODO

- Fix hang at the end of execution
