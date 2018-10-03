# vacationplanner
This is a dead simple script which I use to calculate my remaining vacation.

## Example
```
$ ./plan.py example.json
Wednesday, 02.05.2018     - Thursday, 03.05.2018      2.0 days
Friday, 01.06.2018                                    1.0 days
Thursday, 20.12.2018      - Friday, 21.12.2018        2.0 days
Thursday, 27.12.2018      - Friday, 28.12.2018        2.0 days
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Period             : 01.03.2018 to 31.12.2018
Vacation allowance : 20.0 days
Shifted into next  : 13.0 days
Effective allowance: 7.0 days
Vacation taken     : 7.0 days
Vacation remaining : 0.0 days

$ ./plan.py -e 2019 example.json
Wednesday, 02.01.2019     - Friday, 04.01.2019        3.0 days
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Period             : 01.01.2019 to 31.12.2019
Vacation allowance : 30.0 days
Shifted from prev  : 5.0 days
Effective allowance: 35.0 days
Vacation taken     : 3.0 days
Vacation remaining : 32.0 days
```

## License
GNU GPL-3.
