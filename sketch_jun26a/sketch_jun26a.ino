int light_pin = 7;    // Relay for light connected to digital pin 5
int socket_pin = 5;   // Relay for socket connected to digital pin 7

void setup() {
  Serial.begin(9600);
  pinMode(light_pin, OUTPUT);
  pinMode(socket_pin, OUTPUT);

    // Begin serial communication

  // Set both relays to OFF initially (assuming active LOW)
  digitalWrite(light_pin,LOW);
  digitalWrite(socket_pin,LOW);

}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Clean input

    if (command == "LIGHTS_ON") {
      digitalWrite(light_pin,HIGH);    // Turn light ON
      Serial.println("Light turned ON");
    } else if (command == "LIGHTS_OFF") {
      digitalWrite(light_pin,LOW);   // Turn light OFF
      Serial.println("Light turned OFF");
    } else if (command == "SWITCH_ON") {
      digitalWrite(socket_pin,HIGH);   // Turn socket ON
      Serial.println("Socket turned ON");
    } else if (command == "SWITCH_OFF") {
      digitalWrite(socket_pin,LOW);  // Turn socket OFF
      Serial.println("Socket turned OFF");
    } else if (command == "EVERYTHING_ON") {
      digitalWrite(socket_pin,HIGH);
      digitalWrite(light_pin,HIGH);
      Serial.println("Everything is ON");
    } else if (command == "EVERYTHING_OFF") {
      digitalWrite(socket_pin,LOW);
      digitalWrite(light_pin,LOW);
      Serial.println("Everything is Off");
    } else {
      Serial.println("Unknown command");
    }
  }
}
