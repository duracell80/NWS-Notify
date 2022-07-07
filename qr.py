import pyqrcode
import png
from pyqrcode import QRCode

url = "http://www.example.com"
qrl = pyqrcode.create(url)
irl = "/tmp/qr_" + url.replace("://", "-") + ".png"

qrl.png(irl, scale =8, module_color=[0, 0, 0, 255], background=[0xff, 0xff, 0xff])
