# TRi-structural ISOtropic Fuel

This research folder contains information and analysis regarding the questions
of:
1. What are the SWU requirements for TRISO fueled reactor transitions that
   incorporate the proposed LEU+ to HALEU scheme?
2. What are the impacts of deployment schemes in NFC scenarios, and what parts
   are realistic or unrealistic in each?

## Scenarios
We have investigated several growth scenarios at a low, medium, and high
rates based on different projections in the literature. The calculations for
these scenarios can be found in `deployment_calcs`, where there is a notebook
for each level of growth.

### No Growth
A 0% demand growth deployment scenario where LWRs retire at end of license or
at 80 years of operation, whatever is longer. If there are Advanced reactors in
the scenario, they will replace the decommissioned capacity and meet the demand
growth starting in 2030.

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DAN0     | 0%            | LWRs                       |       |
| DAN1     | 0%            | LWRs, Xe-100               |       |
| DAN2     | 0%            | LWRs, MMR                  |       |
| DAN3     | 0%            | LWRs, AP1000               |       |
| DAN4     | 0%            | LWRs, MMR, Xe-100, AP1000  |       |

### Low Growth
A 1% demand growth deployment scenario where LWRs retire at end of license or
at 80 years of operation, whatever is longer. If there are Advanced reactors in
the scenario, they will replace the decommissioned capacity and meet the demand
growth starting in 2030.

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DAL1     | 1%            | LWRs, Xe-100               |       |
| DAL2     | 1%            | LWRs, MMR                  |       |
| DAL3     | 1%            | LWRs, AP1000               |       |
| DAL4     | 1%            | LWRs, MMR, Xe-100, AP1000  |       |

### Medium Growth
A 5, 10, or 15% demand growth deployment scenario where LWRs retire at end of
license or at 80 years of operation, whatever is longer. If there are Advanced
reactors in the scenario, they will replace the decommissioned capacity and
meet the demand growth starting in 2030.

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DA5M1    | 5%            | LWRs, Xe-100               |       |
| DA5M2    | 5%            | LWRs, MMR                  |       |
| DA5M3    | 5%            | LWRs, AP1000               |       |
| DA5M4    | 5%            | LWRs, MMR, Xe-100, AP1000  |       |

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DA10M1   | 10%           | LWRs, Xe-100               |       |
| DA10M2   | 10%           | LWRs, MMR                  |       |
| DA10M3   | 10%           | LWRs, AP1000               |       |
| DA10M4   | 10%           | LWRs, MMR, Xe-100, AP1000  |       |

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DA15M1   | 15%           | LWRs, Xe-100               |       |
| DA15M2   | 15%           | LWRs, MMR                  |       |
| DA15M3   | 15%           | LWRs, AP1000               |       |
| DA15M4   | 15%           | LWRs, MMR, Xe-100, AP1000  |       |

### High Growth
A 100 or 200% demand growth deployment scenario where LWRs retire at end of
license or at 80 years of operation, whatever is longer. If there are Advanced
reactors in the scenario, they will replace the decommissioned capacity and
meet the demand growth starting in 2030.

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DA1A1    | 100%          | LWRs, Xe-100               |       |
| DA1A2    | 100%          | LWRs, MMR                  |       |
| DA1A3    | 100%          | LWRs, AP1000               |       |
| DA1A4    | 100%          | LWRs, MMR, Xe-100, AP1000  |       |

| Scenario | Demand Growth | Reactors                   | Notes |
|----------|---------------|----------------------------|-------|
| DA2A1    | 200%          | LWRs, Xe-100               |       |
| DA2A2    | 200%          | LWRs, MMR                  |       |
| DA2A3    | 200%          | LWRs, AP1000               |       |
| DA2A4    | 200%          | LWRs, MMR, Xe-100, AP1000  |       |

## Analysis
Stores the notebooks used for data analysis.

## Reactors
Stores `.xml` definition files for the reactors used in this work. Inside there
is a folder called `lwrs/` that contains the unique definition for each reactor
in the US fleet.