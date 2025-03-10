#include <SPI.h>
#include <MFRC522.h>
#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>

// Firebase configuration
FirebaseConfig firebaseConfig;
FirebaseAuth firebaseAuth;

#define FIREBASE_HOST "automationlab-9fccb-default-rtdb.firebaseio.com"  // Firebase Project URL
#define FIREBASE_AUTH "vYM9NyncpNvI8D0gbXKwmHtzf07Cz97HN48ggWoe"         // Firebase database secret key

// Network Credentials
const char* ssid = "TESTNET";
const char* password = "12345678";

// RFID configuration
#define SS_PIN D2
#define RST_PIN D1
MFRC522 rfid(SS_PIN, RST_PIN);

WiFiClient client;
FirebaseData firebaseData;
String lastUID = "";  // To track the last UID sent to Firebase

void setup() {
  Serial.begin(115200);
  delay(10);

  // Connecting to Wi-Fi
  Serial.println();
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  // Wait for the Wi-Fi connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Configure Firebase
  firebaseConfig.host = FIREBASE_HOST;
  firebaseConfig.signer.tokens.legacy_token = FIREBASE_AUTH;

  // Initialize Firebase
  Firebase.begin(&firebaseConfig, &firebaseAuth);
  Firebase.reconnectWiFi(true);

  // Initialize RFID
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("RFID reader initialized.");
}

void loop() {
  // Ensure Wi-Fi and Firebase are connected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting to WiFi...");
    WiFi.begin(ssid, password);
    delay(1000);
  }

  // Reconnect Firebase if disconnected
  if (!Firebase.ready()) {
    Serial.println("Reconnecting to Firebase...");
    Firebase.begin(&firebaseConfig, &firebaseAuth);
  }

  // Check for a new RFID card and read it
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    // Get the card number (UID)
    String card_num = getCardNumber();

    // Check if this UID has already been sent
    if (card_num != lastUID) {
      Serial.print("Detected Card ID: ");
      Serial.println(card_num);

      // Send the card number to Firebase
      if (Firebase.setString(firebaseData, "/rfidData/cardID", card_num)) {
        Serial.println("Card ID sent to Firebase successfully.");
        lastUID = card_num;  // Update lastUID to avoid resending
      } else {
        Serial.print("Error sending card ID to Firebase: ");
        Serial.println(firebaseData.errorReason());
      }
    } else {
      Serial.println("Card already scanned. Remove card and try again.");
    }

    // Halt PICC to stop reading the same card repeatedly
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    delay(5000);  // Delay to avoid immediate consecutive reads
  }
}

String getCardNumber() {
  String UID = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    UID += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    UID += String(rfid.uid.uidByte[i], HEX);
  }
  UID.toUpperCase();
  return UID;
}
