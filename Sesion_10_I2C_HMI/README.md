# Sesion 10 — Smart I2C HMI Monitor
Juan Pablo Ruiz Gil
## 1. Objetivo

Desarrollar un monitor HMI (Human-Machine Interface) con una Raspberry Pi Pico W y una pantalla OLED SSD1306 de 128 × 64 píxeles. El sistema utiliza comunicación I2C para controlar la pantalla, lee una señal analógica mediante el ADC, muestra estados de operación y registra estadísticas de las muestras.

El proyecto utiliza tres vistas: **LIVE**, **I2C** y **STATS**. Un LED externo funciona como indicador de alarma.

## 2. Material utilizado

- Raspberry Pi Pico W.
- Pantalla OLED SSD1306 I2C de 128 × 64.
- LED externo.
- Resistencia de 220 Ω a 330 Ω para el LED.
- Cables Dupont.
- Cable USB para programar la Pico W.

No se utilizó un segundo dispositivo I2C ni el sensor MPU6050 (bonus opcional).

## 3. Diagrama de conexiones y pines

| Elemento | Pin de Raspberry Pi Pico W |
|---|---|
| OLED VCC | 3V3(OUT) |
| OLED GND | GND |
| OLED SDA | GP0 |
| OLED SCL | GP1 |
| Entrada analógica ADC | GP26 / ADC0 |
| LED (ánodo, mediante resistencia) | GP15 |
| LED (cátodo) | GND |

**Nota:** el LED debe conectarse en serie con una resistencia de 220 Ω a 330 Ω. No conectes un LED directamente entre GP15 y GND sin resistencia.

La entrada GP26 se utiliza como señal analógica. Como no se cuenta con potenciómetro, puede conectarse GP26 a GND para probar una lectura cercana a 0 %, o a 3V3(OUT) para una lectura cercana a 100 %. Nunca se debe aplicar más de 3.3 V a una entrada ADC. Si GP26 queda desconectado, la lectura puede fluctuar porque la entrada está flotante.

### Diagrama lógico

```text
             Raspberry Pi Pico W
          ┌────────────────────────┐
          │                        │
 GP0  ────┼──────── SDA ─────┐     │
 GP1  ────┼──────── SCL ───┐ │     │
 3V3  ────┼──────── VCC ─┐ │ │     │
 GND  ────┼──────── GND ─┴─┴─┴──┐  │
          │                     │  │
 GP26 ────┼──── Entrada ADC     │  │
 GP15 ────┼── Resistencia ─ LED ─ GND
          │                        │
          └────────────────────────┘
                       OLED SSD1306
```

## 4. Comunicación I2C

I2C (Inter-Integrated Circuit) es un protocolo de comunicación serial síncrono que utiliza dos líneas principales:

- **SDA (Serial Data):** transmite los datos.
- **SCL (Serial Clock):** transporta la señal de reloj que sincroniza la comunicación.

Varios dispositivos pueden compartir las mismas líneas SDA y SCL porque cada dispositivo utiliza una dirección I2C única. El controlador inicia la comunicación y selecciona al dispositivo al que desea enviar o del que desea recibir información mediante esa dirección. Por ello, una pantalla y otros sensores I2C pueden conectarse al mismo bus, siempre que no tengan direcciones duplicadas y respeten los niveles eléctricos del bus.

En esta práctica se configura I2C0 en GP0 (SDA) y GP1 (SCL), con una frecuencia de 400 kHz.

## 5. Escaneo y dirección de la OLED

El programa ejecuta `i2c.scan()` al iniciar y muestra las direcciones encontradas en decimal y hexadecimal en la consola serial.

La dirección más habitual de una OLED SSD1306 es:

| Formato | Dirección |
|---|---|
| Decimal | 60 |
| Hexadecimal | 0x3C |

Algunas pantallas pueden utilizar `0x3D` (decimal 61). El programa valida ambas direcciones y se detiene con un mensaje de error si no detecta ninguna.

**Resultado real de la práctica:** completar esta sección después de ejecutar el programa y revisar la consola serial.

- Resultado de `i2c.scan()` en decimal: **[ESCRIBIR RESULTADO REAL]**
- Resultado de `i2c.scan()` en hexadecimal: **[ESCRIBIR RESULTADO REAL]**
- Dirección detectada de la OLED: **[0x3C / 0x3D, CONFIRMAR]**

No se debe copiar un resultado esperado como si fuera una medición: los valores anteriores son referencias comunes y deben confirmarse con el escaneo físico.

## 6. Funcionamiento de las pantallas HMI

### Pantalla LIVE

Muestra el porcentaje calculado a partir de la lectura ADC, el estado del sistema y una barra de progreso.

Los umbrales configurados son:

| Porcentaje ADC | Estado | LED |
|---|---|---|
| 0 % a 59 % | NORMAL | Apagado |
| 60 % a 84 % | WARNING | Apagado |
| 85 % a 100 % | ALARM | Encendido |

El LED se enciende únicamente cuando el estado es `ALARM`.

**Captura de pantalla LIVE:**  
[Insertar aquí la captura de la pantalla LIVE]

### Pantalla I2C

Muestra los pines SDA y SCL utilizados, la frecuencia configurada y las direcciones detectadas durante el escaneo inicial.

**Captura de pantalla I2C:**  
[Insertar aquí la captura de la pantalla I2C]

### Pantalla STATS

Muestra el valor mínimo, el valor máximo y el número de muestras registradas desde que inició el programa. Los valores mínimo y máximo se expresan como porcentaje ADC.

**Captura de pantalla STATS:**  
[Insertar aquí la captura de la pantalla STATS]

## 7. Cambio de pantalla

Se utiliza el botón físico BOOTSEL de la Raspberry Pi Pico W mediante la función `rp2.bootsel_button()` de MicroPython. Cada pulsación cambia a la siguiente pantalla en el orden LIVE → I2C → STATS → LIVE.

La detección se realiza periódicamente y utiliza un intervalo antirrebote por software. No se necesita un pulsador externo adicional.

## 8. Actualización del sistema

El programa realiza una lectura ADC cada 100 ms y actualiza la pantalla cada 250 ms. El bucle principal utiliza una pausa de solo 5 ms, evitando pausas largas que hagan lenta la interfaz.

## 9. Tabla de pruebas

Completar la columna de resultado después de realizar cada prueba.

| Prueba | Procedimiento | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| Detección I2C | Encender la Pico W y revisar la consola | Detectar OLED en 0x3C o 0x3D | [0x3c] |
| Pantalla LIVE | Observar la primera pantalla | Mostrar ADC, estado y barra | [listo] |
| Pantalla I2C | Pulsar BOOTSEL una vez | Mostrar SDA, SCL, frecuencia y dirección | [listo] |
| Pantalla STATS | Pulsar BOOTSEL otra vez | Mostrar mínimo, máximo y muestras | [listo] |
| Estado NORMAL | Mantener GP26 conectado a GND | Estado NORMAL y LED apagado | [listo] |
| Estado WARNING | Aplicar una señal entre 60 % y 84 % de 3.3 V | Estado WARNING y LED apagado | [listo] |
| Estado ALARM | Aplicar una señal igual o superior al 85 % de 3.3 V | Estado ALARM y LED encendido | [listo] |
| Cambio cíclico | Seguir pulsando BOOTSEL | Regresar a LIVE después de STATS | [listo] |


## 10. Conclusión

Se desarrolló un monitor HMI con una Raspberry Pi Pico W y una pantalla OLED SSD1306 mediante el protocolo de comunicación I2C. El sistema permite consultar información de una entrada analógica, visualizar estados de operación, revisar los parámetros y dispositivos del bus I2C y consultar estadísticas de las muestras.

También se implementó un indicador LED que se activa únicamente cuando la lectura alcanza el estado ALARM. La práctica permite comprender el uso de un bus I2C compartido, la lectura ADC y la actualización de una interfaz en un sistema embebido.
