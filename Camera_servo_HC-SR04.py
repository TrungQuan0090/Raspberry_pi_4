from time import sleep, time

#--------UltraSonic setup
import RPi.GPIO as GPIO

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time()
    StopTime = time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
#------------------------------------    

#-------Camera setup
from picamera2 import Picamera2, Preview
from libcamera import Transform
picam2 = Picamera2()

#Xoay hình ảnh từ camera 180 độ theo chiều dọc
camera_config = picam2.create_preview_configuration(transform=Transform(vflip=True))

picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
#------------------------------------


#-------Servo setup
from adafruit_servokit import ServoKit
kit = ServoKit(channels=8)

def doc ():
    truc_Y=int(input("Nhap goc:"))
    
    kit.servo[4].angle = truc_Y
    if truc_Y < 0:
        truc_Y = 0
    if truc_Y > 180:
        truc_Y =180
    
def ngang ():
    truc_X = int(input("Nhap goc:"))
    
    kit.servo[7].angle = truc_X
    
    if truc_X > 180:
        truc_X =180
    if truc_X < 0:
        truc_X = 0
    buf=truc_X
#------------------------------------

#---------------OLED setup
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

RESET_PIN = digitalio.DigitalInOut(board.D4)
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.show()

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

#-----------------------------------------
global cmd		#Khởi tạo biến global
cmd = ""
while True:
    
    if(cmd==""):	#Lựa chọn thực hiện tác vụ nào
        cmd = input("Nhap: ")
    if(cmd == 'Y'):		#Điều khiển servo dọc
        doc()
        cmd=""
    if(cmd == 'X'):		#Điều khiển servo ngang
        ngang()
        cmd=""
    
    if(cmd == 'CAP'):	#Chụp ảnh, lưu vào file cap.jpg
        picam2.capture_file("cap.jpg")
        cmd=""
        
        #Sau khi chup hien thi len OLED
        image = (
            Image.open("cap.jpg")
            .resize((oled.width, oled.height), Image.BICUBIC)
            .convert("1")
        )
oled.image(image)
        oled.show()
        sleep(1)
    
    if(cmd == 'HOLD'):	#Bật sensor UltraSonic
        dist = distance()

   #Khi có vật cản trong khoảng dưới 10cm
   #Điều khiển servo cho camera hướng về phía UltraSonic và chụp hình vật cản
        if dist < 10:
            kit.servo[4].angle = 90
            kit.servo[7].angle = 20
            
            sleep(0.7)
            picam2.capture_file("sensor.jpg")
            
            #Sau khi chup hien thi len OLED
            image = (
                Image.open("sensor.jpg")
                .resize((oled.width, oled.height), Image.BICUBIC)
                .convert("1")
            )
            oled.image(image)
            oled.show()
            cmd=""
        
        
    if(cmd == 'SHOWCAP'):		#Xuất ảnh chụp từ file cap.jpg 
        image = (
            Image.open("cap.jpg")
            .resize((oled.width, oled.height), Image.BICUBIC)
            .convert("1")
        )            
            
        oled.image(image)
        oled.show()
        sleep(1)
        
    if(cmd == 'SHOWSEN'):		#Xuất ảnh chụp từ file sensor.jpg
        image = (
            Image.open("sensor.jpg")
            .resize((oled.width, oled.height), Image.BICUBIC)
            .convert("1")
        )
                
        oled.image(image)
        oled.show()
        sleep(1)
        
    if(cmd!='HOLD' and cmd!='X' and cmd!='Y' and cmd!='CAP' and cmd!=""):
        cmd=""
