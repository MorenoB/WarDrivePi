import lcd

lcd.init()
lcd.send_byte_data(lcd.LCD_LINE_1, lcd.LCD_CMD)
lcd.message("Raspberry Pi", 2)
lcd.send_byte_data(lcd.LCD_LINE_2, lcd.LCD_CMD)
lcd.message("is ready!", 2)


lcd.cleanup()
