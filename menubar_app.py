import rumps
import sys

class AgentEminenceApp(rumps.App):
    def __init__(self):
        super(AgentEminenceApp, self).__init__(name="Agent Eminence", title="🤖 Eminence: Active")
        
        # You can add actions here
        self.menu = [
            rumps.MenuItem("Status: Analyzing Top 20 Stocks...", callback=None),
            None, # Separator
            rumps.MenuItem("Stop Agent", callback=self.stop_agent)
        ]

    def stop_agent(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    # rumps.debug_mode(True)
    app = AgentEminenceApp()
    app.run()
