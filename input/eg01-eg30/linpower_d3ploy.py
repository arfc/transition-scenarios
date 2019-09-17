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

name = 'eg01-eg30-linpower-d3ploy-buffer'

demand_eq = "60000 + 250*t/12"
buff_size = "0"

thro_frmixer = 50e3
buffer_frTR = thro_frmixer / (1.0 + 0.8854 / 0.1146)
buffer_frU = (buffer_frTR * 0.8854 / 0.1146) * 1.05
thro_frmixer = str(thro_frmixer)
buffer_frTR = str(buffer_frTR)
buffer_frU = str(buffer_frU)

thro_moxmixer = 100e3
buffer_moxTR = thro_moxmixer / (1.0 + 0.896 / 0.104)
buffer_moxU = (buffer_moxTR * 0.896 / 0.104) * 1.05
thro_moxmixer = str(thro_moxmixer)
buffer_moxTR = str(buffer_moxTR)
buffer_moxU = str(buffer_moxU)

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
            <throughput>1e8</throughput>
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
            <swu_capacity>1e100</swu_capacity>
            <initial_feed>5e7</initial_feed>
        </Enrichment>
    </config>
</facility>
<facility>
    <name>lwr</name>
    <config>
        <Reactor>
            <fuel_inrecipes> <val>lwrinrecipe</val> </fuel_inrecipes>
            <fuel_outrecipes> <val>lwroutrecipe</val> </fuel_outrecipes>
            <fuel_incommods> <val>enrichmentout</val> </fuel_incommods>
            <fuel_outcommods> <val>lwrout</val> </fuel_outcommods>
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
    <name>fr</name>
    <lifetime>720</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes> <val>frinrecipe</val> </fuel_inrecipes>
            <fuel_outrecipes> <val>froutrecipe</val> </fuel_outrecipes>
            <fuel_incommods> <val>frmixerout</val> </fuel_incommods>
            <fuel_outcommods> <val>frout</val> </fuel_outcommods>
            <cycle_time>12</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>3950</assem_size>
            <n_assem_core>1</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>333.34</power_cap>
        </Reactor>
    </config>
</facility>
<facility>
    <name>moxlwr</name>
    <lifetime>960</lifetime>
    <config>
        <Reactor>
            <fuel_inrecipes> <val>moxinrecipe</val> </fuel_inrecipes>
            <fuel_outrecipes> <val>moxoutrecipe</val> </fuel_outrecipes>
            <fuel_incommods> <val>moxmixerout</val> </fuel_incommods>
            <fuel_outcommods> <val>moxout</val> </fuel_outcommods>
            <cycle_time>18</cycle_time>
            <refuel_time>0</refuel_time>
            <assem_size>33130</assem_size>
            <n_assem_core>1</n_assem_core>
            <n_assem_batch>1</n_assem_batch>
            <power_cap>1000</power_cap>
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
            <max_inv_size>1e8</max_inv_size>
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
            <max_inv_size>1e8</max_inv_size>
        </Storage>
    </config>
</facility>
<facility>
    <name>moxstorage</name>
    <config>
        <Storage>
            <in_commods>
                <val>moxout</val>
            </in_commods>
            <residence_time>36</residence_time>
            <out_commods>
                <val>moxstorageout</val>
            </out_commods>
            <max_inv_size>1e8</max_inv_size>
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
            <feedbuf_size>1e8</feedbuf_size>
            <throughput>1e8</throughput>
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
            <feedbuf_size>1e8</feedbuf_size>
            <throughput>1e8</throughput>
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
    <name>moxreprocessing</name>
    <config>
        <Separations>
            <feed_commods>
                <val>moxstorageout</val>
            </feed_commods>
            <feedbuf_size>1e8</feedbuf_size>
            <throughput>1e8</throughput>
            <leftover_commod>moxreprocessingwaste</leftover_commod>
            <leftoverbuf_size>1e8</leftoverbuf_size>
            <streams>
                <item>
                    <commod>moxtru</commod>
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
                    <commod>moxu</commod>
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
    <name>frmixer</name>
    <config>
        <Mixer>
            <in_streams>
                <stream>
                    <info>
                        <mixing_ratio>0.1146</mixing_ratio>
                        <buf_size>%s</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>lwrtru</commodity>
                            <pref>3.0</pref>
                        </item>
                        <item>
                            <commodity>frtru</commodity>
                            <pref>2.0</pref>
                        </item>
                        <item>
                            <commodity>moxtru</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
                <stream>
                    <info>
                        <mixing_ratio>0.8854</mixing_ratio>
                        <buf_size>%s</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>lwru</commodity>
                            <pref>3.0</pref>
                        </item>
                        <item>
                            <commodity>fru</commodity>
                            <pref>2.0</pref>
                        </item>
                        <item>
                            <commodity>moxu</commodity>
                            <pref>1.0</pref>
                        </item>
                        <item>
                            <commodity>tailings</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
            </in_streams>
            <out_commod>frmixerout</out_commod>
            <out_buf_size>%s</out_buf_size>
            <throughput>%s</throughput>
        </Mixer>
    </config>
</facility>
<facility>
    <name>moxmixer</name>
    <config>
        <Mixer>
            <in_streams>
                <stream>
                    <info>
                        <mixing_ratio>0.104</mixing_ratio>
                        <buf_size>%s</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>lwrtru</commodity>
                            <pref>3.0</pref>
                        </item>
                        <item>
                            <commodity>frtru</commodity>
                            <pref>1.0</pref>
                        </item>
                        <item>
                            <commodity>moxtru</commodity>
                            <pref>2.0</pref>
                        </item>
                    </commodities>
                </stream>
                <stream>
                    <info>
                        <mixing_ratio>0.896</mixing_ratio>
                        <buf_size>%s</buf_size>
                    </info>
                    <commodities>
                        <item>
                            <commodity>lwru</commodity>
                            <pref>3.0</pref>
                        </item>
                        <item>
                            <commodity>fru</commodity>
                            <pref>1.0</pref>
                        </item>
                        <item>
                            <commodity>moxu</commodity>
                            <pref>2.0</pref>
                        </item>
                        <item>
                            <commodity>tailings</commodity>
                            <pref>1.0</pref>
                        </item>
                    </commodities>
                </stream>
            </in_streams>
            <out_commod>moxmixerout</out_commod>
            <out_buf_size>%s</out_buf_size>
            <throughput>%s</throughput>
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
            <max_inv_size>1e20</max_inv_size>
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
            <max_inv_size>1e20</max_inv_size>
        </Sink>
    </config>
</facility>
<facility>
    <name>moxsink</name>
    <config>
        <Sink>
            <in_commods>
                <val>moxreprocessingwaste</val>
            </in_commods>
            <max_inv_size>1e20</max_inv_size>
        </Sink>
    </config>
</facility>
""" % (buffer_frTR, buffer_frU, thro_frmixer, thro_frmixer,
       buffer_moxTR, buffer_moxU, thro_moxmixer, thro_moxmixer)

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
    <nuclide> <id>H1</id>  <comp>1.8902589607549852e-06</comp> </nuclide>
    <nuclide> <id>H2</id>  <comp>5.790966758382324e-07</comp> </nuclide>
    <nuclide> <id>H3</id>  <comp>7.757710185757454e-06</comp> </nuclide>
    <nuclide> <id>He3</id>  <comp>7.757710185757454e-06</comp> </nuclide>
    <nuclide> <id>He4</id>  <comp>0.00011964355849865369</comp> </nuclide>
    <nuclide> <id>Br85</id>  <comp>0.00033707797074734847</comp> </nuclide>
    <nuclide> <id>Kr82</id>  <comp>3.004746902934225e-07</comp> </nuclide>
    <nuclide> <id>Kr85</id>  <comp>7.539183138271328e-05</comp> </nuclide>
    <nuclide> <id>Kr85m</id>  <comp>0.00033707797074734847</comp> </nuclide>
    <nuclide> <id>Sr90</id>  <comp>0.001109571083610802</comp> </nuclide>
    <nuclide> <id>Zr95</id>  <comp>0.0025578590908250983</comp> </nuclide>
    <nuclide> <id>Nb94</id>  <comp>1.3931099277240498e-09</comp> </nuclide>
    <nuclide> <id>Nb95</id>  <comp>0.0025567664555876677</comp> </nuclide>
    <nuclide> <id>Nb95m</id>  <comp>2.7643671506994872e-05</comp> </nuclide>
    <nuclide> <id>Mo94</id>  <comp>2.6223245698335053e-12</comp> </nuclide>
    <nuclide> <id>Mo96</id>  <comp>9.287399518160331e-07</comp> </nuclide>
    <nuclide> <id>Mo99</id>  <comp>0.0031795685409231255</comp> </nuclide>
    <nuclide> <id>Tc99</id>  <comp>0.0031795685409231255</comp> </nuclide>
    <nuclide> <id>Ru103</id>  <comp>0.003600233107333917</comp> </nuclide>
    <nuclide> <id>Ru106</id>  <comp>0.002256291765294245</comp> </nuclide>
    <nuclide> <id>Rh106</id>  <comp>0.002256291765294245</comp> </nuclide>
    <nuclide> <id>Sn121m</id>  <comp>2.8954833791911622e-06</comp> </nuclide>
    <nuclide> <id>Sb122</id>  <comp>8.358659566344297e-09</comp> </nuclide>
    <nuclide> <id>Sb124</id>  <comp>8.41329132821583e-07</comp> </nuclide>
    <nuclide> <id>Sb125</id>  <comp>7.539183138271328e-05</comp> </nuclide>
    <nuclide> <id>Te132</id>  <comp>0.002687882684079343</comp> </nuclide>
    <nuclide> <id>I129</id>  <comp>0.0007156760805170608</comp> </nuclide>
    <nuclide> <id>I131</id>  <comp>0.0022344390605456327</comp> </nuclide>
    <nuclide> <id>I133</id>  <comp>0.0038187601548200422</comp> </nuclide>
    <nuclide> <id>I135</id>  <comp>0.003409021940783557</comp> </nuclide>
    <nuclide> <id>Xe128</id>  <comp>1.365794046788284e-09</comp> </nuclide>
    <nuclide> <id>Xe130</id>  <comp>1.2619936992323744e-06</comp> </nuclide>
    <nuclide> <id>Xe131m</id>  <comp>2.4256502270959927e-05</comp> </nuclide>
    <nuclide> <id>Xe133</id>  <comp>0.0038406128595686547</comp> </nuclide>
    <nuclide> <id>Xe133m</id>  <comp>0.00012182882897351494</comp> </nuclide>
    <nuclide> <id>Xe135</id>  <comp>0.004097382140364852</comp> </nuclide>
    <nuclide> <id>Xe135m</id>  <comp>0.0010762457088691678</comp> </nuclide>
    <nuclide> <id>Cs134</id>  <comp>6.282652615226107e-07</comp> </nuclide>
    <nuclide> <id>Cs137</id>  <comp>0.0034691168788422416</comp> </nuclide>
    <nuclide> <id>Ba140</id>  <comp>0.0028971223320473083</comp> </nuclide>
    <nuclide> <id>La140</id>  <comp>0.00290859500204033</comp> </nuclide>
    <nuclide> <id>Ce141</id>  <comp>0.0027370512697637212</comp> </nuclide>
    <nuclide> <id>Ce144</id>  <comp>0.001914296935978459</comp> </nuclide>
    <nuclide> <id>Pr144</id>  <comp>0.0019148432535971744</comp> </nuclide>
    <nuclide> <id>Nd142</id>  <comp>1.3712572229754374e-09</comp> </nuclide>
    <nuclide> <id>Nd144</id>  <comp>0.0019148432535971744</comp> </nuclide>
    <nuclide> <id>Nd147</id>  <comp>0.0010538466865018402</comp> </nuclide>
    <nuclide> <id>Pm147</id>  <comp>0.0010538466865018402</comp> </nuclide>
    <nuclide> <id>Pm148</id>  <comp>6.5558114245837635e-09</comp> </nuclide>
    <nuclide> <id>Pm148m</id>  <comp>1.5843210942744093e-08</comp> </nuclide>
    <nuclide> <id>Pm149</id>  <comp>0.0006965549638620248</comp> </nuclide>
    <nuclide> <id>Pm151</id>  <comp>0.0004348688244973896</comp> </nuclide>
    <nuclide> <id>Sm148</id>  <comp>2.1306387129897234e-08</comp> </nuclide>
    <nuclide> <id>Sm150</id>  <comp>2.7862198554480997e-06</comp> </nuclide>
    <nuclide> <id>Sm151</id>  <comp>0.000435415142116105</comp> </nuclide>
    <nuclide> <id>Sm153</id>  <comp>0.00021852704748612548</comp> </nuclide>
    <nuclide> <id>Eu151</id>  <comp>0.000435415142116105</comp> </nuclide>
    <nuclide> <id>Eu152</id>  <comp>2.622324569833505e-10</comp> </nuclide>
    <nuclide> <id>Eu154</id>  <comp>6.938233757684484e-08</comp> </nuclide>
    <nuclide> <id>Eu155</id>  <comp>9.342031280031864e-05</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.0009592342315400002</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.08159736522620001</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.026759037549500004</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.0029846904673000003</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.00149966729066</comp> </nuclide>
    <nuclide> <id>Pu244</id>  <comp>5.234800000000001e-09</comp> </nuclide>
    <nuclide> <id>U232</id>  <comp>7.93244176110115e-09</comp> </nuclide>
    <nuclide> <id>U233</id>  <comp>5.4819338672768064e-09</comp> </nuclide>
    <nuclide> <id>U234</id>  <comp>0.00016133585380000002</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.00019790111900000001</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.00031121273160000004</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.8013295369022</comp> </nuclide>
    <nuclide> <id>Am241</id>  <comp>0.372034217349</comp> </nuclide>
    <nuclide> <id>Am242m</id>  <comp>0.02422538847</comp> </nuclide>
    <nuclide> <id>Am243</id>  <comp>0.10954349109900001</comp> </nuclide>
    <nuclide> <id>Cm242</id>  <comp>0.016223903343</comp> </nuclide>
    <nuclide> <id>Cm243</id>  <comp>0.000986552217</comp> </nuclide>
    <nuclide> <id>Cm244</id>  <comp>0.054130938228</comp> </nuclide>
    <nuclide> <id>Cm245</id>  <comp>0.011979036378</comp> </nuclide>
    <nuclide> <id>Cm246</id>  <comp>0.004365667044</comp> </nuclide>
    <nuclide> <id>Cm247</id>  <comp>0.000161795151</comp> </nuclide>
    <nuclide> <id>Cm248</id>  <comp>1.1562525796316895e-05</comp> </nuclide>
    <nuclide> <id>Cm250</id>  <comp>1.9498012888129913e-12</comp> </nuclide>
    <nuclide> <id>Cf249</id>  <comp>1.9616003888965777e-07</comp> </nuclide>
    <nuclide> <id>Cf250</id>  <comp>2.0397694269503573e-08</comp> </nuclide>
    <nuclide> <id>Cf251</id>  <comp>5.791883253531473e-10</comp> </nuclide>
    <nuclide> <id>Cf252</id>  <comp>1.2216493249045363e-11</comp> </nuclide>
    <nuclide> <id>Np237</id>  <comp>0.21633723097200003</comp> </nuclide>
</recipe>
<recipe>
    <name>moxinrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>U234</id>  <comp>0.0001387087</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.0041782621</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.003077193</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.5029315439</comp> </nuclide>
    <nuclide> <id>Np237</id>  <comp>0.0232914608</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.0115607251</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.2333146335</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.1104069247</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.0519432579</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.0323320279</comp> </nuclide>
    <nuclide> <id>Am241</id>  <comp>0.0165510381</comp> </nuclide>
    <nuclide> <id>Am242m</id>  <comp>2.97718672915165E-05</comp> </nuclide>
    <nuclide> <id>Am243</id>  <comp>0.0073874633</comp> </nuclide>
    <nuclide> <id>Cm243</id>  <comp>2.49115624531971E-05</comp> </nuclide>
    <nuclide> <id>Cm244</id>  <comp>0.0026211644</comp> </nuclide>
    <nuclide> <id>Cm245</id>  <comp>0.0002109132</comp> </nuclide>
</recipe>
<recipe>
    <name>moxoutrecipe</name>
    <basis>mass</basis>
    <nuclide> <id>H1</id>  <comp>1.6592893412427388e-06</comp> </nuclide>
    <nuclide> <id>H1</id>  <comp>1.6592893412427388e-06</comp> </nuclide>
    <nuclide> <id>H2</id>  <comp>5.490295614406121e-07</comp> </nuclide>
    <nuclide> <id>H3</id>  <comp>5.774977609227179e-06</comp> </nuclide>
    <nuclide> <id>He3</id>  <comp>5.774977609227179e-06</comp> </nuclide>
    <nuclide> <id>He4</id>  <comp>8.914613323539418e-05</comp> </nuclide>
    <nuclide> <id>Br85</id>  <comp>0.0002334392357532676</comp> </nuclide>
    <nuclide> <id>Kr82</id>  <comp>7.117049870526452e-07</comp> </nuclide>
    <nuclide> <id>Kr85</id>  <comp>5.530964470809129e-05</comp> </nuclide>
    <nuclide> <id>Kr85m</id>  <comp>0.0002342526128813278</comp> </nuclide>
    <nuclide> <id>Sr90</id>  <comp>0.000818664079392557</comp> </nuclide>
    <nuclide> <id>Zr95</id>  <comp>0.0020127017033848807</comp> </nuclide>
    <nuclide> <id>Nb94</id>  <comp>6.832367875705393e-09</comp> </nuclide>
    <nuclide> <id>Nb95</id>  <comp>0.0020114816376927904</comp> </nuclide>
    <nuclide> <id>Nb95m</id>  <comp>2.175783817560944e-05</comp> </nuclide>
    <nuclide> <id>Mo94</id>  <comp>1.4640788305082986e-11</comp> </nuclide>
    <nuclide> <id>Mo96</id>  <comp>2.0741116765534236e-06</comp> </nuclide>
    <nuclide> <id>Mo99</id>  <comp>0.002515368768526063</comp> </nuclide>
    <nuclide> <id>Tc99</id>  <comp>0.002514962079962033</comp> </nuclide>
    <nuclide> <id>Ru103</id>  <comp>0.002825672142881017</comp> </nuclide>
    <nuclide> <id>Ru106</id>  <comp>0.0017032117061579876</comp> </nuclide>
    <nuclide> <id>Rh106</id>  <comp>0.0017032117061579876</comp> </nuclide>
    <nuclide> <id>Sn121m</id>  <comp>2.1147805329564317e-06</comp> </nuclide>
    <nuclide> <id>Sb122</id>  <comp>9.760525536721992e-09</comp> </nuclide>
    <nuclide> <id>Sb124</id>  <comp>9.272499259885892e-07</comp> </nuclide>
    <nuclide> <id>Sb125</id>  <comp>4.758256199151971e-05</comp> </nuclide>
    <nuclide> <id>Te132</id>  <comp>0.002072078233733273</comp> </nuclide>
    <nuclide> <id>I129</id>  <comp>0.0005722108095903268</comp> </nuclide>
    <nuclide> <id>I131</id>  <comp>0.0015145082124480291</comp> </nuclide>
    <nuclide> <id>I133</id>  <comp>0.002834619291289678</comp> </nuclide>
    <nuclide> <id>I135</id>  <comp>0.0025743386103104253</comp> </nuclide>
    <nuclide> <id>Xe128</id>  <comp>9.516512398303943e-10</comp> </nuclide>
    <nuclide> <id>Xe130</id>  <comp>6.751030162899378e-07</comp> </nuclide>
    <nuclide> <id>Xe131m</id>  <comp>1.647088684321836e-05</comp> </nuclide>
    <nuclide> <id>Xe133</id>  <comp>0.0028427530625702805</comp> </nuclide>
    <nuclide> <id>Xe133m</id>  <comp>8.784472983049792e-05</comp> </nuclide>
    <nuclide> <id>Xe135</id>  <comp>0.002993227831261411</comp> </nuclide>
    <nuclide> <id>Xe135m</id>  <comp>0.0007239056439735477</comp> </nuclide>
    <nuclide> <id>Cs134</id>  <comp>2.724813379001556e-07</comp> </nuclide>
    <nuclide> <id>Cs137</id>  <comp>0.0026792642598301867</comp> </nuclide>
    <nuclide> <id>Ba140</id>  <comp>0.0021643965377681016</comp> </nuclide>
    <nuclide> <id>La140</id>  <comp>0.0021688701119724325</comp> </nuclide>
    <nuclide> <id>Ce141</id>  <comp>0.002116813975776582</comp> </nuclide>
    <nuclide> <id>Ce144</id>  <comp>0.0015271155579329617</comp> </nuclide>
    <nuclide> <id>Pr144</id>  <comp>0.0015275222464969918</comp> </nuclide>
    <nuclide> <id>Nd142</id>  <comp>5.896984178436203e-10</comp> </nuclide>
    <nuclide> <id>Nd144</id>  <comp>0.0015275222464969918</comp> </nuclide>
    <nuclide> <id>Nd147</id>  <comp>0.0008312714248774897</comp> </nuclide>
    <nuclide> <id>Pm147</id>  <comp>0.0008312714248774897</comp> </nuclide>
    <nuclide> <id>Pm148</id>  <comp>2.2774559585684646e-09</comp> </nuclide>
    <nuclide> <id>Pm148m</id>  <comp>4.798925055554979e-09</comp> </nuclide>
    <nuclide> <id>Pm149</id>  <comp>0.0005136476563699948</comp> </nuclide>
    <nuclide> <id>Pm151</id>  <comp>0.0003155903256873444</comp> </nuclide>
    <nuclide> <id>Sm148</id>  <comp>6.832367875705393e-09</comp> </nuclide>
    <nuclide> <id>Sm150</id>  <comp>9.231830403482883e-07</comp> </nuclide>
    <nuclide> <id>Sm151</id>  <comp>0.0003155903256873444</comp> </nuclide>
    <nuclide> <id>Sm153</id>  <comp>0.00015454165433143155</comp> </nuclide>
    <nuclide> <id>Eu151</id>  <comp>0.0003155903256873444</comp> </nuclide>
    <nuclide> <id>Eu152</id>  <comp>7.93042699858662e-11</comp> </nuclide>
    <nuclide> <id>Eu154</id>  <comp>1.9927739637474066e-08</comp> </nuclide>
    <nuclide> <id>Eu155</id>  <comp>7.076381014123444e-05</comp> </nuclide>
    <nuclide> <id>Pu238</id>  <comp>0.0044566634772000005</comp> </nuclide>
    <nuclide> <id>Pu239</id>  <comp>0.03025956446406</comp> </nuclide>
    <nuclide> <id>Pu240</id>  <comp>0.020955172652820004</comp> </nuclide>
    <nuclide> <id>Pu241</id>  <comp>0.010839136847400002</comp> </nuclide>
    <nuclide> <id>Pu242</id>  <comp>0.00728930104722</comp> </nuclide>
    <nuclide> <id>Pu244</id>  <comp>1.61517158245631e-07</comp> </nuclide>
    <nuclide> <id>U232</id>  <comp>6.073368072739612e-10</comp> </nuclide>
    <nuclide> <id>U233</id>  <comp>1.0603318711422634e-08</comp> </nuclide>
    <nuclide> <id>U234</id>  <comp>0.00027194035646</comp> </nuclide>
    <nuclide> <id>U235</id>  <comp>0.00444193081428</comp> </nuclide>
    <nuclide> <id>U236</id>  <comp>0.005230015263780001</comp> </nuclide>
    <nuclide> <id>U238</id>  <comp>0.84785610241408</comp> </nuclide>
    <nuclide> <id>Am241</id>  <comp>0.16971099736</comp> </nuclide>
    <nuclide> <id>Am242m</id>  <comp>0.00401628096</comp> </nuclide>
    <nuclide> <id>Am243</id>  <comp>0.1661221824</comp> </nuclide>
    <nuclide> <id>Cm242</id>  <comp>0.02195556216</comp> </nuclide>
    <nuclide> <id>Cm243</id>  <comp>0.00100805784</comp> </nuclide>
    <nuclide> <id>Cm244</id>  <comp>0.08118693216</comp> </nuclide>
    <nuclide> <id>Cm245</id>  <comp>0.010176278</comp> </nuclide>
    <nuclide> <id>Cm246</id>  <comp>0.0004897534400000001</comp> </nuclide>
    <nuclide> <id>Cm247</id>  <comp>9.618019982286001e-06</comp> </nuclide>
    <nuclide> <id>Cm248</id>  <comp>7.304431593512233e-07</comp> </nuclide>
    <nuclide> <id>Cm250</id>  <comp>2.97791762967296e-15</comp> </nuclide>
    <nuclide> <id>Cf249</id>  <comp>3.2000000000000005e-09</comp> </nuclide>
    <nuclide> <id>Cf250</id>  <comp>2.339108839804712e-09</comp> </nuclide>
    <nuclide> <id>Cf251</id>  <comp>1.154800409150096e-09</comp> </nuclide>
    <nuclide> <id>Cf252</id>  <comp>6.009268703691961e-10</comp> </nuclide>
    <nuclide> <id>Np237</id>  <comp>0.34532360008</comp> </nuclide>
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
        <steps>1</steps>
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
          <facility>moxlwr</facility>
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
          <facility>frmixer</facility>
          <commod>frmixerout</commod>
        </item>
        <item>
          <facility>moxmixer</facility>
          <commod>moxmixerout</commod>
        </item>
        </facility_commod>
        <facility_capacity>
        <item>
          <facility>source</facility>
          <capacity>1e8</capacity>
        </item>
        <item>
          <facility>enrichment</facility>
          <capacity>1e100</capacity>
        </item>
        <item>
          <facility>fr</facility>
          <capacity>333.34</capacity>
        </item>
        <item>
          <facility>moxlwr</facility>
          <capacity>1000</capacity>
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
          <facility>frmixer</facility>
          <capacity>%s</capacity>
        </item>
        <item>
          <facility>moxmixer</facility>
          <capacity>%s</capacity>
        </item>
        </facility_capacity>
        <facility_pref>
        <item>
          <facility>fr</facility>
          <pref>(t-959)/np.abs(t-959)</pref>
        </item>
        <item>
          <facility>moxlwr</facility>
          <pref>(t-959)/np.abs(t-959)</pref>
        </item>
        <item>
          <facility>lwr1</facility>
          <pref>(959-t)/np.abs(t-959)</pref>
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
        </facility_pref>
        <facility_sharing>
        <item>
            <facility>fr</facility>
            <percentage>85</percentage>
        </item>
        <item>
            <facility>moxlwr</facility>
            <percentage>15</percentage>
        </item>
        </facility_sharing>
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
      <number>10</number>
      <prototype>lwr1</prototype>
    </entry>
    <entry>
      <number>10</number>
      <prototype>lwr2</prototype>
    </entry>
    <entry>
      <number>10</number>
      <prototype>lwr3</prototype>
    </entry>
    <entry>
      <number>10</number>
      <prototype>lwr4</prototype>
    </entry>
    <entry>
      <number>10</number>
      <prototype>lwr5</prototype>
    </entry>
    <entry>
      <number>10</number>
      <prototype>lwr6</prototype>
    </entry>
    </initialfacilitylist>
    </institution>
    <institution>
    <config>

    <SupplyDrivenDeploymentInst>
        <calc_method>%s</calc_method>
        <steps>1</steps>
        <back_steps>2</back_steps>
        <facility_commod>
        <item>
            <facility>lwrstorage</facility>
            <commod>lwrout</commod>
        </item>
        <item>
            <facility>frstorage</facility>
            <commod>frout</commod>
        </item>
        <item>
            <facility>moxstorage</facility>
            <commod>moxout</commod>
        </item>
        <item>
            <facility>lwrreprocessing</facility>
            <commod>lwrstorageout</commod>
        </item>
        <item>
            <facility>frreprocessing</facility>
            <commod>frstorageout</commod>
        </item>
        <item>
            <facility>moxreprocessing</facility>
            <commod>moxstorageout</commod>
        </item>
        <item>
            <facility>lwrsink</facility>
            <commod>lwrreprocessingwaste</commod>
        </item>
        <item>
            <facility>frsink</facility>
            <commod>frreprocessingwaste</commod>
        </item>
        <item>
            <facility>moxsink</facility>
            <commod>moxreprocessingwaste</commod>
        </item>
        </facility_commod>
        <facility_capacity>
        <item>
            <facility>lwrstorage</facility>
            <capacity>1e8</capacity>
        </item>
        <item>
            <facility>frstorage</facility>
            <capacity>1e8</capacity>
        </item>
        <item>
            <facility>moxstorage</facility>
            <capacity>1e8</capacity>
        </item>
            <item>
            <facility>lwrreprocessing</facility>
            <capacity>1e8</capacity>
        </item>
        <item>
            <facility>frreprocessing</facility>
            <capacity>1e8</capacity>
        </item>
        <item>
            <facility>moxreprocessing</facility>
            <capacity>1e8</capacity>
        </item>
        <item>
            <facility>lwrsink</facility>
            <capacity>1e20</capacity>
        </item>
        <item>
            <facility>frsink</facility>
            <capacity>1e20</capacity>
        </item>
        <item>
            <facility>moxsink</facility>
            <capacity>1e20</capacity>
        </item>
        </facility_capacity>
    </SupplyDrivenDeploymentInst>
    </config>
    <name>supplydrivendeploymentinst</name>
    </institution>
    <name>SingleRegion</name>
    </region>""" % (calc_method, demand_eq, thro_frmixer, thro_moxmixer,
                    buff_size, calc_method)

for calc_method in calc_methods:

    input_file = name + buff_size + '-' + calc_method + '.xml'
    output_file = name + buff_size + '-' + calc_method + '.sqlite'

    with open(input_file, 'w') as f:
        f.write('<simulation>\n')
        f.write(control)
        f.write(region[calc_method])
        f.write(recipes)
        f.write('</simulation>')

    s = subprocess.check_output(['cyclus', '-o', output_file, input_file],
                                universal_newlines=True, env=ENV)
