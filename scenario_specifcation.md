## Assumption, Parameters, Models and References:

1. The compositions, core mass and reactor ratio are obtained from [appendix B of E&S study](https://fuelcycleevaluation.inl.gov/Shared%20Documents/ES%20Appendix%20B.pdf).

2. The assumptions of net installed power increase and advanced technology availability are obtained from [FCO study](https://github.com/arfc/transition-scenarios/files/796778/5061-.final.pdf).

3. `CYCAMORE::REACTOR`, the recipe reactor, was used for the reactor archetype.

4. `CYCAMORE::MIXER`, the fixed ratio mixer, was used for the fuel fabrication archetype.

5. EG23 and EG24 are done using an approximate recipe from ORGIEN.

6. EG29 and EG30 are done using a simplification (4 group - U, TRU, MA, FP) model.

7. For SFRs, blanket and driver are averaged into one 'core' (added mass with weighted composition).

## Gaps:

1. Recipe Reactor Limitations:
   * Can't match with Burnup, needs recipe (always same composition out)

2. Fuel Cycle Facility limitations:
   * Simple infinite capacity / throughput
        instead of deployment of multiple facilities depending on need.
   * FuelFab cannot mix three commodities (Nat U, Rep U, Rep TRU/Pu)

3. FR modeling limitations:
   * blanket and driver composition has to be averaged
   * Separate EFPY for blanket and driver can't be modeled

4. Can't Match Demand:
   * Demand of FR fuel can't be met, and the FR just gets deployed, but does not produce power

5. EG29, 30 reprocessed material only goes in one mixer if both mixer has infinite throughput / buffer.

6. Throughput should be adjusted according to fuel demand, in order for the distribution
of fissile commodity (rep U, TRU, PU) among different fuel fab facilities.
( If two facilities with infinite throughput (demand of commodity A) exists, one facility gets all
the commodity A and the other none. Also, When given a situation where multiple demands cannot be met,
the agent with a higher demand quantity is preferred.)


## From Appendix B of Fuelcycleevaluation.inl.gov
### EG23
Continuous recycle of Pu/U in SFR:

$
    \begin{table}[h]
        \centering
        \caption {EG23 - Continuous Recycle of Pu/U in SFR:}
            \begin{tabular}{|c|c|c|}
                \hline
                Category & Driver & Blanket \\ \hline
                Material & Pu / Rep U & Nat U  \\ \hline
                Burnup & 81.5 Gwd/t & 23.5 Gwd/t \\ \hline
                Composition & 15.3 \% Pu & 0.7\% U235 \\ \hline
                Fuel Residence Time & 3.6 years (avg) & 3.6 years (avg) \\ \hline
                Normalized \% & 91.21\% & 8.79\% \\ \hline
                
            \end{tabular}
            \end {table}
$
For 100 GW-year (250 FR-year) the SFR fleet uses 1.25e6 kg of fuel.
1 FR spends 1,257,400/250 = 5,029 kg / year
Since a batch is replaced every 14 months, the mass of a batch is: 5,029 * (14/12) = **5,867 kg / Batch **

Refueling frequency: 14 months  
Refueling time: 1 month

------

### EG24
Continuous recycle of TRU/U in SFR:

$
    \begin{table}[h]
        \centering
        \caption {EG24 - Continuous Recycle of TRU/U in SFR:}
            \begin{tabular}{|c|c|}
                \hline
                Category & Driver  \\ \hline
                Material & TRU / Rep U \\ \hline
                Burnup & 73 Gwd/t  \\ \hline
                Composition & 13.9 \% TRU  \\ \hline
                Fuel Residence Time & 3.6 years \\ \hline
                
            \end{tabular}
            \end {table}
$

 For 100 GW-year (250 FR-year) the SFR fleet uses 1.25e6 kg of fuel.
1 FR spends 1,251,200/250 = 5,004 kg / year
Since a batch is replaced every 14 months, the mass of a batch is: 5,004 * (14/12) = **5,838 kg / Batch **

Refueling frequency: 14 months  
Refueling time: 1 month

------
### EG29
Pu/U produced in SFR used to operate PWR in continuous recycle strategy:

$
    \begin{table}[h]
        \centering
        \caption {EG29 - Pu/U produced in SFR used to operate PWR in continuous recycle strategy:}
            \begin{tabular}{|c|c|c|c|}
                \hline
                Category & Driver & Blanket & MOX \\ \hline
                Material & Pu / Rep U / Nat U & Rep U / Nat U & Pu / Rep U \\ \hline
                Burnup & 96.8 Gwd/t & 20.7 Gwd/t & 50 GWd/t \\ \hline
                Composition & 21.4 \% Pu & ~.2\% U235 & 9.11\% Pu  \\ \hline
                Fuel Residence Time & 5 years (avg) & 5 years (avg) & 3.9 years \\ \hline
                Normalized \% & 33.3\% & 66.7\% & 100\% \\ \hline
                
            \end{tabular}
            \end {table}
$

**FR:**

For 61.08 GW-year (152 FR-year) the SFR fleet uses 1.206e6 kg of fuel.
1 FR spends 1,206,900/152 = 7,940 kg / year
Since a batch is replaced every 14 months, the mass of a batch is: 5,029 * (14/12) = **9,263 kg / Batch **
Refueling frequency: 14 months  
Refueling time: 1 month

**MOX LWR:**
For 38.92 GW-year (39 LWR-year), the MOX LWR fleet uses 8.6e5 kg of fuel.
1 MOX LWR spends 861,400/39 = 22,087 kg / year
Since a batch is replaced every 18 months, the mass of a batch is: 22,087 * (18/12) = **33130 kg / Batch **
Refueling frequency: 18 months  
Refueling time: 1 month

------

### EG30
TRU/U produced in SFR used to operate PWR in continuous recycle strategy:

$
    \begin{table}[h]
        \centering
        \caption {EG30 - TRU/U produced in SFR used to operate PWR in continuous recycle strategy:}
            \begin{tabular}{|c|c|c|c|}
                \hline
                Category & Driver & Blanket & MOX \\ \hline
                Material & TRU / Rep U / Nat U & Rep U / Nat U & TRU / Rep U \\ \hline
                Burnup & 107 Gwd/t & 23 Gwd/t & 50 GWd/t \\ \hline
                Composition & 24.4 \% TRU & .15\% U235 & 10.4 \% TRU  \\ \hline
                Fuel Residence Time & 4.9 years (avg) & 4.9 years (avg) & 3.9 years \\ \hline
                Normalized \% & 47\% & 53\% & 100\% \\ \hline
                
            \end{tabular}
            \end {table}
$

**FR:**

For 87.0 GW-year (218 FR-year) the SFR fleet uses 1.218e6 kg of fuel.
1 FR spends 1,218,300/218 = 5,588 kg / year
Since a batch is replaced every 14 months, the mass of a batch is: 5,588 * (14/12) = **6,519 kg / Batch **
Refueling frequency: 14 months  
Refueling time: 1 month

**MOX LWR:**
For 13 GW-year (13 LWR-year), the MOX LWR fleet uses 2.87e5 kg of fuel.
1 MOX LWR spends 287,000/13 = 22,076 kg / year
Since a batch is replaced every 18 months, the mass of a batch is: 22,076 * (18/12) = **33115 kg / Batch **
Refueling frequency: 18 months  
Refueling time: 1 month
