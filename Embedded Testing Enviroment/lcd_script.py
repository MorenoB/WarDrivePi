import sys
import lcd

lcd.init()
lcd.sendByteData(lcd.LCD_LINE_1, lcd.LCD_CMD)
lcd.message("Raspberry Pi", 2)
lcd.sendByteData(lcd.LCD_LINE_2, lcd.LCD_CMD)
lcd.message("is ready!", 2)


lcd.cleanup()
