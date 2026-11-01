# Sesion_10_I2C_HMI
# Raspberry Pi Pico W + OLED SSD1306 128x64 + LED
# MicroPython

from machine import Pin, I2C, ADC
import time
import rp2
import ssd1306

# ---------------- CONFIGURACION ----------------
I2C_ID = 0
PIN_SDA = 0
PIN_SCL = 1
I2C_FREQ = 400_000

PIN_ADC = 26       # GP26 / ADC0
PIN_LED = 15       # LED externo con resistencia en serie

# Umbrales sobre el porcentaje ADC
WARNING_LIMIT = 60
ALARM_LIMIT = 85

SCREEN_W = 128
SCREEN_H = 64
UPDATE_MS = 100
DRAW_MS = 250
BUTTON_POLL_MS = 30
DEBOUNCE_MS = 180

# ---------------- INICIALIZACION I2C ----------------
i2c = I2C(
    I2C_ID,
    scl=Pin(PIN_SCL),
    sda=Pin(PIN_SDA),
    freq=I2C_FREQ
)

devices = i2c.scan()

print("Escaneo I2C al iniciar:")
if devices:
    for address in devices:
        print("Decimal:", address, "| Hexadecimal: 0x{:02X}".format(address))
else:
    print("No se detectaron dispositivos I2C.")

# Validar la OLED. La direccion mas habitual es 0x3C.
OLED_ADDRESS = None
for address in devices:
    if address in (0x3C, 0x3D):
        OLED_ADDRESS = address
        break

if OLED_ADDRESS is None:
    raise RuntimeError(
        "No se detecto una OLED SSD1306 en 0x3C ni 0x3D. "
        "Revisa VCC, GND, SDA (GP0) y SCL (GP1)."
    )

oled = ssd1306.SSD1306_I2C(
    SCREEN_W, SCREEN_H, i2c, addr=OLED_ADDRESS
)

# ---------------- ENTRADAS Y SALIDAS ----------------
adc = ADC(Pin(PIN_ADC))
led = Pin(PIN_LED, Pin.OUT)
led.off()

# BOOTSEL se utiliza como boton para cambiar de pantalla.
# rp2.bootsel_button() esta disponible en el firmware MicroPython para RP2.
screen = 0
screen_names = ("LIVE", "I2C", "STATS")

# Estadisticas del porcentaje ADC
minimum = 100
maximum = 0
samples = 0

adc_raw = 0
percentage = 0
status = "NORMAL"

last_update = time.ticks_ms()
last_draw = 0
last_button_poll = 0
last_button_change = 0
button_was_pressed = False

# ---------------- FUNCIONES ----------------
def read_sensor():
    """Lee ADC0 y actualiza porcentaje, estado, LED y estadisticas."""
    global adc_raw, percentage, status
    global minimum, maximum, samples

    adc_raw = adc.read_u16()
    percentage = int((adc_raw * 100) / 65535)

    if percentage >= ALARM_LIMIT:
        status = "ALARM"
        led.on()
    elif percentage >= WARNING_LIMIT:
        status = "WARNING"
        led.off()
    else:
        status = "NORMAL"
        led.off()

    if percentage < minimum:
        minimum = percentage
    if percentage > maximum:
        maximum = percentage

    samples += 1


def draw_header(title):
    oled.fill(0)
    oled.text("I2C HMI MONITOR", 0, 0)
    oled.hline(0, 10, 128, 1)
    oled.text(title, 0, 14)


def draw_live():
    draw_header("LIVE")
    oled.text("ADC: {}%".format(percentage), 0, 26)
    oled.text("STATE: {}".format(status), 0, 38)

    # Barra de progreso de 0 a 100 por ciento
    bar_x, bar_y, bar_w, bar_h = 0, 53, 128, 9
    oled.rect(bar_x, bar_y, bar_w, bar_h, 1)
    fill_w = int((bar_w - 2) * percentage / 100)
    if fill_w > 0:
        oled.fill_rect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, 1)


def draw_i2c():
    draw_header("I2C")
    oled.text("SDA: GP{}".format(PIN_SDA), 0, 27)
    oled.text("SCL: GP{}".format(PIN_SCL), 68, 27)
    oled.text("FREQ: {} kHz".format(I2C_FREQ // 1000), 0, 39)

    if devices:
        address_text = " ".join("0x{:02X}".format(a) for a in devices)
        oled.text("ADDR:", 0, 51)
        oled.text(address_text[:15], 42, 51)
    else:
        oled.text("ADDR: none", 0, 51)


def draw_stats():
    draw_header("STATS")
    oled.text("MIN: {}%".format(minimum if samples else 0), 0, 27)
    oled.text("MAX: {}%".format(maximum if samples else 0), 0, 39)
    oled.text("SAMPLES: {}".format(samples), 0, 51)


def draw_screen():
    if screen == 0:
        draw_live()
    elif screen == 1:
        draw_i2c()
    else:
        draw_stats()

    oled.show()


def check_button(now):
    """Detecta pulsacion BOOTSEL con antirrebote por software."""
    global screen, button_was_pressed, last_button_change

    pressed = rp2.bootsel_button()

    if pressed and not button_was_pressed:
        if time.ticks_diff(now, last_button_change) >= DEBOUNCE_MS:
            screen = (screen + 1) % 3
            last_button_change = now

    button_was_pressed = pressed


# ---------------- BUCLE PRINCIPAL ----------------
print("OLED detectada en decimal:", OLED_ADDRESS,
      "| hexadecimal: 0x{:02X}".format(OLED_ADDRESS))
print("Pulsa BOOTSEL para cambiar entre LIVE, I2C y STATS.")

draw_screen()

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_update) >= UPDATE_MS:
        read_sensor()
        last_update = now

    if time.ticks_diff(now, last_button_poll) >= BUTTON_POLL_MS:
        check_button(now)
        last_button_poll = now

    if time.ticks_diff(now, last_draw) >= DRAW_MS:
        draw_screen()
        last_draw = now

    # Pausa muy corta para ceder tiempo al sistema; no bloquea la HMI.
    time.sleep_ms(5)
