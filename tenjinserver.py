#! /usr/bin/env python

#--
# Authors: Henrique Bastos, Vitor Mazzi
#
# This code is free to be used under the terms of the MIT license
# http://www.opensource.org/licenses/mit-license.php
#++

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import os, sys
import mimetypes
from urllib2 import urlparse

import tenjin
import tenjin.helpers
import tenjin.helpers.html

_helpers = dict(tenjin.helpers.__dict__)
_helpers |= tenjin.helpers.html.__dict__

class TenjinHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(self.path)
            filename = f"{os.getcwd()}{path}"
            prefix = None

            if path.endswith(".pyhtml"):   #our dynamic content
                query_dict = {}
                if query:
                    query_dict = dict([item.split('=') for item in query.split('&') if not item.isspace()])

                template_name = filename.split('/')[-1]
                try:
                    prefix = query_dict['prefix']
                except KeyError:
                    pass

                try:
                    context_name = query_dict['context']
                    context_module = __import__(context_name)
                    reload(context_module)
                    context = context_module.__dict__
                except KeyError:
                    raise

                _helpers = dict(tenjin.helpers.__dict__)
                _helpers |= tenjin.helpers.html.__dict__

                engine = tenjin.Engine(prefix=prefix, postfix='.pyhtml', 
                                       path=filename, cache=False, encoding='utf-8')
                content = engine.render(template_name, context, _helpers).encode('utf-8')
                content_type = 'text/html'

            else:
                content_type, content_encoding  = mimetypes.guess_type(filename)
                with open(filename) as f:
                    content = f.read()
            self.send_response(200)
            self.send_header('Content-type',	content_type)
            self.end_headers()
            self.wfile.write(content)
            return

        except IOError:
            #raise
            self.send_error(404, f'File Not Found: {path}')
     
def main():
    port = 8080
    basedir = os.getcwd() 

    if len(sys.argv) == 3:
        basedir, port = sys.argv[1:]
    elif len(sys.argv) == 2:
        basedir = sys.argv[1]

    port = int(port)
    os.chdir(basedir)
    sys.path.append(os.getcwd())

    try:
        server = HTTPServer(('', port), TenjinHandler)
        print 'started tenjinserver (port %d, docroot: %s)' % (port, basedir)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    print "WARNING !!!\n this potentially makes every file on your computer readable by the internet \n"
    main()

