#!/usr/bin/env python3
"""面板静态服务器：提供面板 HTML 文件，并在 /api/sub 做节点订阅的同源代理。

用法：
    python3 panel_server.py [端口，默认 8080]

- 静态文件：服务本脚本所在目录（node-panel.html、server-panel.html）。
- /api/sub：向 http://se5.nodaroo.fun:26295/sub 拉取订阅，成功返回 200 与
  订阅原文，失败返回 502。面板页用它测延迟、判在线（同源，无跨域问题）。
"""
import os
import sys
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

SUB_URL = "http://se5.nodaroo.fun:26295/sub"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/sub" or self.path.startswith("/api/sub?"):
            self._proxy_sub()
            return
        super().do_GET()

    def _proxy_sub(self):
        try:
            req = urllib.request.Request(SUB_URL, method="GET")
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            msg = ("node unreachable: %s" % e).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)
    handler = partial(Handler, directory=root)
    httpd = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print("panel server on 0.0.0.0:%d, root %s" % (port, root), flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
