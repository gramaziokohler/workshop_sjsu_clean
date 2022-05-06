//
// Requirements:
//  - Adafruit NeoPixel (from Library Manager)
//  - Arduino JSON (from Library Manager)
//  - AsyncTCP (from ZIP file)
//  - ESPAsyncWebServer (from ZIP file)
//
// Tools:
//  - ESP32 Filesystem Uploader https://github.com/me-no-dev/arduino-esp32fs-plugin/releases/
//
#include "Arduino.h"
#include <Adafruit_NeoPixel.h>

#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>

/**************************
 * Configure web server
 **************************/

const char* ssid = "lightpainting";
const char* password = "robolux21";
AsyncWebServer server(80);

/**************************
 * LED configuration
 **************************/
 
#define NUM_LEDS 7
#define DATA_PIN 25
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, DATA_PIN, NEO_GRB + NEO_KHZ800);
int led_values[NUM_LEDS][3] = {{0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}};


void setup() {
  Serial.begin(115200);
  setupLEDs();
  setupWifi();
  setupServer();
}

void loop() {
}


/**************************
 * LED functions
 **************************/

void setupLEDs() {
  strip.setBrightness(25);
  strip.show();

  setStatusLed(0, 0, 0, 50);
}

void setStatusLed(uint8_t r, uint8_t g, uint8_t b, uint8_t delay_in_ms) {
  led_values[0][0] = r;
  led_values[0][1] = g;
  led_values[0][2] = b;
  updateStrip();
  if (delay_in_ms > 0) delay(delay_in_ms);
}

void pulseLed(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < 100 ; i++) {
    float p = i / 100.0;
    setStatusLed(int(r * p), int(g * p), int(b * p), 0);
    delay(20);
  }
  for (int i = 100; i > 0; i--) {
    float p = i / 100.0;
    setStatusLed(int(r * p), int(g * p), int(b * p), 0);
    delay(20);
  }
}

void updateStrip() {
  for(uint16_t i=0; i< strip.numPixels(); i++) {
    strip.setPixelColor(i, led_values[i][0], led_values[i][1], led_values[i][2]);
  }
  strip.show();
}

/**************************
 * Web functions
 **************************/

void setupWifi() {
  setStatusLed(255, 0, 0, 100);

  WiFi.mode(WIFI_STA);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.println(F("Connecting to WiFi..."));
    WiFi.begin(ssid, password);
  
    if (WiFi.waitForConnectResult() != WL_CONNECTED) {
        Serial.println(F("WiFi Failed! Will retry in 2 seconds."));
        delay(2000);
    } else {
      break;
    }
  }

  Serial.println(F("Connected."));
  Serial.print(F("IP Address: "));
  Serial.println(WiFi.localIP());

  pulseLed(0, 255, 0);
  delay(100);
}

StaticJsonDocument<200> doc;

void setupServer() {
  if(!SPIFFS.begin(true)){
    Serial.println(F("An Error has occurred while mounting SPIFFS"));
    return;
  }

  // Static routes
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/index.html", String(), false);
  });
  server.on("/style.css", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/style.css", "text/css");
  });

  // Active routes
  server.on("/hi", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/plain", "Hello SJSU");
  });
  server.on("/brightness", HTTP_GET, [](AsyncWebServerRequest *request){
    int value = (int)request->getParam("value");
    strip.setBrightness(value);
    updateStrip();
    request->send(200, "text/plain", "OK");
  });
  server.on("/leds", HTTP_GET, [] (AsyncWebServerRequest *request) {
    if (request->hasParam("rgb")) {
      DeserializationError error = deserializeJson(doc, request->getParam("rgb")->value().c_str());
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      }

      JsonArray values = doc.as<JsonArray>();
      int i = 0;
      for (JsonVariant value : values) {
        led_values[int(i / 3)][i % 3] = value.as<int>();
        i++;
      }
    }
    if (request->hasParam("brightness")) {
      strip.setBrightness(request->getParam("brightness")->value().toInt());
    }
    updateStrip();
    request->send(200, "text/plain", "OK");
  });

  server.onNotFound(notFound);
  server.begin();

  pulseLed(0, 255, 0);
  delay(100);
  Serial.println(F("Web server started."));
  
}

void notFound(AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "This is not the page you're looking for.");
}
