
from scrapy.http import HtmlResponse

import gtk
import webkit
import jswebkit
import time
from scrapy import log
from scrapy.selector import Selector
from webkit.webkit import LOAD_FINISHED, LOAD_FAILED
from functools import partial

class WebkitDownloader( object ):

#    def stop_gtk(self, v, f):
#        gtk.main_quit()

    def _get_webview(self):
        webview = webkit.WebView()
        props = webview.get_settings()
        props.set_property('enable-java-applet', False)
        props.set_property('enable-plugins', False)
        props.set_property('enable-page-cache', False)
        return webview

#    def _webview_get_html(self, webview):
#        webview.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
#        html = webview.get_main_frame().get_title()
#        webview.execute_script('document.title=oldtitle;')
#        return html

    def _webview_get_html(self, webview):
        ctx = jswebkit.JSContext(webview.get_main_frame().get_global_context())
        html = ctx.EvaluateScript('document.documentElement.innerHTML')
        return html


    def process_request( self, request, spider):
        if 'renderjs' in request.meta:
            webview = self._get_webview()
#            webview.connect('load-finished', self.stop_gtk)
            webview.load_uri(request.url)
            log.msg("gtk main")
            while True:
                st = webview.get_load_status()
                if st == LOAD_FINISHED:
                    break
                if st == LOAD_FAILED:
                    raise Exception("%s load fail" % (request.url))
                gtk.main_iteration(True)
            log.msg("gtk main done")
#            gtk.main()
            wait_dom_css_sels = request.meta.get("wait_dom_css_sels")
            if wait_dom_css_sels:
                while True:
                    html = self._webview_get_html(webview)
                    done = True
                    for sel in wait_dom_css_sels:
                        if not Selector(text=html).css(sel):
                            log.msg("waiting for ajax %s" % (sel))
                            gtk.main_iteration(True)
                            done = False
                            #time.sleep(1)
                            break
                    if not done:
                        continue
                    break

            log.msg("geting html")
            html = self._webview_get_html(webview) 
#            url = ctx.EvaluateScript('window.location.href')
            return HtmlResponse(request.url, encoding='utf-8', body=html.encode('utf-8'))
#            return HtmlResponse(url, encoding='utf-8', body=html.encode('utf-8'))

