from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import requests
import json
import os

Window.size = (900, 600)
Window.clearcolor = (.05,0,.8,1)

KV = '''

<ReqBox>
    size_hint: 1, None
    size: -1, 40


BoxLayout:
    orientation: 'vertical'
    BoxLayout: #top bar
        size_hint: (1, .07)
        BoxLayout: #base url setter
            pos_hint: {'top': .95}
            orientation: 'horizontal'
            TextInput:
                id: ti_burl
                size_hint: (.8, 1)
                font_size: 25
                padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
                multiline: False
                hint_text: "Base Url Address"
                foreground_color: (1, 0.1, 0, 1)
            Button:
                size_hint: (.2, 1)
                text: 'Set Base Url'
                id: bt_burl
    BoxLayout: #center (main content)
        size_hint: (1, .93)
        orientation: 'horizontal'
        BoxLayout: #left (request history)
            size_hint: (.3, 1)
            orientation: 'vertical'
            ScrollView:
                size_hint: (1, .95)
                do_scroll_x: False

                GridLayout:
                    cols: 1
                    padding: 10
                    spacing: 10
                    size_hint_y: None
                    height: self.minimum_height
                    id: gl_reqhist

                
                        
        BoxLayout: #right (current request)
            size_hint: (.7, 1)
            orientation: 'vertical'
            BoxLayout:
                size_hint: (1, .06)
                orientation: 'horizontal'
                Spinner:
                    size_hint: (.15, 1)
                    id: sp_reqmth
                    text: 'GET'
                    values: 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'
                TextInput:
                    size_hint: (.65, 1)
                    id: ti_url
                    font_size: 21
                    padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
                    multiline: False
                    hint_text: "Base Url Address"
                    foreground_color: (.1, 1, 0, 1)
                Button:
                    id: bt_sendrqst
                    size_hint: (.1, 1)
                    text: "Send"
                Button:
                    id: bt_saverqst
                    size_hint: (.1, 1)
                    text: "Save"
            BoxLayout:
                size_hint: (1, 0.47)
                TabbedPanel:
                    size_hint: (1, 1)
                    do_default_tab: False
                    TabbedPanelItem:
                        text: 'Headers'
                        BoxLayout:
                            size_hint: (1, 1)
                            TextInput:
                                id: ti_reqh
                                hint_text: "Request Headers"
                                foreground_color: (0, 0, 1, 1)
                                font_size: 22
                                text: "{}"
                                   
                    TabbedPanelItem:
                        text: 'Data'
                        BoxLayout:
                            size_hint: (1, 1)
                            TextInput:
                                id: ti_reqd
                                hint_text: "Request Data"
                                foreground_color: (0, 0, 1, 1)
                                font_size: 22
                                text: "{}"
                    
                    TabbedPanelItem:
                        text: 'Cookies'
                        BoxLayout:
                            size_hint: (1, 1)
                            TextInput:
                                id: ti_reqc
                                hint_text: "Request Cookies"
                                foreground_color: (0, 0, 1, 1)
                                font_size: 22
                                text: "{}"
                        
                                
                            
                            
            BoxLayout:
                size_hint: (1, 0.47)
                orientation: 'vertical'
                BoxLayout:
                    size_hint: (1, 0.1)
                    orientation: 'horizontal'
                    Label:
                        id: lb_sts
                        text: 'Status:'
                        size_hint: (.5, 1)
                    Label:
                        id: lb_time
                        text: 'Time:'
                        size_hint: (.5, 1)
                TabbedPanel:
                    size_hint: (1, .9)
                    do_default_tab: False
                    TabbedPanelItem:
                        text: 'Headers'
                        BoxLayout:
                            size_hint: (1, 1)
                            TextInput:
                                id: ti_resh
                                hint_text: "Response Headers"
                                foreground_color: (0, 0, 1, 1)
                                font_size: 22
                                   
                    TabbedPanelItem:
                        text: 'Data'
                        BoxLayout:
                            size_hint: (1, 1)
                            TextInput:
                                id: ti_resd
                                hint_text: "Response Data"
                                foreground_color: (0, 0, 1, 1)
                                font_size: 22
                    TabbedPanelItem:
                        text: 'Cookies'
                        BoxLayout:
                            size_hint: (1, 1)
                            TextInput:
                                id: ti_resc
                                hint_text: "Response Cookies"
                                foreground_color: (0, 0, 1, 1)
                                font_size: 22
                


'''
class RButton(Button):
    def __init__(self, key,  **kwargs):
        self.key = key
        Button.__init__(self, **kwargs)

class ReqBox(BoxLayout):
    def __init__(self, key, text, onPressOp, onPressDel, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(RButton(key, text=text, on_press=onPressOp, size_hint=(0.85, 1)))
        self.add_widget(RButton(key, text='X', on_press=onPressDel, size_hint=(0.15, 1)))
    
class ReqTesterApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hist = dict()
    def on_start(self):
        self.root.ids.sp_reqmth.bind(text=self.onMethodChanged)
        self.root.ids.bt_burl.bind(on_press=self.onBaseUrlChanged)
        self.root.ids.bt_sendrqst.bind(on_press=self.sendRequest)
        self.root.ids.bt_saverqst.bind(on_press=self.saveRequest)
        self.title = "Request Tester"
        self.dbFile = ".reqtester"
        if os.path.isfile(os.getcwd()+"/{}".format(self.dbFile)):
            with open(self.dbFile) as json_file:
                data = json.load(json_file)
                self.hist.update(data)
        self._load_Hist()
    def on_stop(self):
        pass
    def on_pause(self):
        return True
    def on_resume(self):
        pass
    def build(self):
        self.req_method = 'GET'
        self.base_url = ''
        return Builder.load_string(KV)
    def loadHistory(self, item):
        try:
            req = self.hist[item.key]
            self.root.ids.ti_url.text = req["url"]
            self.root.ids.ti_burl.text = self.base_url = req["base_url"]
            self.root.ids.sp_reqmth.text = self.req_method = req["method"]
            self.root.ids.ti_reqd.text = req["data"]
            self.root.ids.ti_reqh.text = req["headers"]
            self.root.ids.ti_reqc.text = req["cookies"]
        except Exception as e:
            print("Oops!", e.__class__, "occurred.\n", str(e))
    def onMethodChanged(self, item, value):
        self.req_method = item.text
    def onBaseUrlChanged(self, item):
        self.base_url = self.root.ids.ti_burl.text
    def sendRequest(self, item):
        r = None
        headers = self.root.ids.ti_reqh.text
        data = self.root.ids.ti_reqd.text
        cookies = self.root.ids.ti_reqc.text
        url = self.base_url+self.root.ids.ti_url.text
        try:
            headers_ = json.loads(headers)
            data_ = json.loads(data)
            cookies_ = json.loads(cookies)
            if self.req_method == "GET":
                r = requests.get(url, json=data_, headers=headers_, cookies=cookies_)
            if self.req_method == "POST":
                r = requests.post(url, json=data_, headers=headers_, cookies=cookies_)
            if self.req_method == "PUT":
                r = requests.put(url, json=data_, headers=headers_, cookies=cookies_)
            if self.req_method == "PATCH":
                r = requests.patch(url, json=data_, headers=headers_, cookies=cookies_)
            if self.req_method == "DELETE":
                r = requests.delete(url, json=data_, headers=headers_, cookies=cookies_)
        except Exception as e:
            print("Oops(sendRequest)!", e.__class__, "occurred.\n", str(e))
            return
        print('\nMethod:  {}\nUrl:  {}\nData:  {}\nHeaders:  {}'.format(self.req_method, url, data, headers))
        self.root.ids.ti_resh.text = str(r.headers)
        self.root.ids.ti_resd.text = str(r.text)
        self.root.ids.ti_resc.text = str(r.cookies)
        self.root.ids.lb_sts.text = 'Status:  '+str(r.status_code)
    def deleteRequest(self, item):
        try:
            key = item.key
            if key in self.hist.keys():
                self.hist.pop(key)
        except Exception as e:
            print("Oops!", e.__class__, "occurred.\n", str(e)) 
        self._load_Hist()
    def saveRequest(self, item):
        url = self.root.ids.ti_url.text
        base_url = self.base_url
        method = self.req_method
        data = self.root.ids.ti_reqd.text
        headers = self.root.ids.ti_reqh.text
        cookies = self.root.ids.ti_reqc.text
        name = method+" "+base_url[:10]+url[:10]
        key = method+base_url+url
        if len(base_url+url) > 0:
            self.hist.update({
                key: {
                    "name":name,
                    "base_url": base_url,
                    "url": url,
                    "method": method,
                    "data": data,
                    "headers": headers,
                    "cookies": cookies
                }
            })
        with open(self.dbFile, 'w') as json_file:
            json.dump(self.hist, json_file)
        self._load_Hist()
    def _load_Hist(self):
        reqHistCont = self.root.ids.gl_reqhist
        reqHistCont.clear_widgets()
        for key in self.hist.keys():
            reqHistCont.add_widget(ReqBox(key, text=self.hist[key]['name'], onPressOp=self.loadHistory, onPressDel=self.deleteRequest))


if __name__ == '__main__':
        ReqTesterApp().run()