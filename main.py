import trame.app

import geometry
import config
import toroidal_slice
import asyncio

import trame.widgets.vuetify3 as v3
import trame.widgets.html as html

class W7xConfigApp:
    def __init__(self, serverOrName = None):
        self.server = trame.app.get_server(serverOrName)
        
        self.taskManager = TaskManager(self.server)
        self.geometryManager = geometry.GeometryManager(self.server)
        self.configManager = config.ConfigManager(self.server, self.geometryManager, self.taskManager)
        self.sliceManager = toroidal_slice.SliceManager(self.server, self.configManager, self.taskManager)
        
        self.ui = self.setupUI()
        
        self.updateUI()
    
    def setupUI(self):
        from trame.ui.vuetify3 import SinglePageLayout
        import trame.widgets.vuetify3 as v3
        
        with SinglePageLayout(self.server) as layout:
            with layout.content:                
                with v3.VTabs(v_model = ("mainTab", "geo")):
                    v3.VTab(value = "geo", text = "Geometry")
                    v3.VTab(value = "config", text = "Configuration")
                    v3.VTab(value = "slice", text = "Toroidal Cross-sections")
                
                with v3.VTabsWindow(v_model = "mainTab", direction = "horizontal"):
                    with v3.VTabsWindowItem(value = "geo"):
                        self.geometryManager.setupUI()
                        
                    with v3.VTabsWindowItem(value = "config"):
                        self.configManager.setupUI()
                        
                    with v3.VTabsWindowItem(value = "slice"):
                        self.sliceManager.setupUI(layout)
                        
                self.taskManager.setupUI()
    
    def updateUI(self):
        self.geometryManager.updateUI()

class TaskManager:
    def __init__(self, server):
        self.server = server
        self.tasks = []
    
    def setupUI(self):
        state = self.server.state
        state.tasks = []
        
        with v3.VCard(title = "Running tasks"):
            with v3.VTable():
                with html.Thead():
                    with html.Tr(v_for = "task in tasks"):
                        html.Td("{{ task }}")
    
    def updateUI(self):
        self.tasks = [
            (name, t) for name, t in self.tasks
            if not t.done()
        ]
        
        state = self.server.state
        
        with state:
            state.tasks = [n for n, _ in self.tasks]
    
    def addTask(self, name, task):
        t = asyncio.create_task(task)
        
        def update(x):
            self.updateUI()
            
        t.add_done_callback(update)
        
        self.tasks.append((name, t))
        self.updateUI()
        
        return t
        

if __name__ == "__main__":
    app = W7xConfigApp()
    app.server.hot_reload = True
    app.server.start()