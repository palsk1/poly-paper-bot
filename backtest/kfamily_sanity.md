# Kalshi census sanity check (digs.py ksane)

A clean, fair market loses about $0 per $100 at the middle of bid and ask. Big losses at the middle mean the quotes were stale or one-sided, not real prices.

| group | events | bets | per $100 at the ask (+fee) | per $100 at the middle (no fee) |
|---|---|---|---|---|
| all | 42831 | 221931 | -$12.31 | -$0.34 |
| gap 0-2c | 28073 | 113980 | -$3.83 | -$0.03 |
| gap 2-5c | 16955 | 43207 | -$6.00 | -$0.04 |
| gap 5-15c | 11137 | 27262 | -$10.51 | -$0.10 |
| gap 15-100c | 14201 | 37482 | -$35.88 | -$1.79 |
| someone traded that hour | 29089 | 83174 | -$8.15 | -$0.22 |
| nobody traded that hour | 37321 | 138757 | -$14.65 | -$0.41 |
| traded that hour AND gap 0-2c | 19190 | 54330 | -$3.76 | -$0.04 |
| traded + gap 0-2c, 72h | 718 | 1486 | -$3.67 | -$0.05 |
| traded + gap 0-2c, 24h | 3406 | 6653 | -$3.80 | -$0.09 |
| traded + gap 0-2c, 6h | 8666 | 17125 | -$3.87 | -$0.02 |
| traded + gap 0-2c, 1h | 14828 | 29066 | -$3.69 | -$0.03 |
| traded + gap 0-2c, 2-10c YES | 3549 | 4225 | -$29.42 | -$13.41 |
| traded + gap 0-2c, 2-10c NO | 1024 | 1191 | -$40.82 | -$28.15 |
| traded + gap 0-2c, 10-25c YES | 4490 | 5480 | -$6.32 | +$3.12 |
| traded + gap 0-2c, 10-25c NO | 1220 | 1473 | -$8.58 | +$0.37 |
| traded + gap 0-2c, 25-50c YES | 6356 | 8408 | -$6.59 | -$0.76 |
| traded + gap 0-2c, 25-50c NO | 4546 | 6181 | -$11.56 | -$6.29 |
| traded + gap 0-2c, 50-75c YES | 4888 | 6688 | +$0.06 | +$3.99 |
| traded + gap 0-2c, 50-75c NO | 6308 | 8367 | -$3.10 | +$0.52 |
| traded + gap 0-2c, 75-90c YES | 1373 | 1683 | -$2.72 | -$0.64 |
| traded + gap 0-2c, 75-90c NO | 4431 | 5471 | -$2.71 | -$0.67 |
| traded + gap 0-2c, 90-98c YES | 762 | 896 | +$0.16 | +$1.32 |
| traded + gap 0-2c, 90-98c NO | 2970 | 3574 | -$0.85 | +$0.31 |

Examples: 90-98c buys that lost (quote age, gap, traded that hour, prices after)

- KXMLBINNINGTOTAL-26SEP111420PITCHC-7-1 24h NO paid 97c, gap 52c, age 106 min, vol 0.0, next bid/ask ['0.03/0.58', '0.03/0.55', '0.2/0.55', '0.43/0.48'] | 7th inning: Over 0.5 runs | Over 0.5 runs in the 7th inning
- KXNCAAWVMATCH-26SEP111400PRSTTTU-PRST 24h YES paid 96c, gap 93c, age 11 min, vol 0.0, next bid/ask ['0.03/0.96', '0.03/0.96', '0.03/0.96', '0.03/0.96'] | Portland State wins | Portland State
- KXNCAAWVMATCH-26SEP111400PRSTTTU-PRST 6h YES paid 97c, gap 94c, age 131 min, vol 0.0, next bid/ask ['0.03/0.96', '0.02/0.59', '0.0/0.59', '0.0/0.01'] | Portland State wins | Portland State
- KXNCAAWVMATCH-26SEP111600ALBYDART-ALBY 24h YES paid 96c, gap 93c, age 21 min, vol 0.0, next bid/ask ['0.03/0.96', '0.03/0.96', '0.03/0.96', '0.03/0.96'] | Albany wins | Albany
- KXNCAAWVMATCH-26SEP111600ALBYDART-ALBY 6h YES paid 97c, gap 94c, age 81 min, vol 0.0, next bid/ask ['0.03/0.95', '0.35/0.95', '0.16/0.84', '0.56/0.8'] | Albany wins | Albany
- KXTTELITEMATCH-26SEP110840MBAJPE-MBA 6h YES paid 94c, gap 88c, age 0 min, vol 0.0, next bid/ask ['0.06/0.94', '0.05/0.95', '0.0/0.01'] | Mariusz Baron wins | Mariusz Baron
- KXTTELITEMATCH-26SEP110115KWILAD-LAD 6h YES paid 94c, gap 88c, age 40 min, vol 0.0, next bid/ask ['0.06/0.94', '0.05/0.95', '0.27/0.28'] | Linek Adam wins | Linek Adam
- KXR6GAME-26SEP110500DKCYBME-DK 24h NO paid 94c, gap 85c, age 60 min, vol 0.0, next bid/ask ['0.87/0.91', '0.87/0.91', '0.87/0.91', '0.87/0.91'] | Will Dplus win the Dplus vs. Can You Be My Enemy R6 match? | Dplus
- KXSCOCUPADVANCE-26SEP11STEHOM-HOM 72h NO paid 97c, gap 86c, age 35 min, vol 0.0, next bid/ask ['0.04/0.89', '0.04/0.9', '0.05/0.89', '0.06/0.9'] | Heart of Midlothian To Advance | Heart of Midlothian advances
- KXARENASCORE-GPT6ASTRA-1495 6h YES paid 95c, gap 91c, age 9 min, vol 0.0, next bid/ask ['0.04/0.95', '0.04/0.95', '0.04/0.95', '0.05/0.94'] | GPT 6 Astra debut arena score? | Above 1495
- KXARENASCORE-GPT6ASTRA-1495 1h YES paid 94c, gap 89c, age 9 min, vol 0.0, next bid/ask ['0.01/0.5'] | GPT 6 Astra debut arena score? | Above 1495
- KXBIGGESTQUAKE-11SEP26-6.4 24h NO paid 96c, gap 18c, age 60 min, vol 0.0, next bid/ask ['0.04/0.22', '0.04/0.22', '0.03/0.23', '0.02/0.22'] | What will the biggest earthquake be on Sep 11, 2026? | Magnitude of at

