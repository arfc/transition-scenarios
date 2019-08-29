"""
Running this script generates .xml files and runs them producing the .sqlite
files for all the prediction methods.

The user can choose a demand equation (demand_eq) and a buffer size
(buff_size). The buffer plays its role one time step before the transition
starts. The transition starts at after 960 time steps (80 years).
"""

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

direc = os.listdir('./')

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')

calc_methods = ["ma", "arma", "arch", "poly", "exp_smoothing", "holt_winters",
                "fft", "sw_seasonal"]

demand_eq = "60000"
buff_size = "0"
# buff_size = sys.argv[1]

control = """
<control>
    <duration>1440</duration>
    <startmonth>1</startmonth>
    <startyear>2000</startyear>
    <decay>lazy</decay>
</control>

<archetypes>
        <spec>
            <lib>cycamore</lib>
            <name>Source</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Enrichment</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Reactor</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Storage</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Separations</name>
        </spec>
        <spec>
            <lib>cycamore</lib>
            <name>Mixer</name>
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
        <spec>
            <lib>d3ploy.supply_driven_deployment_inst</lib>
            <name>SupplyDrivenDeploymentInst</name>
        </spec>
</archetypes>

<facility>
    <name>source</name>
    <config>
        <Source>
            <outcommod>sourceout</outcommod>
            <outrecipe>sourceoutrecipe</outrecipe>
            <throughput>1e7</throughput>
        </Source>
    </config>
</facility>

<facility>
    <name>enrichment</name>
    <config>
        <Enrichment>
            <feed_commod>sourceout</feed_commod>
            <feed_recipe>sourceoutrecipe</feed_recipe>
            <product_commod>enrichmentout</product_commod>
            <tails_assay>0.0025</tails_assay>
            <tails_commod>enrichmentwaste</tails_commod>
            <swu_capacity>1e10</swu_capacity>
            <initial_feed>1e6</initial_feed>
            <max_feed_inventory>1e7</max_feed_inventory>
        </Enrichment>
    </config>
</facility>

<facility>
    <name>lwr</name>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr1</name>
    <lifetime>960</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr2</name>
    <lifetime>980</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr3</name>
    <lifetime>1000</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr4</name>
    <lifetime>1020</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr5</name>
    <lifetime>1040</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr6</name>
    <lifetime>1060</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr7</name>
    <lifetime>1080</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr8</name>
    <lifetime>1100</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr9</name>
    <lifetime>1120</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwr10</name>
    <lifetime>1140</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>lwrinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>lwroutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>enrichmentout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>lwrout</val>
            </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>29863.3</assem_size>
            <n_assem_core>3</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>fr</name>
    <lifetime>720</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes>
                <val>frinrecipe</val>
            </fuel_inrecipes>
            <fuel_outrecipes>
                <val>froutrecipe</val>
            </fuel_outrecipes>
            <fuel_incommods>
                <val>mixerout</val>
            </fuel_incommods>
            <fuel_outcommods>
                <val>frout</val>
            </fuel_outcommods>
            <cycle_time>12</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>5867</assem_size>
            <n_assem_core>4</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>333.34</power_cap>
        </Reactor>
    </config>
</facility>

<facility>
    <name>lwrstorage</name>
    <config>
        <Storage>
            <in_commods>
                <val>lwrout</val>
            </in_commods>
            <residence_time>36</residence_time>
            <out_commods>
                <val>lwrstorageout</val>
            </out_commods>
            <max_inv_size>1e7</max_inv_size>
        </Storage>
    </config>
</facility>

<facility>
    <name>frstorage</name>
    <config>
        <Storage>
            <in_commods>
                <val>frout</val>
            </in_commods>
            <residence_time>36</residence_time>
            <out_commods>
                <val>frstorageout</val>
            </out_commods>
            <max_inv_size>1e6</max_inv_size>
        </Storage>
    </config>
</facility>

<facility>
    <name>lwrreprocessing</name>
    <config>
        <Separations>
            <feed_commods>
                <val>lwrstorageout</val>
            </feed_commods>
            <feedbuf_size>1e6</feedbuf_size>
            <throughput>1e6</throughput>
            <leftover_commod>lwrreprocessingwaste</leftover_commod>
            <leftoverbuf_size>1e8</leftoverbuf_size>
            <streams>
                <item>
                    <commod>lwrtru</commod>
                    <info>
                        <buf_size>1e8</buf_size>
                        <efficiencies>
                              <item>
                                <comp>Np</comp>
                                <eff>1.0</eff>
                              </item>
                              <item>
                                <comp>Am</comp>
                                <eff>1.0</eff>
                              </item>
                              <item>
                                <comp>Cm</comp>
                                <eff>1.0</eff>
                              </item>
                              <item>
                                <comp>Pu</comp>
                                <eff>1.0</eff>
                              </item>
                        </efficiencies>
                    </info>
                </item>
                <item>
                    <commod>lwru</commod>
                    <info>
                        <buf_size>1e8</buf_size>
                        <efficiencies>
                            <item>
                                <comp>U</comp>
                                <eff>1.0</eff>
                            </item>
                        </efficiencies>
                    </info>
                </item>
            </streams>
        </Separations>
    </config>
</facility>

<facility>
    <name>frreprocessing</name>
    <config>
        <Separations>
            <feed_commods>
                <val>frstorageout</val>
            </feed_commods>
            <feedbuf_size>1e6</feedbuf_size>
            <throughput>1e6</throughput>
            <leftover_commod>frreprocessingwaste</leftover_commod>
            <leftoverbuf_size>1e8</leftoverbuf_size>
            <streams>
                <item>
                    <commod>frtru</commod>
                    <info>
                        <buf_size>1e8</buf_size>
                        <efficiencies>
                            <item>
                                <comp>Np</comp>
                                <eff>1.0</eff>
                            </item>
                            <item>
                                <comp>Am</comp>
                                <eff>1.0</eff>
                            </item>
                            <item>
                                <comp>Cm</comp>
                                <eff>1.0</eff>
                            </item>
                            <item>
                                <comp>Pu</comp>
                                <eff>1.0</eff>
                            </item>
                        </efficiencies>
                    </info>
                </item>
                <item>
                    <commod>fru</commod>
                    <info>
                        <buf_size>1e8</buf_size>
                        <efficiencies>
                            <item>
                                <comp>U</comp>
                                <eff>1.0</eff>
                            </item>
                        </efficiencies>
                    </info>
                </item>
            </streams>
        </Separations>
    </config>
</facility>

<facility>
    <name>lwrmixer</name>
    <config>
        <Mixer>
            <in_streams>
                <stream>
                    <info>
                        <mixing_ratio>0.139</mixing_ratio>
                        <buf_size>1e6</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>lwrtru</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
                <stream>
                    <info>
                        <mixing_ratio>0.771</mixing_ratio>
                        <buf_size>1e7</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>lwru</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
                <stream>
                    <info>
                        <mixing_ratio>0.09</mixing_ratio>
                        <buf_size>1e7</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>sourceout</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
            </in_streams>
            <out_commod>mixerout</out_commod>
            <out_buf_size>1e10</out_buf_size>
            <throughput>1e7</throughput>
        </Mixer>
    </config>
</facility>

<facility>
    <name>frmixer</name>
    <config>
        <Mixer>
            <in_streams>
                <stream>
                    <info>
                        <mixing_ratio>0.139</mixing_ratio>
                        <buf_size>1e6</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>frtru</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
                <stream>
                    <info>
                        <mixing_ratio>0.771</mixing_ratio>
                        <buf_size>1e7</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>fru</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
                <stream>
                    <info>
                        <mixing_ratio>0.09</mixing_ratio>
                        <buf_size>1e7</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>sourceout</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
            </in_streams>
            <out_commod>mixerout</out_commod>
            <out_buf_size>1e10</out_buf_size>
            <throughput>1e7</throughput>
        </Mixer>
    </config>
</facility>

<facility>
    <name>lwrsink</name>
    <config>
        <Sink>
            <in_commods>
                <val>lwrreprocessingwaste</val>
            </in_commods>
            <max_inv_size>1e6</max_inv_size>
        </Sink>
    </config>
</facility>

<facility>
    <name>frsink</name>
    <config>
        <Sink>
            <in_commods>
                <val>frreprocessingwaste</val>
            </in_commods>
            <max_inv_size>1e6</max_inv_size>
        </Sink>
    </config>
</facility>
"""

recipes = """
<recipe>
    <name>sourceoutrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>U235</id> <comp>0.711</comp> </nuclide>
    <nuclide> <id>U238</id> <comp>99.289</comp> </nuclide>
</recipe>

<recipe>
    <name>lwrinrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>U234</id>  <comp>0.0002558883</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.0319885317</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.96775558</comp> </nuclide>
</recipe>

<recipe>
    <name>lwroutrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>He4</id>  <comp>9.47457840128509E-07</comp> </nuclide>
    <nuclide> <id>Ra226</id>  <comp>9.78856442957042E-14</comp> </nuclide>
    <nuclide> <id>Ra228</id>  <comp>2.75087759176098E-20</comp> </nuclide>
    <nuclide> <id>Pb206</id>  <comp>5.57475193532078E-18</comp> </nuclide>
    <nuclide> <id>Pb207</id>  <comp>1.68592497990149E-15</comp> </nuclide>
    <nuclide> <id>Pb208</id>  <comp>3.6888358546006E-12</comp> </nuclide>
    <nuclide> <id>Pb210</id>  <comp>3.02386544437848E-19</comp> </nuclide>
    <nuclide> <id>Th228</id>  <comp>8.47562285269577E-12</comp> </nuclide>
    <nuclide> <id>Th229</id>  <comp>2.72787861516683E-12</comp> </nuclide>
    <nuclide> <id>Th230</id>  <comp>2.6258831537493E-09</comp> </nuclide>
    <nuclide> <id>Th232</id>  <comp>4.17481422959E-10</comp> </nuclide>
    <nuclide> <id>Bi209</id>  <comp>6.60770597104927E-16</comp> </nuclide>
    <nuclide> <id>Ac227</id>  <comp>3.0968621961773E-14</comp> </nuclide>
    <nuclide> <id>Pa231</id>  <comp>9.24658854635179E-10</comp> </nuclide>
    <nuclide> <id>U232</id>  <comp>0.000000001</comp> </nuclide>
    <nuclide> <id>U233</id>  <comp>2.21390148606282E-09</comp> </nuclide>
    <nuclide> <id>U234</id>  <comp>0.0001718924</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.0076486597</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.0057057461</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.9208590237</comp> </nuclide>
    <nuclide> <id>Np237</id>  <comp>0.0006091729</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.000291487</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.0060657301</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.0029058707</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.0017579218</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.0008638616</comp> </nuclide>
    <nuclide> <id>Pu244</id>  <comp>2.86487251922763E-08</comp> </nuclide>
    <nuclide> <id>Am241</id>  <comp>6.44271331287386E-05</comp> </nuclide>
    <nuclide> <id>Am242m</id>  <comp>8.53362027193319E-07</comp> </nuclide>
    <nuclide> <id>Am243</id>  <comp>0.0001983912</comp> </nuclide>
    <nuclide> <id>Cm242</id>  <comp>2.58988475560194E-05</comp> </nuclide>
    <nuclide> <id>Cm243</id>  <comp>0.000000771</comp> </nuclide>
    <nuclide> <id>Cm244</id>  <comp>8.5616190260478E-05</comp> </nuclide>
    <nuclide> <id>Cm245</id>  <comp>5.72174539442251E-06</comp> </nuclide>
    <nuclide> <id>Cm246</id>  <comp>7.29567535786554E-07</comp> </nuclide>
    <nuclide> <id>Cm247</id>  <comp>0.00000001</comp> </nuclide>
    <nuclide> <id>Cm248</id>  <comp>7.69165773748653E-10</comp> </nuclide>
    <nuclide> <id>Cm250</id>  <comp>4.2808095130239E-18</comp> </nuclide>
    <nuclide> <id>Cf249</id>  <comp>1.64992658175413E-12</comp> </nuclide>
    <nuclide> <id>Cf250</id>  <comp>2.04190913935875E-12</comp> </nuclide>
    <nuclide> <id>Cf251</id>  <comp>9.86556100338561E-13</comp> </nuclide>
    <nuclide> <id>Cf252</id>  <comp>6.57970721693466E-13</comp> </nuclide>
    <nuclide> <id>H3</id>  <comp>8.58461800264195E-08</comp> </nuclide>
    <nuclide> <id>C14</id>  <comp>4.05781943561107E-11</comp> </nuclide>
    <nuclide> <id>Kr81</id>  <comp>4.21681236076192E-11</comp> </nuclide>
    <nuclide> <id>Kr85</id>  <comp>3.44484671160181E-05</comp> </nuclide>
    <nuclide> <id>Sr90</id>  <comp>0.0007880649</comp> </nuclide>
    <nuclide> <id>Tc99</id>  <comp>0.0011409492</comp> </nuclide>
    <nuclide> <id>I129</id>  <comp>0.0002731878</comp> </nuclide>
    <nuclide> <id>Cs134</id>  <comp>0.0002300898</comp> </nuclide>
    <nuclide> <id>Cs135</id>  <comp>0.0006596706</comp> </nuclide>
    <nuclide> <id>Cs137</id>  <comp>0.0018169192</comp> </nuclide>
    <nuclide> <id>H1</id>  <comp>0.0477938151</comp> </nuclide>
</recipe>

<recipe>
    <name>frinrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>He4</id>  <comp>8.12E-11</comp> </nuclide>
    <nuclide> <id>U232</id>  <comp>4.71E-09</comp> </nuclide>
    <nuclide> <id>U234</id>  <comp>0.0003</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.0004</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.0003</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.83</comp> </nuclide>
    <nuclide> <id>Np237</id>  <comp>0.0007</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.0022</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.0947</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.0518</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.0072</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.0057</comp> </nuclide>
    <nuclide> <id>Am241</id>  <comp>0.0031</comp> </nuclide>
    <nuclide> <id>Am242m</id>  <comp>0.0002</comp> </nuclide>
    <nuclide> <id>Am243</id>  <comp>0.0016</comp> </nuclide>
    <nuclide> <id>Cm242</id>  <comp>0.0000</comp> </nuclide>
    <nuclide> <id>Cm243</id>  <comp>0.0000</comp> </nuclide>
    <nuclide> <id>Cm244</id>  <comp>0.0011</comp> </nuclide>
    <nuclide> <id>Cm245</id>  <comp>0.0003</comp> </nuclide>
    <nuclide> <id>Cm246</id>  <comp>0.0001</comp> </nuclide>
</recipe>

<recipe>
    <name>froutrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>H1</id>  <comp>2.2488058046007715e-06</comp> </nuclide>
    <nuclide> <id>H2</id>  <comp>6.889405066117969e-07</comp> </nuclide>
    <nuclide> <id>H3</id>  <comp>9.22920301310143e-06</comp> </nuclide>
    <nuclide> <id>He3</id>  <comp>9.22920301310143e-06</comp> </nuclide>
    <nuclide> <id>He4</id>  <comp>0.00014233770844149392</comp> </nuclide>
    <nuclide> <id>Br85</id>  <comp>0.0004010153703579988</comp> </nuclide>
    <nuclide> <id>Kr82</id>  <comp>3.5746913078914e-07</comp> </nuclide>
    <nuclide> <id>Kr85</id>  <comp>8.969225463436604e-05</comp> </nuclide>
    <nuclide> <id>Kr85m</id>  <comp>0.0004010153703579988</comp> </nuclide>
    <nuclide> <id>Sr90</id>  <comp>0.0013200360084231696</comp> </nuclide>
    <nuclide> <id>Zr95</id>  <comp>0.003043037218826824</comp> </nuclide>
    <nuclide> <id>Nb94</id>  <comp>1.6573568791132852e-09</comp> </nuclide>
    <nuclide> <id>Nb95</id>  <comp>0.0030417373310784998</comp> </nuclide>
    <nuclide> <id>Nb95m</id>  <comp>3.288716003260088e-05</comp> </nuclide>
    <nuclide> <id>Mo94</id>  <comp>3.1197305959779486e-12</comp> </nuclide>
    <nuclide> <id>Mo96</id>  <comp>1.1049045860755233e-06</comp> </nuclide>
    <nuclide> <id>Mo99</id>  <comp>0.0037826733476232634</comp> </nuclide>
    <nuclide> <id>Tc99</id>  <comp>0.0037826733476232634</comp> </nuclide>
    <nuclide> <id>Ru103</id>  <comp>0.004283130130728059</comp> </nuclide>
    <nuclide> <id>Ru106</id>  <comp>0.00268426820028936</comp> </nuclide>
    <nuclide> <id>Rh106</id>  <comp>0.00268426820028936</comp> </nuclide>
    <nuclide> <id>Sn121m</id>  <comp>3.444702533058985e-06</comp> </nuclide>
    <nuclide> <id>Sb122</id>  <comp>9.94414127467971e-09</comp> </nuclide>
    <nuclide> <id>Sb124</id>  <comp>1.0009135662095918e-06</comp> </nuclide>
    <nuclide> <id>Sb125</id>  <comp>8.969225463436604e-05</comp> </nuclide>
    <nuclide> <id>Te132</id>  <comp>0.003197723860877397</comp> </nuclide>
    <nuclide> <id>I129</id>  <comp>0.0008514264751523151</comp> </nuclide>
    <nuclide> <id>I131</id>  <comp>0.0026582704453228774</comp> </nuclide>
    <nuclide> <id>I133</id>  <comp>0.004543107680392888</comp> </nuclide>
    <nuclide> <id>I135</id>  <comp>0.004055649774771334</comp> </nuclide>
    <nuclide> <id>Xe128</id>  <comp>1.6248596854051817e-09</comp> </nuclide>
    <nuclide> <id>Xe130</id>  <comp>1.5013703493143878e-06</comp> </nuclide>
    <nuclide> <id>Xe131m</id>  <comp>2.8857508012796026e-05</comp> </nuclide>
    <nuclide> <id>Xe133</id>  <comp>0.0045691054353593705</comp> </nuclide>
    <nuclide> <id>Xe133m</id>  <comp>0.0001449374839381422</comp> </nuclide>
    <nuclide> <id>Xe135</id>  <comp>0.004874579056215545</comp> </nuclide>
    <nuclide> <id>Xe135m</id>  <comp>0.001280389432099283</comp> </nuclide>
    <nuclide> <id>Cs134</id>  <comp>7.474354552863835e-07</comp> </nuclide>
    <nuclide> <id>Cs137</id>  <comp>0.004127143600929161</comp> </nuclide>
    <nuclide> <id>Ba140</id>  <comp>0.0034466523646814714</comp> </nuclide>
    <nuclide> <id>La140</id>  <comp>0.0034603011860388747</comp> </nuclide>
    <nuclide> <id>Ce141</id>  <comp>0.003256218809551984</comp> </nuclide>
    <nuclide> <id>Ce144</id>  <comp>0.0022774033350639027</comp> </nuclide>
    <nuclide> <id>Pr144</id>  <comp>0.0022780532789380644</comp> </nuclide>
    <nuclide> <id>Nd142</id>  <comp>1.6313591241468025e-09</comp> </nuclide>
    <nuclide> <id>Nd144</id>  <comp>0.0022780532789380644</comp> </nuclide>
    <nuclide> <id>Nd147</id>  <comp>0.0012537417332586383</comp> </nuclide>
    <nuclide> <id>Pm147</id>  <comp>0.0012537417332586383</comp> </nuclide>
    <nuclide> <id>Pm148</id>  <comp>7.799326489944873e-09</comp> </nuclide>
    <nuclide> <id>Pm148m</id>  <comp>1.8848372350700106e-08</comp> </nuclide>
    <nuclide> <id>Pm149</id>  <comp>0.0008286784395566425</comp> </nuclide>
    <nuclide> <id>Pm151</id>  <comp>0.0005173553238330098</comp> </nuclide>
    <nuclide> <id>Sm148</id>  <comp>2.5347811092320833e-08</comp> </nuclide>
    <nuclide> <id>Sm150</id>  <comp>3.3147137582265707e-06</comp> </nuclide>
    <nuclide> <id>Sm151</id>  <comp>0.000518005267707172</comp> </nuclide>
    <nuclide> <id>Sm153</id>  <comp>0.00025997754966482906</comp> </nuclide>
    <nuclide> <id>Eu151</id>  <comp>0.000518005267707172</comp> </nuclide>
    <nuclide> <id>Eu152</id>  <comp>3.119730595977948e-10</comp> </nuclide>
    <nuclide> <id>Eu154</id>  <comp>8.254287201858323e-08</comp> </nuclide>
    <nuclide> <id>Eu155</id>  <comp>0.00011114040248171444</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.001164798127359022</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.09908368059417465</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.03249349929635785</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.0036243096344423897</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.0018210459910484378</comp> </nuclide>
    <nuclide> <id>Pu244</id>  <comp>6.35661764e-09</comp> </nuclide>
    <nuclide> <id>U232</id>  <comp>7.648700297471588e-09</comp> </nuclide>
    <nuclide> <id>U233</id>  <comp>5.285846459910117e-09</comp> </nuclide>
    <nuclide> <id>U234</id>  <comp>0.000155564910542954</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.00019082224532527</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.000300080729799828</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.7726661792000105</comp> </nuclide>
</recipe>
"""

region = {}

for calc_method in calc_methods:
    region[calc_method] = """
    <region>
        <config>
            <NullRegion>
            </NullRegion>
        </config>

        <institution>
        <config>
        <DemandDrivenDeploymentInst>
            <calc_method>%s</calc_method>
            <demand_eq>%s</demand_eq>
            <installed_cap>1</installed_cap>
            <back_steps>2</back_steps>
            <facility_commod>
            <item>
              <facility>source</facility>
              <commod>sourceout</commod>
            </item>
            <item>
              <facility>enrichment</facility>
              <commod>enrichmentout</commod>
            </item>
            <item>
              <facility>fr</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr1</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr2</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr3</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr4</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr5</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr6</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr7</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr8</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr9</facility>
              <commod>POWER</commod>
            </item>
            <item>
              <facility>lwr10</facility>
              <commod>POWER</commod>
            </item>
            </facility_commod>
            <facility_capacity>
            <item>
              <facility>source</facility>
              <capacity>1e7</capacity>
            </item>
            <item>
              <facility>enrichment</facility>
              <capacity>1e7</capacity>
            </item>
            <item>
              <facility>fr</facility>
              <capacity>333.34</capacity>
            </item>
            <item>
              <facility>lwr1</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr2</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr3</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr4</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr5</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr6</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr7</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr8</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr9</facility>
              <capacity>1000</capacity>
            </item>
            <item>
              <facility>lwr10</facility>
              <capacity>1000</capacity>
            </item>
            </facility_capacity>
            <facility_pref>
            <item>
              <facility>fr</facility>
              <pref>(t-959)/np.abs(t-959)</pref>
            </item>
            <item>
              <facility>lwr1</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr2</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr3</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr4</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr5</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr6</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr7</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr8</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr9</facility>
              <pref>-1</pref>
            </item>
            <item>
              <facility>lwr10</facility>
              <pref>-1</pref>
            </item>
            </facility_pref>
            <buffer_type>
            <item>
              <commod>POWER</commod>
              <type>abs</type>
            </item>
            </buffer_type>
            <supply_buffer>
            <item>
              <commod>POWER</commod>
              <buffer>%s</buffer>
            </item>
            </supply_buffer>
        </DemandDrivenDeploymentInst>
        </config>
        <name>timeseriesinst</name>
        <initialfacilitylist>
        <entry>
          <number>6</number>
          <prototype>lwr1</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr2</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr3</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr4</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr5</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr6</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr7</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr8</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr9</prototype>
        </entry>
        <entry>
          <number>6</number>
          <prototype>lwr10</prototype>
        </entry>
        </initialfacilitylist>
        </institution>

        <institution>
        <config>
        <SupplyDrivenDeploymentInst>
            <calc_method>%s</calc_method>
            <back_steps>2</back_steps>
            <facility_commod>
            <item>
                <facility>lwrreprocessing</facility>
                <commod>lwrstorageout</commod>
            </item>
            <item>
                <facility>frreprocessing</facility>
                <commod>frstorageout</commod>
            </item>
            <item>
                <facility>lwrmixer</facility>
                <commod>lwrtru</commod>
            </item>
            <item>
                <facility>frmixer</facility>
                <commod>frtru</commod>
            </item>
            <item>
                <facility>lwrstorage</facility>
                <commod>lwrout</commod>
            </item>
            <item>
                <facility>frstorage</facility>
                <commod>frout</commod>
            </item>
            <item>
                <facility>lwrsink</facility>
                <commod>lwrreprocessingwaste</commod>
            </item>
            <item>
                <facility>frsink</facility>
                <commod>frreprocessingwaste</commod>
            </item>
            </facility_commod>
            <facility_capacity>
            <item>
                <facility>lwrreprocessing</facility>
                <capacity>1e6</capacity>
            </item>
            <item>
                <facility>frreprocessing</facility>
                <capacity>1e6</capacity>
            </item>
            <item>
                <facility>lwrmixer</facility>
                <capacity>1e6</capacity>
            </item>
            <item>
                <facility>frmixer</facility>
                <capacity>1e6</capacity>
            </item>
            <item>
                <facility>lwrstorage</facility>
                <capacity>1e7</capacity>
            </item>
            <item>
                <facility>frstorage</facility>
                <capacity>1e6</capacity>
            </item>
            <item>
                <facility>lwrsink</facility>
                <capacity>1e6</capacity>
            </item>
            <item>
                <facility>frsink</facility>
                <capacity>1e6</capacity>
            </item>
            </facility_capacity>
        </SupplyDrivenDeploymentInst>
        </config>
        <name>supplydrivendeploymentinst</name>
        </institution>

        <name>SingleRegion</name>
    </region>
    """ % (calc_method, demand_eq, buff_size, calc_method)

for calc_method in calc_methods:

    input_file = 'eg01-eg24-flatpower-d3ploy-buffer' + buff_size + '-' \
                + calc_method + '.xml'
    output_file = 'eg01-eg24-flatpower-d3ploy-buffer' + buff_size + '-' \
        + calc_method + '.sqlite'

    with open(input_file, 'w') as f:
        f.write('<simulation>\n')
        f.write(control)
        f.write(region[calc_method])
        f.write(recipes)
        f.write('</simulation>')

    s = subprocess.check_output(['cyclus', '-o', output_file, input_file],
                                universal_newlines=True, env=ENV)
