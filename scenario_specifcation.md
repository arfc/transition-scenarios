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




## FROM APPENDIX B OF FUELCYCLEEVALUATION.INL.GOV
### EG23
Continuous recycle of Pu/U in SFR:
In this Analysis Example, an SFR core consists of driver and radial blanket fuels to achieve a breakeven
conversion ratio (i.e., slightly higher than 1.0 to account for losses in the fuel separation and
fabrication) in the equilibrium state. The U-Pu-Zr ternary metallic fuel is irradiated to burnup of 81.5
GWd/t in the driver fuel zone, while the U-Zr binary metallic fuel is irradiated to burnup of 23.5
GWd/t in the radial blanket zone. The average fuel burnup is 72.6 GWd/t. The discharged UNF is
reprocessed to recover both Pu and RU that are recycled back into the SFR. The MA, FP, and
material losses from fuel reprocessing are waste that is sent to disposal. Any low level waste is also
sent to disposal. NU is the only external makeup feed during fuel production, used for replacing the
heavy metal destroyed by fission. Note that this is the traditional SFR breeder. In a growth scenario,
the SFR would be configured to breed excess fissile material at a level commensurate with the
demand for startup of new reactors.

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
This is a companion Analysis Example to the one for EG23. In this case, TRU in metallic fuel instead
of Pu-only is recycled in the SFR. In this Analysis Example, the SFR uses U-TRU-Zr driver fuel only
(no blanket) to achieve a break-even TRU conversion ratio (i.e., slightly higher than 1.0 to account
for losses in the fuel separation and fabrication) in the equilibrium state. The U-TRU-Zr metallic fuel
is irradiated to burnup of 73 GWd/t and discharged from the reactor. The discharged UNF is
reprocessed to recover both TRU and RU that are recycled back into the same SFR. The FP, excess
RU, and material losses from fuel reprocessing are waste that is sent to disposal. Any low level waste
is also sent to disposal. The recovered RU is the primary source of uranium with an external supply
of uranium required as makeup for the roughly 7% of heavy metal fissioned each recycle pass.


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
This is a two-stage Analysis Example involving SFRs and PWRs in which Pu is produced in the
Stage 1 SFR breeder for use in running the Stage 2 PWR. The SFR in Stage 1 uses driver and blanket
fuels. In the equilibrium state, Pu/U recovered from the reprocessing of the discharged driver fuels from
the Stage 1 SFRs are mixed with NU (used as external feed) to make new Pu/U metallic driver fuel for
Stage 1. The blanket is made from natural uranium and recovered uranium from the reprocessing of the
Stage 1 blanket fuel. These driver and blanket fuels are irradiated to discharged burnups of 97 and 21
GWd/t, respectively. The excess Pu/U from the reprocessing of the discharged blanket fuel is recycled to
Stage 2. The FP, MA and material losses during fuel reprocessing of the Stage 1 fuels are waste that is sent
to disposal.
Recovered Pu/U from Stage 2 PWR and excess recovered Pu /U from the blanket fuels of Stage 1 SFR are
used to make Pu/U MOX fuel for the Stage 2 PWR. No NU is necessary since the Pu/U from Stage 1
brings enough RU. The Pu/U MOX fuel is irradiated to a burnup of 50 GWd/t in the Stage 2 PWR and the
discharged UNF is reprocessed. The recovered Pu /U is recycled back to Stage 2. The MA, FP and
material losses during fuel reprocessing are waste that is sent to disposal. Any low level waste is also sent
to disposal. Note that for this Analysis Example to be viable, it is necessary to feed the PWR (MOX) with
the high fissile content Pu from the SFR blanket of Stage 1. If a less fissile Pu mixture is used (e.g., a blend
of Pu coming from the SFR driver fuel and blanket) the necessary Pu content in the PWR (MOX) becomes
higher than the upper limit required by the reactor safety (i.e., ~12% Pu) after a few recycles

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
This is a counterpart Analysis Example to the example for EG29, with the exception that TRU
recycle is the target in this two-stage example. The Stage 1 SFR breeder is used to produce TRU for
use in running the Stage 2 PWR. The SFR in Stage 1 uses driver and blanket fuels. In the equilibrium
state, recovered TRU/U from Stage 1 and recovered MA from Stage 2 are mixed with NU (used as
external feed) to make driver TRU/U metallic fuel. The blanket is made from natural uranium and
recovered uranium from the reprocessing of the Stage 1 blanket fuel. The metallic driver fuel in the
SFR breeder is irradiated to burnup of 107 GWd/t. The blanket fuel is irradiated to burnup of 23
GWd/t. The discharged UNF from driver fuel is reprocessed to recover TRU/U that is recycled back
into Stage 1 for making new driver fuel. The excess recovered TRU/U from the reprocessing of the
discharged blanket fuel are recycled for making fuel for the Stage 2 PWR. The FP and material losses
during the reprocessing of the Stage 1 fuels are waste that is sent to disposal.
Recovered Pu/U from Stage 2 PWR and recovered TRU/U from the blanket fuels of Stage 1 are used
to make TRU/U MOX fuel for the Stage 2 PWR. The TRU/U MOX fuel is irradiated to a burnup of
50 GWd/t in the Stage 2 PWR and following discharge is reprocessed. Recovered Pu/U is recycled
back to Stage 2. Recovered MA is sent to Stage 1 to reduce MA content in Stage 2 PWR fuels. FP
and material losses during the reprocessing of the Stage 2 fuel are waste that is sent to disposal. Any
low level waste is also sent to disposal. 

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
