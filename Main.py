from MCP.MouseController import MouseController
from MCP.WindowController import WindowController
from RunPodClient import RunPodClient

#client = RunPodClient()

#answer = client.send("What is 2 + 2?")
#print(answer)

#MouseController.mouseMove(0.5, 0.5, duration=1.0)
#MouseController.click(0.5, 0.5)
MouseController.scroll(0.5, 0.5, -1125)
WindowController.saveScreenshot("./screenshot.png")