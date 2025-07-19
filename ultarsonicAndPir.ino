const int trigPin = D5;
const int echoPin = D6;
const int pirPin = D7;
const int ldrPin = A0;
const int bulbPin = D1;

const int lightThreshold = 400;

bool ldrChecked = false;
bool bulbOn = false;

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(pirPin, INPUT);
  pinMode(bulbPin, OUTPUT);
  digitalWrite(bulbPin, LOW);
  Serial.println("ESP8266 Ready");
}

void loop() {
  // 1. Ultrasonic distance check
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;

  bool personDetected = (distance <= 50);

  if (personDetected) {
    // 2. Check LDR only once per presence
    if (!ldrChecked) {
      int lightValue = analogRead(ldrPin);
      if (lightValue < lightThreshold) {
        digitalWrite(bulbPin, HIGH);
        bulbOn = true;
        Serial.println("Bulb ON");
      } else {
        digitalWrite(bulbPin, LOW);
        bulbOn = false;
        Serial.println("Bulb OFF");
      }
      ldrChecked = true;
    }

    // 3. Check PIR motion and send status
    int motion = digitalRead(pirPin);
    Serial.println(motion == HIGH ? "1" : "0");

  } else {
    // 4. Person out of range: reset
    if (bulbOn) {
      digitalWrite(bulbPin, LOW);
      bulbOn = false;
    }
    ldrChecked = false;
    Serial.println("0");
  }

  delay(200);
}





