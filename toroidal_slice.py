import trame.app

import trame.widgets.vuetify3 as v3
import trame.widgets.html as html
import trame.widgets.matplotlib
import trame.widgets

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors

import fusionsc as fsc
from fusionsc.devices import w7x

import mpld3

import io
import base64

import asyncio

matplotlib.use("Agg")
from fusionsc.devices import w7x


class SliceManager:
    def __init__(self, server, configManager, taskManager):
        self.server = server
        
        self.configManager = configManager
        self.taskManager = taskManager
        self.lcfsPlots = {}
        self.pcPlots = {}
        self.clPlots = {}
        
        self.downAt = None
    
    def setupUI(self, layout):
        self.layout = layout
        
        # Due to lots of redraws required, the UI for this needs to be mostly rebuilt
        state = self.server.state
        
        state.angles = [0]
        state.pcPoints = []
        state.clRegions = []
        state.turnLimit = 5000
        
        state.figureClickX = 0
        state.figureClickY = 0
        
        state.pixelsPerM = 100
        state.dpi = 125
        
        state.rMin = 0
        state.rMax = 0
        state.zMin = 0
        state.zMax = 0
        
        state.pcColor = "clen"
        state.pointSize = 1
        
        @state.change("angles", "turnLimit")
        def anglesChanged(**kwargs):
            self.lcfsPlots = {}
            self.pcPlots = {}
        
        @state.change("pcPoints")
        def pointsChanged(**kwargs):
            self.pcPlots = {}
            
        v3.VLabel("Angles {{ angles }}")
        
        with v3.VContainer(fluid = True):
            with v3.VRow():
                with v3.VCol():
                    with v3.VCard(outline = True, title = "PC points"):
                        with v3.VCardText():
                            with v3.VTable():
                                with html.Thead():
                                    with html.Tr():
                                        html.Td("Phi")
                                        html.Td("R")
                                        html.Td("Z")
                                        html.Td("--")
                                
                                with html.Tr(v_for = "(x, index) in pcPoints"):
                                    html.Td("{{ x[0] }}")
                                    html.Td("{{ x[1] }}")
                                    html.Td("{{ x[2] }}")
                                    
                                    with html.Td():
                                        v3.VBtn("x", click = "pcPoints.splice(index, 1); flushState('pcPoints');")
                                
                                with html.Tr():
                                    with html.Td():
                                        v3.VTextField(v_model = ("newPhi", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newR", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newZ", 0))
                                        
                                    with html.Td():
                                        def addNew():
                                            state.pcPoints.append([
                                                float(state.newPhi), float(state.newR), float(state.newZ)
                                            ])
                                            state.dirty("pcPoints")
                                            
                                        v3.VBtn("+", click = addNew)
        
            with v3.VRow():
                with v3.VCol():
                    with v3.VCard(outline = True, title = "Angles"):
                        with v3.VCardText():
                            with v3.VTable():
                                with html.Thead():
                                    with html.Tr():
                                        html.Td("Phi")
                                        html.Td("--")
                                
                                with html.Tr(v_for = "(x, index) in angles"):
                                    html.Td("{{ x }}")
                                    
                                    with html.Td():
                                        v3.VBtn("x", click = "angles.splice(index, 1); flushState('angles');")
                                
                                with html.Tr():
                                    with html.Td():
                                        v3.VTextField(v_model = ("newAngle", 0))
                                        
                                    with html.Td():
                                        def addNew():
                                            state.angles.append(float(state.newAngle))
                                            state.dirty("angles")
                                            
                                        v3.VBtn("+", click = addNew)
                                    
            with v3.VRow():
                with v3.VCol():
                    with v3.VCard(outline = True, title = "CL regions"):
                        with v3.VCardText():
                            with v3.VTable():
                                with html.Thead():
                                    with html.Tr():
                                        html.Td("Phi")
                                        html.Td("R1")
                                        html.Td("R2")
                                        html.Td("Z1")
                                        html.Td("Z2")
                                        html.Td("nR")
                                        html.Td("nZ")
                                        html.Td("--")
                                
                                with html.Tr(v_for = "(x, index) in clRegions"):
                                    html.Td("{{ x[0] }}")
                                    html.Td("{{ x[1] }}")
                                    html.Td("{{ x[2] }}")
                                    html.Td("{{ x[3] }}")
                                    html.Td("{{ x[4] }}")
                                    html.Td("{{ x[5] }}")
                                    html.Td("{{ x[6] }}")
                                    
                                    with html.Td():
                                        v3.VBtn("x", click = "clRegions.splice(index, 1); flushState('clRegions');")
                                
                                with html.Tr():
                                    with html.Td():
                                        v3.VTextField(v_model = ("newPhi", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newR1", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newR2", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newZ1", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newZ2", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newNR", 0))
                                    with html.Td():
                                        v3.VTextField(v_model = ("newNZ", 0))
                                        
                                    with html.Td():
                                        def addNew():
                                            state.clRegions.append([
                                                float(state.newPhi), float(state.newR1), float(state.newR2),
                                                float(state.newZ1), float(state.newZ2), float(state.newNR),
                                                float(state.newNZ)
                                            ])
                                            state.dirty("clRegions")
                                            
                                        v3.VBtn("+", click = addNew)
            with v3.VRow():
                with v3.VCol():
                    with v3.VCard(outline = True, title = "CL regions"):
                        with v3.VCardText():
                            v3.VTextField("Pixel density for con.len. (px/m):", v_model_number = "pixelsPerM")
                            v3.VTextField("Figure dpi:", v_model_number = "dpi")
                            v3.VTextField("Poincare turn limit:", v_model_number = "turnLimit")
                            v3.VTextField("Z min:", v_model = "zMin")
                            v3.VTextField("Z max:", v_model = "zMax")
                            v3.VTextField("R min:", v_model = "rMin")
                            v3.VTextField("R max:", v_model = "rMax")
                            
                            with v3.VRadioGroup(v_model = "pcColor"):
                                v3.VRadio(label = "Color points by connection length", value = "clen")
                                v3.VRadio(label = "Color points black", value = "black")
                            v3.VTextField("Point size:", v_model = "pointSize")
                            
                            html.H3("Click on points to define new Poincare surfaces. Use Alt + Drag to define Connection-length regions")
                            v3.VBtn("Calculate...", click = self.recalculate)
                            v3.VBtn("Update...", click = self.updateUI)
        
        with v3.VCard(outline = True, title = "Plots"):
            self.plotRoot = v3.VCardText("... plots ...")
        
        controller = self.server.controller

    def recalculate(self):
        state = self.server.state
        taskManager = self.taskManager
        
        angles = [float(x) for x in self.server.state.angles]
        
        for configName in self.lcfsPlots:
            if configName not in state.allConfigs:
                del self.lcfsPlots[configName]
        
        for configName in self.pcPlots:
            if configName not in state.allConfigs:
                del self.pcPlots[configName]
        
        for configName in self.clPlots:            
            regions = {tuple(k) for k in state.clRegions}
            
            toDelete = [
                k
                for k in self.clPlots[configName]
                if not k in regions
            ]
            
            print("Deleting", toDelete)
            
            for k in toDelete:
                del self.clPlots[configName][k]
                
        for configName in state.allConfigs:
            config = self.configManager.configs[configName]
            
            if config is None:
                continue
            
            if configName not in self.lcfsPlots:
                lcfsTrace = taskManager.addTask("LCFS trace", fsc.flt.poincareInPhiPlanes.asnc(
                    config.lcfs, config.config,
                    np.radians(angles), state.turnLimit,
                    
                    geometry = config.geometry,
                    mapping = config.mapping,
                    
                    stepSize = 13, distanceLimit = 0
                ))
                
                self.lcfsPlots[configName] = lcfsTrace
                lcfsTrace.add_done_callback(self.whenDone)
            
            if configName not in self.pcPlots and len(state.pcPoints) > 0:
                print("Poincare: ", configName)
                phi, r, z = np.asarray(state.pcPoints, dtype = np.float64).T
                x = np.cos(np.radians(phi)) * r
                y = np.sin(np.radians(phi)) * r
                
                pcTrace = taskManager.addTask("Poincare trace", fsc.flt.poincareInPhiPlanes.asnc(
                    [x, y, z], config.config,
                    np.radians(angles), state.turnLimit,
                    
                    geometry = config.geometry,
                    mapping = config.mapping,
                    
                    stepSize = 13, distanceLimit = 0
                ))
                
                self.pcPlots[configName] = pcTrace
                pcTrace.add_done_callback(self.whenDone)
            
            if configName not in self.clPlots:
                self.clPlots[configName] = {}
            
            for r in state.clRegions:
                r = tuple(r)
                
                print(self.clPlots[configName].keys())
                print(r)
                print(r in self.clPlots[configName])
                
                if r in self.clPlots[configName]:
                    continue
                
                phi, r1, r2, z1, z2, nR, nZ = r
                
                print("CLen", configName, r)
                
                rVals = np.linspace(r1, r2, nR)
                zVals = np.linspace(z1, z2, nZ)
                
                rVals, zVals = np.meshgrid(rVals, zVals, indexing = "ij")
                
                phi = np.radians(phi)
                
                async def trace(d, config, phi, rVals, zVals):
                    traces = await fsc.flt.connectionLength.asnc([rVals * np.cos(phi), rVals * np.sin(phi), zVals], config.config, config.geometry, stepSize = 13, distanceLimit = 1e3, mapping = config.mapping, direction = d)
                    return traces
                
                async def traceBoth(*args):
                    fwd, bwd = await asyncio.gather(trace("forward", *args), trace("backward", *args))
                    return fwd + bwd
                
                t = self.taskManager.addTask("Trace connection length", traceBoth(config, phi, rVals, zVals))
                self.clPlots[configName][r] = t
                t.add_done_callback(self.whenDone)
        
        self.updateUI()
    
    def whenDone(self, *args, **kwargs):
        self.updateUI()
         
    def updateUI(self):
        state = self.server.state
        
        self.plotRoot.clear()
        
        with self.plotRoot:
            with v3.VContainer():
                for angleIdx, angle in enumerate(state.angles):
                    """with html.Thead():
                        with html.Tr():
                            html.Td(f"{angle}", colspan = len(state.allConfigs))
                        with html.Tr():
                            for configName in state.allConfigs:
                                html.Td(f"<h1>{configName}</h1>")"""
                    
                    with v3.VRow():
                        for configName in state.allConfigs:
                            with v3.VCol():
                                config = self.configManager.configs.get(configName, None)
                                if config is None:
                                    continue
                                
                                self.makePlot(configName, config, angleIdx, angle)
        
        with self.layout:
            self.layout.flush_content()
                        
    def makePlot(self, configName, config, angleIdx, angle):
        state = self.server.state
        
        rMin = float(state.rMin)
        rMax = float(state.rMax)
        zMin = float(state.zMin)
        zMax = float(state.zMax)
        
        w = 4
        h = 7
        
        if rMin != rMax and zMin != zMax:
            h = 4 * abs((zMax - zMin) / (rMax - rMin)) + 2
            
        dpi = float(self.server.state.dpi)
        fig = plt.figure(figsize = (w, h), dpi = dpi)
        
        norm = matplotlib.colors.LogNorm(vmin = 0.01, vmax = 2000)
        
        cb = None
        
        ps = float(state.pointSize)
        
        if configName in self.lcfsPlots and self.lcfsPlots[configName].done():
            x, y, z = self.lcfsPlots[configName].result()[:3, angleIdx, :]
            r = np.sqrt(x**2 + y**2)
            
            plt.scatter(r, z, c = 'r', s = ps, marker = '.')
        
        if configName in self.pcPlots and self.pcPlots[configName].done():
            x, y, z, cLenF, cLenB = self.pcPlots[configName].result()[:, angleIdx, ...].reshape([5, -1])
            r = np.sqrt(x**2 + y**2)
            
            if state.pcColor == "clen":
                mask = np.logical_and(cLenF > 0, cLenB > 0)
                mask2 = np.logical_and(cLenF < 0, cLenB < 0)
                
                cLen = cLenF + cLenB
                
                plt.scatter(r[mask], z[mask], c = cLen[mask], norm = norm, s = ps, marker = '.')
                
                if cb is None:
                    cb = plt.colorbar(label = 'Connection length [m]')
                plt.scatter(r[mask2], z[mask2], c = 'k', s = ps, marker = '.')
            else:
                plt.scatter(r, z, c = 'k', s = ps, marker = '.')
                
        if configName in self.clPlots:
            for (phi, r1, r2, z1, z2, nR, nZ), data in self.clPlots[configName].items():
                if phi != angle:
                    continue
                    
                if not data.done():
                    continue
                    
                
                plt.imshow(data.result().T, origin = "lower", extent = [r1, r2, z1, z2], norm = norm)
                
                if cb is None:
                    cb = plt.colorbar(label = 'Connection length [m]')
        
        plt.axis('equal')
        
        if rMin != rMax:
            plt.xlim(rMin, rMax)
        
        if zMin != zMax:
            plt.ylim(zMin, zMax) 
        
        plt.title(f"{configName} - {angle:.1f}")
        
        config.geometry.plotCut(np.radians(angle))
        
        bytesIo = io.BytesIO()
        plt.savefig(bytesIo, format = 'png', dpi = fig.dpi)
        bytesIo.seek(0)
        
        base64String = base64.b64encode(bytesIo.read()).decode("utf-8")
        srcString = f"data:image/jpeg;base64,{base64String}"
        
        transData = plt.gca().transData.inverted()
        
        def imgSpace(x, y):
            return transData.transform((x, dpi * h - y))
        
        def addPoints(x, y, altKey):
            if altKey:
                return
                
            r, z = imgSpace(x, y)
            
            self.server.state.pcPoints.extend([[angle + 72 * i, r, z] for i in range(0, 5)])
            self.server.state.dirty("pcPoints")
        
        def mouseDown(x, y, altKey):
            if not altKey:
                return
            
            self.downAt = (angle, x, y)
        
        def mouseUp(x2, y2, altKey):
            if not self.downAt:
                return
            
            phi1, x1, y1 = self.downAt
            self.downAt = None
            
            if not altKey or phi1 != angle:
                return
            
            r1, z1 = imgSpace(x1, y1)
            r2, z2 = imgSpace(x2, y2)
            
            rMin = min(r1, r2)
            rMax = max(r1, r2)
            
            zMin = min(z1, z2)
            zMax = max(z1, z2)
            
            state = self.server.state
            
            nR = int(abs(r2 - r1) * float(state.pixelsPerM))
            nZ = int(abs(z2 - z1) * float(state.pixelsPerM))
            
            state.clRegions.append([angle, rMin, rMax, zMin, zMax, nR, nZ])
            state.dirty("clRegions")
        
        img = v3.VImg(
            src = srcString,
            height=dpi * h, width = dpi * w,
            click = (addPoints, "[$event.offsetX, $event.offsetY, $event.altKey]"),
            mousedown = (mouseDown, "[$event.offsetX, $event.offsetY, $event.altKey]"),
            mouseup = (mouseUp, "[$event.offsetX, $event.offsetY, $event.altKey]"),
        )
        
        plt.close()