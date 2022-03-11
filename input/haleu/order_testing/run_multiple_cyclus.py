import json
import re
import subprocess
import os
import sqlite3 as lite
import copy
import glob
import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import d3ploy.tester as tester
import d3ploy.plotter as plotter
import collections


# Delete previously generated files
direc = os.listdir('./')
file_base = 'fft_noDI_back'
hit_list = glob.glob(file_base+'*.sqlite') + glob.glob(file_base+'*.xml')
for file in hit_list:
    os.remove(file)

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')


##### List of types of calc methods that are to be tested #####
calc_methods = ["ma", "arma", "arch", "poly",
                "exp_smoothing", "holt_winters", "fft", "sw_seasonal"]
step_sizes = ["1", "2","5","10", "20"]

control = """
<control>
    <duration>1000</duration>
    <startmonth>1</startmonth>
    <startyear>2000</startyear>
</control>"""

archetypes = """
<archetypes>
        <spec>
            <lib>cycamore</lib>
            <name>Source</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Reactor</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Sink</name>
        </spec>
        <spec>
            <lib>agents</lib>
            <name>NullRegion</name>
        </spec>
        <spec>
            <lib>agents</lib>
            <name>NullInst</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>DeployInst</name>
        </spec>
        <spec>
            <lib>d3ploy.demand_driven_deployment_inst</lib>
            <name>DemandDrivenDeploymentInst</name>
        </spec>
    </archetypes>
"""

source = """
<facility>
    <name>source</name>
    <config>
        <Source>
            <outcommod>fresh_fuel</outcommod>
            <outrecipe>fresh_fuel_recipe</outrecipe>
            <throughput>1e6</throughput>
        </Source>
    </config>
</facility>
"""

LWR = """
  <facility>
    <name>LWR</name>
    <lifetime>240</lifetime>
    <config>
      <Reactor>
        <fuel_incommods> <val>fresh_fuel</val> </fuel_incommods>
        <fuel_inrecipes> <val>fresh_fuel_recipe</val> </fuel_inrecipes>
        <fuel_outcommods> <val>spent_fuel</val> </fuel_outcommods>
        <fuel_outrecipes> <val>spent_fuel_recipe</val> </fuel_outrecipes>
        <cycle_time>18</cycle_time>
        <refuel_time>1</refuel_time>
        <assem_size>100</assem_size>
        <n_assem_core>1</n_assem_core>
        <n_assem_batch>1</n_assem_batch>
        <power_cap>100</power_cap>
      </Reactor>
    </config>
  </facility>
"""

AR = """
  <facility>
    <name>AdvancedReactor</name>
    <lifetime>240</lifetime>
    <config>
      <Reactor>
        <fuel_incommods> <val>fresh_fuel</val> </fuel_incommods>
        <fuel_inrecipes> <val>fresh_fuel_recipe</val> </fuel_inrecipes>
        <fuel_outcommods> <val>spent_fuel</val> </fuel_outcommods>
        <fuel_outrecipes> <val>spent_fuel_recipe</val> </fuel_outrecipes>
        <cycle_time>24</cycle_time>
        <refuel_time>1</refuel_time>
        <assem_size>75</assem_size>
        <n_assem_core>1</n_assem_core>
        <n_assem_batch>1</n_assem_batch>
        <power_cap>75</power_cap>
      </Reactor>
    </config>
  </facility>
  """

sink = """
<facility>
        <name>sink</name>
        <config>
            <Sink>
                <in_commods>
                    <val>spent_fuel</val>
                </in_commods>
                <max_inv_size>1e6</max_inv_size>
            </Sink>
        </config>
    </facility>
"""

region = {}

for step_size in step_sizes:
    region[step_size] = """
   <region>
        <config>
            <NullRegion>
            </NullRegion>
        </config>

        <institution>
          <config>
            <NullInst/>
          </config>
          <initialfacilitylist>
            <entry>
              <number>1</number>
              <prototype>sink</prototype>
            </entry>  
            <entry>
              <number>1</number>
              <prototype>source</prototype>
            </entry>             
          </initialfacilitylist>
          <name>sink_source_facilities</name>
        </institution>

        <institution>
            <config>
                <DemandDrivenDeploymentInst>
			<calc_method>fft</calc_method>
                    <facility_commod>
                        <item>
                            <facility>AdvancedReactor</facility>
                            <commod>POWER</commod>
                        </item>
                    </facility_commod>
                    <facility_capacity>
                        <item>
                            <facility>AdvancedReactor</facility>
                            <capacity>75</capacity>
                        </item>
                    </facility_capacity>
                    <driving_commod>POWER</driving_commod>
                    <demand_eq>np.heaviside(t-500,0.5)*300</demand_eq>
                    <record>1</record>
                    <steps>1</steps>
                    <back_steps>%s</back_steps>
                </DemandDrivenDeploymentInst>
            </config>
            <name>source_inst</name>
            </institution>

        <!--institution>
          <name>LWRDeployment</name>
          <config>
            <DeployInst>
              <prototypes>
                <val>LWR</val>
                <val>LWR</val>
                <val>LWR</val>
              </prototypes>
              <build_times>
                <val>1</val>
                <val>100</val>
                <val>200</val>
              </build_times>
              <n_build> 
                <val>1</val>
                <val>2</val>
                <val>1</val>
              </n_build>
            </DeployInst>
          </config>
        </institution-->

        <name>SingleRegion</name>
  </region>
    """%(step_size)

recipe = """
<recipe>
   <name>fresh_fuel_recipe</name>
   <basis>mass</basis>
   <nuclide> <id>U235</id> <comp>0.711</comp> </nuclide>
   <nuclide> <id>U238</id> <comp>99.289</comp> </nuclide>
</recipe>
 
<recipe>
   <name>spent_fuel_recipe</name>
   <basis>mass</basis>
   <nuclide> <id>Kr85</id> <comp>50</comp> </nuclide>
   <nuclide> <id>Cs137</id> <comp>50</comp> </nuclide>
</recipe>
 """


for step_size in step_sizes:
    input_file = file_base + step_size +'.xml'
    output_file = file_base + step_size +'.sqlite'

    with open(input_file, 'w') as f:
        f.write('<simulation>\n')
        f.write(control + archetypes)
        f.write(source + LWR + AR + sink)
        f.write(region[step_size])
        f.write(recipe)
        f.write('</simulation>')

    s = subprocess.check_output(['cyclus', '-o', output_file, input_file],
                            universal_newlines=True, env=ENV)
