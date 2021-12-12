#!/bin/bash

# declare -a DateArray=("2021-11-04" "2021-11-19")
declare -a DateArray=("2021-11-04" "2021-11-19" "2021-11-22" "2021-11-26" "2021-11-30" "2021-12-03" "2021-12-06" "2021-12-07" "2021-12-08")

for date in "${DateArray[@]}"; do
    python ../strategies/v3/stoch_rsi.py --fromdate $date --stoch_rsi_period 11 --overbought 0.1 --oversold 0.9
    python ../strategies/v3/stoch_rsi.py --fromdate $date --stoch_rsi_period 9 --overbought 0.1 --oversold 0.9
    python ../strategies/v3/stoch_rsi.py --fromdate $date --stoch_rsi_period 11 --overbought 0.2 --oversold 0.8
    python ../strategies/v3/stoch_rsi.py --fromdate $date --stoch_rsi_period 9 --overbought 0.2 --oversold 0.8
    python ../strategies/v3/stoch_rsi.py --fromdate $date --stoch_rsi_period 11 --overbought 0.3 --oversold 0.7
    python ../strategies/v3/stoch_rsi.py --fromdate $date --stoch_rsi_period 9 --overbought 0.3 --oversold 0.7

    python ../strategies/v3/cheat_on_open_stoch_rsi.py --fromdate $date --stoch_rsi_period 11 --overbought 0.1 --oversold 0.9
    python ../strategies/v3/cheat_on_open_stoch_rsi.py --fromdate $date --stoch_rsi_period 9 --overbought 0.1 --oversold 0.9
    python ../strategies/v3/cheat_on_open_stoch_rsi.py --fromdate $date --stoch_rsi_period 11 --overbought 0.2 --oversold 0.8
    python ../strategies/v3/cheat_on_open_stoch_rsi.py --fromdate $date --stoch_rsi_period 9 --overbought 0.2 --oversold 0.8
    python ../strategies/v3/cheat_on_open_stoch_rsi.py --fromdate $date --stoch_rsi_period 11 --overbought 0.3 --oversold 0.7
    python ../strategies/v3/cheat_on_open_stoch_rsi.py --fromdate $date --stoch_rsi_period 9 --overbought 0.3 --oversold 0.7

    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 1 --sma_pslow 2
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 2 --sma_pslow 3
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 3 --sma_pslow 4
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 4 --sma_pslow 5
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 5 --sma_pslow 6
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 1 --sma_pslow 3
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 2 --sma_pslow 4
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 3--sma_pslow 5
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 4 --sma_pslow 6
    python ../strategies/v3/sma_cross.py --fromdate $date --sma_pfast 5 --sma_pslow 7

    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 1 --sma_pslow 2
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 2 --sma_pslow 3
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 3 --sma_pslow 4
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 4 --sma_pslow 5
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 5 --sma_pslow 6
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 1 --sma_pslow 3
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 2 --sma_pslow 4
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 3--sma_pslow 5
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 4 --sma_pslow 6
    python ../strategies/v3/cheat_on_open_sma_cross.py --fromdate $date --sma_pfast 5 --sma_pslow 7

    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 3 --pstreak 2 --prank 30 --overbought 90 --oversold 10
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 4 --pstreak 2 --prank 30 --overbought 90 --oversold 10
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 30 --overbought 90 --oversold 10
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 25 --overbought 90 --oversold 10
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 30 --overbought 80 --oversold 20
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 30 --overbought 70 --oversold 30
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 4 --pstreak 3 --prank 25 --overbought 90 --oversold 10
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 4 --pstreak 3 --prank 25 --overbought 80 --oversold 20
    python ../strategies/v3/cheat_on_open_conner_rsi.py --fromdate $date --prsi 4 --pstreak 3 --prank 25 --overbought 70 --oversold 30

    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 3 --pstreak 2 --prank 30 --overbought 90 --oversold 10
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 4 --pstreak 2 --prank 30 --overbought 90 --oversold 10
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 30 --overbought 90 --oversold 10
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 25 --overbought 90 --oversold 10
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 30 --overbought 80 --oversold 20
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 3 --pstreak 3 --prank 30 --overbought 70 --oversold 30
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 4 --pstreak 3 --prank 25 --overbought 90 --oversold 10
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 4 --pstreak 3 --prank 25 --overbought 80 --oversold 20
    python ../strategies/v3/conner_rsi.py --fromdate $date --prsi 4 --pstreak 3 --prank 25 --overbought 70 --oversold 30

done


