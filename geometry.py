import trame.app

import trame.widgets.vuetify3 as v3
import pyvista as pv

# Always set PyVista to plot off screen with Trame
pv.OFF_SCREEN = True

from fusionsc.devices import w7x

class GeometryManager:
    def __init__(self, server):
        self.server = server
        self.geometries = {
            "Divertor" : w7x.divertor().index(w7x.defaultGeometryGrid()),
            "W7X" : w7x.op21Geometry().index(w7x.defaultGeometryGrid()),
        }
        self.plotter = pv.Plotter()
    
    def setupUI(self):
        # Initialize UI state
        state = self.server.state
        
        state.geometries = []
        state.activeGeometry = ""
        
        # Setup UI
        with v3.VRadioGroup(v_model = "activeGeometry"):
            v3.VRadio(v_for = "geoName in geometries", label = ("geoName",), value = ("geoName",))
        
        with v3.VResponsive(aspect_ratio = ("4/3",), width = "80%"):
            pv.trame.ui.plotter_ui(self.plotter)
        
        # Register state change listener
        state.change("activeGeometry")(self.drawGeometry)
        
        
    def updateUI(self):
        state = self.server.state
        
        # Update geometry list
        state.geometries = list(self.geometries)
        
        if state.activeGeometry not in state.geometries:
            state.activeGeometry = state.geometries[0] if state.geometries else ""
    
    def drawGeometry(self, activeGeometry, **kwargs):
        self.plotter.clear()
        
        # TODO: REMOVE THIS
        return
                
        if activeGeometry in self.geometries:
            self.plotter.add_mesh(self.geometries[activeGeometry].asPyvista())