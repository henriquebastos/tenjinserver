#! /usr/bin/env python

#--
# Copyright (c) 2009 Henrique Bastos, Vitor Mazzi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#++

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import os, sys
import mimetypes
from urllib2 import urlparse

import tenjin
import tenjin.helpers
import tenjin.helpers.html

_helpers = dict(tenjin.helpers.__dict__)
_helpers.update(tenjin.helpers.html.__dict__)

class TenjinHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(self.path)
            filename = "%s%s" % (os.getcwd(), path)
            prefix = None

            if path.endswith(".pyhtml"):   #our dynamic content
                query_dict = dict()
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
                _helpers.update(tenjin.helpers.html.__dict__)

                engine = tenjin.Engine(prefix=prefix, postfix='.pyhtml', 
                                       path=filename, cache=False, encoding='utf-8')
                content = engine.render(template_name, context, _helpers).encode('utf-8')
                content_type = 'text/html'

            else:
                content_type, content_encoding  = mimetypes.guess_type(filename)
                f = open(filename)
                content = f.read()
                f.close()

            self.send_response(200)
            self.send_header('Content-type',	content_type)
            self.end_headers()
            self.wfile.write(content)
            return

        except IOError:
            #raise
            self.send_error(404,'File Not Found: %s' % path)
     
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

