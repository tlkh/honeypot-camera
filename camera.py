import tornado.ioloop
import tornado.web
import os
import time

import datetime
import math
from PIL import Image, ImageDraw, ImageEnhance

COMPANY_NAME = "ZYCRON"

class CameraImageProcessor():
    def __init__(self, in_filename, out_filename, cam_deg, width=640, height=480):
        self.size = (width, height)
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.cam_deg = cam_deg

    def get_crop_area(self, cam_deg):
        x_start = int(640/180 * cam_deg)
        x_end = int(640/180 * cam_deg) + 480
        return (x_start, 0, x_end, 480)

    def process(self, prefix, postfix):
        now = datetime.datetime.now()
        original = Image.open(self.in_filename)
        original = original.crop(self.get_crop_area(self.cam_deg))
        original = ImageEnhance.Brightness(original).enhance(
            self.getDaylightIntensity(now.hour))  # overwrite original
        watermark = Image.new("RGBA", original.size)
        waterdraw = ImageDraw.ImageDraw(watermark, "RGBA")
        waterdraw.text((4, 2), "%s @ %s -- %s" % (prefix, now, postfix))
        original.paste(watermark, None, watermark)
        original.save(self.out_filename, "JPEG")

    def getDaylightIntensity(self, hour):
        # D = [0; 24] and W = [0; 1]
        return 0.45 * math.sin(0.25 * hour + 4.5) + 0.5


cam_deg = 0
countup = True

class CameraHandler1(tornado.web.RequestHandler):
    BOUNDARY = '--boundarydonotcross'
    HEADERS = {
        'Cache-Control': 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0',
        'Connection': 'close',
        'Expires': 'Mon, 3 Jan 2000 12:34:56 GMT',
        'Pragma': 'no-cache'
    }

    def get(self):
        global cam_deg
        global countup

        for hk, hv in CameraHandler1.HEADERS.items():
            self.set_header(hk, hv)

        cip = CameraImageProcessor("img/raw_1.jpg", "img/camera1.jpg", cam_deg)
        cip.process("SWAT CAM1: "+COMPANY_NAME+" FM",
                    "(c) 2018 by "+COMPANY_NAME+" Pte Ltd")
					
        if (cam_deg <= 180 and countup == True):
            cam_deg += 10
            countup = True
            if cam_deg == 180:
                countup = False

        elif (cam_deg >=0 and countup == False):
            cam_deg -= 10
            countup = False
            if cam_deg == 0:
                countup = True

        img_filename = "img/camera1.jpg"
        for hk, hv in self.image_headers(img_filename).items():
            self.set_header(hk, hv)

        with open(img_filename, "rb") as f:
            self.write(f.read())

    def image_headers(self, filename):
        return {
            'X-Timestamp': int(time.time()),
            'Content-Length': os.path.getsize(filename),
            'Content-Type': 'image/jpeg',
        }

class CameraHandler2(tornado.web.RequestHandler):
    BOUNDARY = '--boundarydonotcross'
    HEADERS = {
        'Cache-Control': 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0',
        'Connection': 'close',
        'Expires': 'Mon, 3 Jan 2000 12:34:56 GMT',
        'Pragma': 'no-cache'
    }

    def get(self):
        global cam_deg
        global countup

        for hk, hv in CameraHandler2.HEADERS.items():
            self.set_header(hk, hv)

        cip = CameraImageProcessor("img/raw_2.jpg", "img/camera2.jpg", 180-cam_deg)
        cip.process("SWAT CAM2: "+COMPANY_NAME+" FM",
                    "(c) 2018 by "+COMPANY_NAME+" Pte Ltd")
					
        img_filename = "img/camera2.jpg"
        for hk, hv in self.image_headers(img_filename).items():
            self.set_header(hk, hv)

        with open(img_filename, "rb") as f:
            self.write(f.read())

    def image_headers(self, filename):
        return {
            'X-Timestamp': int(time.time()),
            'Content-Length': os.path.getsize(filename),
            'Content-Type': 'image/jpeg',
        }


class RootHandler(tornado.web.RequestHandler):
    settings = {
        'title': COMPANY_NAME+" Facility Management",
        'refresh': 1,
    }

    def get(self):
        return self.render("templates/index.html", page=RootHandler.settings)


application = tornado.web.Application([
    (r'/camera1.jpg', CameraHandler1),
	(r'/camera2.jpg', CameraHandler2),
    (r'/', RootHandler),
    (r'/(favicon\.ico)', tornado.web.StaticFileHandler,
     {'path': 'static/'}),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
])

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
