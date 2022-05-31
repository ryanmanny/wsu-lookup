# WSU Lookup

Bruteforces a [leaky WSU page](https://livingat.wsu.edu/cardinfo/deposit/default.aspx) to look up a student's name and birthday from only their WSU ID.

I do not endorse using this program for nefarious purposes, it is developed only as proof of an unintended feature of the WSU website which has existed for many years.

If any university staff want me to take this repo down, please email me.

## Usage

```
docker build . --tag wsu-lookup
docker run wsu-lookup [ids ...]
```

## TODO

- Add custom message for deactivated accounts
- Fix hang at the end of execution
