from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import logging
import cgi
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -\
         %(levelname)s - %(message)s')

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hello!"
                output += "<form method='POST' enctype ='multipart/form-data'\
                action='/hello'><h2>What would you like me to say?</h2>\
                <input name='message' type='text'><input type='submit'\
                 value='Submit'></form>"
                output += "</body></html>"

                self.wfile.write(output)
                logging.info(output)
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hola <a href='/hello'>Back to Hello</a>"
                output += "<form method='POST' enctype ='multipart/form-data'\
                action='/hello'><h2>What would you like me to say?</h2>\
                <input name='message' type='text'><input type='submit'\
                 value='Submit'></form>"
                output += "</body></html>"

                self.wfile.write(output)
                logging.info(output)
                return

            if self.path.endswith('/restaurants'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>\
                Make a New Restaurant Here</a>"
                items = session.query(Restaurant).all()
                for item in items:
                    output += "<p>{}</p>".format(item.name)
                    output += "<a href='/restaurants/{}/edit'>Edit</a>\
                    ".format(item.id)
                    output += "</br>"
                    output += "<a href='/restaurants/{}/delete'>Delete</a>\
                    ".format(item.id)
                output += "</body></html>"
                logging.debug(output)
                self.wfile.write(output)
                return

            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<form method='POST' enctype ='multipart/form-data'\
                action='/restaurants/new'><h2>What would you name the Restaurant?</h2>\
                <input name='newresturant' type='text'><input type='submit'\
                 value='Submit'></form>"
                output += "</body></html>"
                logging.debug(output)
                self.wfile.write(output)
                return

            if self.path.endswith('/edit'):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant)\
                    .filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/{}/edit'>"\
                        .format(restaurantIDPath)
                    # output += "<input name='newRestaurantName'\
                    #  type='text' placeholder='{}''>"\
                    #  .format(myRestaurantQuery.name)
                    output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name

                    output += "<input type='submit' value='Rename'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    return

            if self.path.endswith('/delete'):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant)\
                    .filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += "Are you sure you want to delete this?"
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/{}/delete'>"\
                        .format(restaurantIDPath)
                    # output += "<input name='newRestaurantName'\
                    #  type='text' placeholder='{}''>"\
                    #  .format(myRestaurantQuery.name)
                    output += "<input type='submit' value='Delete'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                ctype, pdict = cgi.parse_header(self.headers.getheader(
                    'content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newresturant')
                new_restaurant = Restaurant(name=messagecontent[0])
                session.add(new_restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                return

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return
            # self.send_response(301)
            # self.end_headers()

            # logging.debug(self.headers.getheader('content-type'))
            # ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            # logging.debug(ctype)
            # logging.debug(pdict)
            # if ctype == 'multipart/form-data':
            #     fields = cgi.parse_multipart(self.rfile, pdict)
            #     logging.debug('Fields: %s' % fields)
            #     messagecontent = fields.get('message')

            #     output = ""
            #     output += "<html><body>"
            #     output += "<h2> Okay, how about this: </h2>"
            #     output += "<h1> %s </h1>" % messagecontent[0]

            #     output += "<form method='POST' enctype ='multipart/form-data'\
            #     action='/hello'><h2>What would you like me to say?</h2>\
            #     <input name='message' type='text'><input type='submit'\
            #      value='Submit'></form>"
            #     output += "</body></html>"
            #     self.wfile.write(output)
            #     logging.info(output)
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        logging.info('Web server running on port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
