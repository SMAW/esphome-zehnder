# ESPHome Zehnder Fan Controller met CC1101

Dit project maakt het mogelijk om draadloos een Zehnder ComfoFan / ComfoAir mechanische ventilatie-unit te besturen via Home Assistant. Het gebruikt een ESP32-C6 module samen met een CC1101 868 MHz radio module voor draadloze communicatie met het Zehnder ventilatiesysteem.

## Overzicht

Deze ESPHome component biedt:
- 📡 Draadloze besturing van Zehnder ventilatoren via 868 MHz
- 🏠 Volledige integratie met Home Assistant
- ⚙️ Ondersteuning voor verschillende ventilatiesnelheden (Laag/Gemiddeld/Hoog/Max)
- 🔄 Automatische pairing met de ventilatie-unit
- 💾 Persistente opslag van pairing informatie

## Hardware Vereisten

### Benodigde Componenten

1. **ESP32-C6 Development Board**
   - ESP32-C6-DevKitC-1 of vergelijkbaar
   - Native 802.15.4 support (niet gebruikt, maar handig voor toekomstige uitbreidingen)

2. **CC1101 868 MHz Transceiver Module**
   - Frequentiebereik: 868 MHz
   - SPI interface
   - Voeding: 3.3V

3. **Zehnder Ventilatie Systeem**
   - ComfoAir systemen
   - ComfoFan systemen
   - Of andere Zehnder units die het 868 MHz protocol ondersteunen

### Waarom CC1101 in plaats van nRF905?

De CC1101 heeft belangrijke voordelen ten opzichte van de nRF905:

- ✅ **Beter bereik**: De CC1101 heeft betere RF-eigenschappen op 868 MHz
- ✅ **Native 868 MHz ondersteuning**: Geen hardware modificaties nodig
- ✅ **Betere beschikbaarheid**: CC1101 modules zijn gemakkelijker verkrijgbaar
- ✅ **Meer configuratieopties**: Flexibeler in modulatie en filters
- ✅ **Lagere kosten**: Doorgaans goedkoper dan nRF905 modules

## Bedradingsschema

### ESP32-C6 naar CC1101 Pinout

| ESP32-C6 Pin | CC1101 Pin | Functie | Beschrijving |
|--------------|------------|---------|--------------|
| GPIO6        | SCK        | SPI Clock | Synchrone klok voor SPI communicatie |
| GPIO7        | MOSI (SI)  | SPI Data Out | Data van ESP32 naar CC1101 |
| GPIO2        | MISO (SO)  | SPI Data In | Data van CC1101 naar ESP32 |
| GPIO10       | CSN (CS)   | Chip Select | Selecteert CC1101 voor communicatie |
| GPIO3        | GDO0       | Data Ready | Interrupt pin voor ontvangen data |
| GPIO4        | GDO2       | (Optioneel) | Extra status pin (optioneel) |
| 3.3V         | VCC        | Voeding | 3.3V voedingsspanning |
| GND          | GND        | Massa | Gemeenschappelijke massa |

### Belangrijke Opmerkingen

- ⚠️ **Gebruik ALLEEN 3.3V** - De CC1101 is niet 5V tolerant!
- ⚠️ **Korte verbindingen** - Houd de draden tussen ESP32 en CC1101 zo kort mogelijk voor betrouwbare SPI communicatie
- 💡 **Antenne** - Zorg voor een goede 868 MHz antenne op de CC1101 voor optimaal bereik
- 💡 **GDO2 is optioneel** - Deze pin kan worden weggelaten als deze niet wordt gebruikt

## Installatie

### Stap 1: ESPHome Installeren

Als je ESPHome nog niet hebt geïnstalleerd:

```bash
pip install esphome
```

Of gebruik de Home Assistant Add-on voor ESPHome.

### Stap 2: Project Klonen of Gebruiken als External Component

#### Optie A: Git Clone (Lokale Ontwikkeling)

```bash
git clone https://github.com/SMAW/esphome-zehnder.git
cd esphome-zehnder
```

#### Optie B: External Component (Aanbevolen voor Gebruikers)

Voeg het volgende toe aan je ESPHome YAML configuratie:

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/SMAW/esphome-zehnder
      ref: main
    refresh: 60s
    components: [zehnder_fan]
```

### Stap 3: Secrets Configureren

Maak een `secrets.yaml` bestand aan met je WiFi en API credentials:

```yaml
# secrets.yaml
wifi_ssid: "JouwWiFiSSID"
wifi_password: "JouwWiFiWachtwoord"
wifi_domain: ".local"
api_encryption_key: "jouw-32-byte-base64-sleutel"
ota_password: "jouw-ota-wachtwoord"
```

Genereer een API encryption key met:

```bash
esphome wizard naam-van-je-device.yaml
```

### Stap 4: Configuratie Aanpassen

Pas `zehnder_fan_controller.yaml` aan naar jouw situatie, of maak je eigen YAML configuratie (zie hieronder).

### Stap 5: Firmware Compileren en Flashen

#### Eerste Keer Flashen (via USB)

```bash
esphome run zehnder_fan_controller.yaml
```

Selecteer de USB poort waarop je ESP32-C6 is aangesloten.

#### OTA Updates (na eerste flash)

Na de eerste flash kun je draadloos updaten:

```bash
esphome run zehnder_fan_controller.yaml
```

Selecteer het draadloze apparaat in het menu.

## Configuratie

### Basis YAML Configuratie

```yaml
esphome:
  name: zehnder-fan-controller
  friendly_name: Zehnder Ventilatie Controller

esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf

# Enable logging
logger:

# Enable Home Assistant API
api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  domain: !secret wifi_domain

# SPI configuratie voor CC1101
spi:
  id: spi_bus
  clk_pin: GPIO6   # SCK
  mosi_pin: GPIO7  # MOSI
  miso_pin: GPIO2  # MISO

# External component (voor releases)
external_components:
  - source:
      type: git
      url: https://github.com/SMAW/esphome-zehnder
      ref: main
    refresh: 60s
    components: [zehnder_fan]

# Fan configuratie met CC1101
fan:
  - platform: zehnder_fan
    id: ventilation_fan
    name: Mechanische Ventilatie
    spi_id: spi_bus
    
    # CC1101 Pin Configuratie
    cs_pin: GPIO10      # CS/SS
    gdo0_pin: GPIO3     # GDO0 (data ready interrupt)
    gdo2_pin: GPIO4     # GDO2 (optioneel)

# Utility buttons
button:
  - platform: restart
    name: Herstart Controller
    disabled_by_default: true

  - platform: template
    name: Koppel met Ventilator
    icon: mdi:wifi
    entity_category: config
    on_press:
      - lambda: |-
          id(ventilation_fan).start_pairing();
```

### Pin Aanpassingen

Als je andere pinnen wilt gebruiken, pas dan de volgende secties aan:

**SPI Pinnen:**
```yaml
spi:
  clk_pin: GPIO6   # Verander naar jouw SCK pin
  mosi_pin: GPIO7  # Verander naar jouw MOSI pin
  miso_pin: GPIO2  # Verander naar jouw MISO pin
```

**CC1101 Control Pinnen:**
```yaml
fan:
  - platform: zehnder_fan
    cs_pin: GPIO10   # Chip Select
    gdo0_pin: GPIO3  # Data Ready (verplicht)
    gdo2_pin: GPIO4  # Optioneel, kan worden weggelaten
```

## Gebruik

### 1. Eerste Pairing met Ventilator

Na het flashen van de firmware en toevoegen aan Home Assistant:

1. Open Home Assistant
2. Ga naar de ESPHome integratie
3. Zoek je "Zehnder Ventilatie Controller" device
4. Klik op de **"Koppel met Ventilator"** button
5. Zet je Zehnder ventilator in pairing modus (raadpleeg je ventilator handleiding)
6. De controller zal automatisch zoeken naar de ventilator en koppelen
7. Pairing informatie wordt opgeslagen in het niet-vluchtige geheugen (NVS)

**Pairing Status:**
- Check de ESPHome logs voor pairing voortgang
- Succesvol: "Pairing successful! Network ID: 0x..."
- Gefaald: "Pairing failed" - probeer opnieuw

### 2. Ventilator Bedienen

Na succesvol koppelen kun je de ventilator bedienen via Home Assistant:

**Via UI:**
- Ga naar het Fan entity
- Zet de ventilator aan/uit
- Kies een snelheid:
  - **Laag** (1) - Laagste stand
  - **Gemiddeld** (2) - Normale stand
  - **Hoog** (3) - Hoge stand  
  - **Max** (4) - Maximum stand

**Via Automations:**
```yaml
automation:
  - alias: "Ventilatie hoog bij koken"
    trigger:
      - platform: state
        entity_id: binary_sensor.keuken_sensor
        to: "on"
    action:
      - service: fan.set_percentage
        target:
          entity_id: fan.mechanische_ventilatie
        data:
          percentage: 100  # Max snelheid
```

**Via Services:**
```yaml
service: fan.turn_on
target:
  entity_id: fan.mechanische_ventilatie
data:
  speed: "medium"
```

### 3. Logs Bekijken

Voor troubleshooting, bekijk de live logs:

```bash
esphome logs zehnder_fan_controller.yaml
```

Of via Home Assistant: ESPHome > Device > Logs

## Troubleshooting

### Pairing Lukt Niet

**Symptomen:** "Pairing failed after X retries"

**Oplossingen:**
1. Controleer of de ventilator in pairing modus staat
2. Zorg dat de CC1101 binnen bereik is van de ventilator (< 10 meter voor eerste pairing)
3. Check de antenne op de CC1101
4. Verifieer dat de CC1101 correct is aangesloten (vooral GDO0)
5. Check de logs voor SPI errors

### Geen Communicatie met CC1101

**Symptomen:** "CC1101 initialization failed" of SPI errors

**Oplossingen:**
1. Controleer alle SPI verbindingen (SCK, MOSI, MISO, CS)
2. Verifieer 3.3V voeding naar CC1101
3. Meet met multimeter:
   - VCC = 3.3V
   - GND = 0V
4. Controleer of CS pin correct is geconfigureerd
5. Probeer lagere SPI snelheid (verander `DATA_RATE_4MHZ` naar `DATA_RATE_1MHZ` in code)

### Ventilator Reageert Niet op Commando's

**Symptomen:** Pairing succesvol, maar ventilator reageert niet

**Oplossingen:**
1. Check bereik - CC1101 moet binnen bereik zijn
2. Controleer antenne op CC1101
3. Probeer opnieuw te pairen
4. Verifieer in logs dat commando's worden verzonden
5. Check of Network ID correct is opgeslagen

### ESP32 Crashed of Reboot

**Symptomen:** Onverwachte reboots, watchdog timeouts

**Oplossingen:**
1. Controleer voeding - ESP32-C6 heeft stabiele 3.3V/5V nodig
2. Voeg voedingscondensators toe (100µF bij 3.3V rail)
3. Verlaag SPI snelheid
4. Check voor kortsluiting in bedrading

### Home Assistant Toont Verkeerde Status

**Symptomen:** Fan entity toont verkeerde snelheid of staat

**Oplossingen:**
1. Dit is normaal - Zehnder protocol heeft geen status feedback
2. Controller stuurt commando's, maar ontvangt geen huidige status van ventilator
3. Status in HA is de _gewenste_ staat, niet de _werkelijke_ staat

## Protocol Informatie

### Zehnder 868 MHz Protocol

Het Zehnder protocol blijft ongewijzigd:
- **Frame grootte:** 16 bytes
- **Frequentie:** 868 MHz
- **Modulatie:** GFSK (via CC1101)
- **Pairing:** DISCOVER → JOIN → ACK sequence

**Commando Types:**
- `SETSPEED` (0x02) - Stel ventilatiesnelheid in
- `SETTIMER` (0x03) - Stel timer in
- `JOIN_REQUEST` (0x04) - Pairing request
- `JOIN_OPEN` (0x06) - Pairing open
- `JOIN_ACK` (0x0C) - Pairing acknowledgment

### Verschil met nRF905 Implementatie

**Hardware Laag:**
- nRF905: Native 433/868 MHz transceiver met vaste configuratie
- CC1101: Flexibele sub-GHz transceiver met configureerbare registers

**Protocol Laag:**
- Beide implementaties gebruiken hetzelfde Zehnder applicatie protocol
- Alleen de onderliggende radio driver verschilt

**Voordelen CC1101:**
- Betere RF-eigenschappen
- Meer configuratiemogelijkheden (power, data rate, etc.)
- Eenvoudigere hardware interface (minder control pins)

## Technische Details

### CC1101 Configuratie

De CC1101 wordt geconfigureerd voor:
- **Carrier Frequency:** 868.35 MHz
- **Modulation:** GFSK
- **Data Rate:** ~38.4 kbps
- **RX Bandwidth:** ~101.5 kHz
- **Sync Word:** 0xD391
- **Packet Length:** 16 bytes (fixed)
- **TX Power:** ~10 dBm (configureerbaar)

### Geheugengebruik

- **Pairing Info:** Opgeslagen in ESP32 NVS (Non-Volatile Storage)
- **Persistent:** Blijft bewaard na reboot of power cycle
- **Reset:** Via ESPHome service of opnieuw pairen overschrijft oude data

## Ontwikkeling en Bijdragen

### Repository Structuur

```
.
├── components/
│   └── zehnder_fan/
│       ├── __init__.py          # ESPHome component registratie
│       ├── fan.py               # Python configuratie schema
│       ├── zehnder_fan.h        # C++ header (CC1101Controller + Protocol)
│       └── zehnder_fan.cpp      # C++ implementatie
├── zehnder_fan_controller.yaml  # Voorbeeld configuratie
└── README.md                    # Deze file
```

### Bijdragen

Bijdragen zijn welkom! Open een issue of pull request op GitHub.

**Voor pull requests:**
1. Fork de repository
2. Maak een feature branch
3. Test je wijzigingen grondig
4. Schrijf duidelijke commit messages
5. Open een pull request met beschrijving

## Licentie

Dit project is open source. Zie de LICENSE file voor details.

## Credits en Dankwoord

- **Original nRF905 Implementation:** Gebaseerd op eerdere nRF905 implementaties voor Zehnder control
- **Zehnder Protocol:** Reverse engineered door de community
- **ESPHome:** Voor het uitstekende framework en community
- **Home Assistant:** Voor de integratie mogelijkheden

## Disclaimer

Dit project is niet officieel geaffilieerd met of goedgekeurd door Zehnder Group. Gebruik op eigen risico. 

⚠️ **Waarschuwing:** Het modificeren van ventilatie systemen kan gevolgen hebben voor garantie en veiligheid. Zorg dat je weet wat je doet.

## Support

Voor vragen, problemen of suggesties:
- Open een issue op GitHub
- Check bestaande issues voor oplossingen
- Bekijk de logs voor debugging informatie

---

**Happy ventilating! 🌬️**
