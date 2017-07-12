## GAPS:

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




## FROM APPENDIX B OF FUELCYCLEEVALUATION.INL.GOV
### EG23
Continuous recycle of Pu/U in SFR:

| Category  | Driver| Blanket | 
| :-------------: |:-------------:| -----:|
| Material | Pu / Rep U | Nat U |
| Burnup | 81.5 Gwd/t | 23.5 Gwd/t | 
| Composition |15.3 % Pu | .7% U235 |  
| Fuel Residence Time | 3.6 years (avg) |
| Normalized % |91.21% | 8.79 % |

For 100 GW-year (250 FR-year), uses 1,257,400 kg of fuel  
-> 1 FR spends 1,257,400/250 * (14/12) = **5867 kg / Batch**  

Refueling frequency: 14 months  
Refueling time: 1 month

------

### EG24
Continuous recycle of TRU/U in SFR:



| Category  | Driver| 
| :-------------: |:-------------:| 
| Material | TRU / Rep U / Nat U | 
| Burnup | 73 Gwd/t |  
| Composition | 13.9% TRU |  
| Fuel Residence Time | 3.6 years |
 

For 100 GW-year (250 FR-year), uses 1,251,200 kg of fuel  
-> 1 FR spends 1,251,200/250 * (14/12) = **5838 kg / Batch**  

Refueling frequency: 14 months  
Refueling time: 1 month

------
### EG29
Pu/U produced in SFR used to operate PWR in continuous recycle strategy:


| Category  | Driver| Blanket | MOX | 
| :------------- |:-------------:| :-----:|  :-----:|
| Material | Pu / Rep U / Nat U | Rep U / Nat U | Pu / Rep U |
| Burnup | 96.8 Gwd/t | 20.7 Gwd/t | 50 GWd/t | 
| Composition | 21.4 % Pu | ~.2 % U235 | 9.11% Pu |  
| Fuel Residence Time | 5 years (avg) | 3.9 years |
| Normalized % | 33.3 %  | 66.7 % | 100% |

**FR:**
For 61.08 GW-year (152 FR-year), uses 1,206,900 kg of fuel  
-> 1 FR spends 1,206,900/152 * (14/12) = **9263 kg / Batch**  
Refueling frequency: 14 months  
Refueling time: 1 month

**MOX LWR:**
For 38.92 GW-year (39 LWR-year), uses 861,400 kg of fuel  
-> 1 MOX LWR spends 861,400/39 * (18/12) = **33130 kg / Batch**  
Refueling frequency: 18 months  
Refueling time: 1 month

------

### EG30
TRU/U produced in SFR used to operate PWR in continuous recycle strategy:

| Category  | Driver| Blanket | MOX | 
| :-------------: |:-------------:| :-----:|  :-----:|
| Material | TRU / Rep U / Nat U | Rep U / Nat U | TRU / Rep U |
| Burnup | 107 Gwd/t | 23 Gwd/t | 50 GWd/t | 
| Composition | 24.4 % TRU | .15 % U235 | 10.4 % TRU |  
| Fuel Residence Time | 4.9 years (avg) | 3.9 years |
| Normalized % | 47 %  | 53 % | 100% |

**FR:**  
For 87.0 GW-year (218 FR-year), uses 1,218,300 kg of fuel  
-> 1 FR spends 1,218,300/218 * (14/12) = **6519 kg / Batch**    
Refueling frequency: 14 months  
Refueling time: 1 month

**MOX LWR:**  
For 13 GW-year (13 LWR-year), uses 287,000 kg of fuel  
-> 1 MOX LWR spends 287,000/13 * (18/12) = **33115 kg / Batch**    
Refueling frequency: 18 months  
Refueling time: 1 month
