/**
 * Arduino PWM fan controller
 *
 */

#define LED_PIN 2
#define SWITCH_PIN 3

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
}

void loop() {
    digitalWrite(LED_PIN, digitalRead(SWITCH_PIN));
    delay(10);
}
