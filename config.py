import matplotlib as mp
import matplotlib.pyplot as pv

import pyvista as pv
import trame.widgets.vuetify3 as v3
import trame.widgets.html as html

import fusionsc as fsc
from fusionsc.devices import w7x

import asyncio

class Config:
    def __init__(self, config, geometry):
        self.config = config.compute(w7x.defaultGrid())
        self.geometry = geometry
    
    async def init(self, taskManager):
        # Compute a mapping
        self.mapping = await taskManager.addTask("Compute field line mapping", w7x.computeMapping(self.config, toroidalSymmetry = 5).mapGeometry.asnc(self.geometry.triangulate(0.05), toroidalSymmetry = 5, nU = 100, nV = 100, nPhi = 16))
    
        # Find LCFS
        pInside = [5.5, 0, 0]
        pOutside = [6.5, 0, 0]
        
        self.lcfs = await taskManager.addTask("Compute LCFS", fsc.flt.findLCFS.asnc(self.config, self.geometry, pOutside, pInside, stepSize = 13, mapping = self.mapping))
        
        self.lcfsTrace = None
        self.poincareTrace = None
        

class ConfigManager:
    def __init__(self, server, geometryManager, taskManager):
        self.server = server
        self.geometryManager = geometryManager
        self.taskManager = taskManager
        
        self.configs = {}
    
    def updateUI(self):
        with self.server.state:
            self.server.state.allConfigs = list(self.configs)
        
    def setupUI(self):
        state = self.server.state
        
        # Prepare state
        state.mainConfigs = {"Standard" : [15000] * 5 + [0] * 2}
        state.controlCoilCurrents = [[0,0]]
        state.plasmaCurrents = [0]
        
        state.allConfigs = []
        
        with v3.VContainer():
            with v3.VRow():
                with v3.VCol():
                    with v3.VCard(otitle = "Main configurations", classes = "ga-3", fluid = True):
                        with v3.VCardText():
                            # Create UI elements
                            with v3.VTable():
                                with html.Thead():
                                    with html.Tr():
                                        html.Td("Configuration");
                                        html.Td("I1")
                                        html.Td("I2")
                                        html.Td("I3")
                                        html.Td("I4")
                                        html.Td("I5")
                                        html.Td("IA")
                                        html.Td("IB")
                                        html.Td("--")
                                        
                                with html.Tr():
                                    with html.Td():
                                        v3.VTextField("Name: ", v_model = ("newName", "<Unnamed>"))
                                    
                                    for x in ["1", "2", "3", "4", "5", "A", "B"]:
                                        with html.Td():
                                            v3.VTextField(f"I{x}: ", v_model = (f"newI{x}", 0))
                                    
                                    def addNew():
                                        state.mainConfigs[state.newName] = [
                                            int(x)
                                            for x in [state.newI1, state.newI2, state.newI3, state.newI4, state.newI5, state.newIA, state.newIB]
                                        ]
                                        state.dirty("mainConfigs")
                                        
                                    with html.Td():
                                        v3.VBtn("+", click = addNew)
                                        
                                with html.Tr(v_for = "name in Object.keys(mainConfigs)"):
                                    html.Td("{{ name }}");
                                    html.Td("{{ mainConfigs[name][0] }}")
                                    html.Td("{{ mainConfigs[name][1] }}")
                                    html.Td("{{ mainConfigs[name][2] }}")
                                    html.Td("{{ mainConfigs[name][3] }}")
                                    html.Td("{{ mainConfigs[name][4] }}")
                                    html.Td("{{ mainConfigs[name][5] }}")
                                    html.Td("{{ mainConfigs[name][6] }}")
                                    
                                    with html.Td():
                                        v3.VBtn("x", click = "delete mainConfigs[name]; flushState('mainConfigs');")
        
        with v3.VRow():
            with v3.VCol():
                with v3.VCard(title = "Control currents"):
                    with v3.VCardText():
                        with v3.VTable():
                            with html.Thead():
                                with html.Tr():
                                    html.Td("Icc 1")
                                    html.Td("Icc 2")
                                    html.Td("--")
                            
                            with html.Tr():
                                with html.Td():
                                    v3.VTextField("Icc1: ", v_model = ("newIcc1", 0))
                                with html.Td():
                                    v3.VTextField("Icc1: ", v_model = ("newIcc2", 0))
                                
                                with html.Td():
                                    def addNew():
                                        state.controlCoilCurrents.append([
                                            int(state.newIcc1), int(state.newIcc2)
                                        ])
                                        state.dirty("controlCoilCurrents")
                                        
                                    v3.VBtn("+", click = addNew)
                            
                            with html.Tr(v_for = "(x, index) in controlCoilCurrents"):
                                html.Td("{{ x[0] }}")
                                html.Td("{{ x[1] }}")
                                
                                with html.Td():
                                    v3.VBtn("x", click = "controlCoilCurrents.splice(index, 1); flushState('controlCoilCurrents');")
    
            with v3.VCol():
                with v3.VCard(title = "Plasma currents"):
                    with v3.VCardText():
                        with v3.VTable():
                            with html.Thead():
                                with html.Tr():
                                    html.Td("Iplasma")
                                    html.Td("--")
                            
                            with html.Tr():
                                with html.Td():
                                    v3.VTextField("Ip: ", v_model = ("newIp", 0))
                                
                                with html.Td():
                                    def addNew():
                                        state.plasmaCurrents.append(int(state.newIp))
                                        state.dirty("plasmaCurrents")
                                        
                                    v3.VBtn("+", click = addNew)
                            
                            with html.Tr(v_for = "(x, index) in plasmaCurrents"):
                                html.Td("{{ x }}")
                                
                                with html.Td():
                                    v3.VBtn("x", click = "plasmaCurrents.splice(index, 1); flushState('plasmaCurrents');")
        
        with v3.VRow():
            with v3.VCol():
                with v3.VCard(title = "Active configurations"):
                    with v3.VCardText():
                        v3.VBtn("Generate matrix", click = self.addMatrix)
                        v3.VBtn("Clear generated", click = self.clear)
                        with v3.VTable():
                            with html.Thead():
                                    with html.Tr():
                                        html.Td("Name")
                            
                            with html.Tr(v_for = "config in allConfigs"):
                                html.Td("{{ config }}")
        
    def addMatrix(self):
        state = self.server.state
        
        
        baseGeoName = state.activeGeometry
        baseGeo = self.geometryManager.geometries[baseGeoName]
        
        schedulesConfigs = ()
        
        for baseName, (i1, i2, i3, i4, i5, iA, iB) in state.mainConfigs.items():
            baseConfig = w7x.mainField([i1, i2, i3, i4, i5], [iA, iB])
            baseConfig = baseConfig.compute(w7x.defaultGrid())
            
            for icc1, icc2 in state.controlCoilCurrents:
                configWithCC = baseConfig + w7x.controlCoils([icc1, icc2])
                configWithCC = configWithCC.compute(w7x.defaultGrid())
                
                for iPlasma in state.plasmaCurrents:
                    name = f"{baseName}; Icc: {icc1}, {icc2}; Ip: {iPlasma}"
                    
                    async def addMe(name, configWithCC, iPlasma):
                        config = configWithCC + await self.taskManager.addTask("Compute base & Icc", w7x.axisCurrent.asnc(configWithCC, iPlasma)) if iPlasma != 0 else configWithCC
                        
                        newConfig = Config(config, baseGeo)
                        await newConfig.init(self.taskManager)
                                                
                        self.configs[name] = newConfig
                        self.updateUI()
                    
                    self.taskManager.addTask(f"Initializing config {name}", addMe(name, configWithCC, iPlasma))
    
    def clear(self):
        self.configs = {}
        self.updateUI()
        
        import gc
        gc.collect()
        fsc.asnc.cycle()