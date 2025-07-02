#include <Servo.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define PWMA D1  // Motor speed PWM right
#define PWMB D2  // Motor speed PWM left
#define DA D3    // Motor direction right
#define DB D4    // Motor direction left

#define S1 D5
#define S2 D6
#define S3 A0
#define S4 D7
#define S5 D8

Servo myServo;

String buff;
int motor = -1;  // default motor speed: -1 menandakan belum diatur
int servo = 100;  // default servo angle: -1 menandakan belum diatur
int sensor1, sensor2, sensor3, sensor4, sensor5;

const char* ap_ssid = "trafobot1";
const char* ap_password = "12345678";

WiFiUDP udp;
unsigned int localUdpPort = 4210;
char incomingPacket[255];

void setup() {
  Serial.begin(115200);
  Serial.println("Program Dimulai");

  WiFi.softAP(ap_ssid, ap_password);
  Serial.print("Access Point \"");
  Serial.print(ap_ssid);
  Serial.println("\" dibuat");
  Serial.print("IP Access Point: ");
  Serial.println(WiFi.softAPIP());

  udp.begin(localUdpPort);
  Serial.print("UDP server mulai di port: ");
  Serial.println(localUdpPort);

  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(DA, OUTPUT);
  pinMode(DB, OUTPUT);
  pinMode(S1, INPUT);
  pinMode(S2, INPUT);
  pinMode(S3, INPUT);
  pinMode(S4, INPUT);
  pinMode(S5, INPUT);

  digitalWrite(PWMA, LOW);
  digitalWrite(PWMB, LOW);
  digitalWrite(DA, LOW);
  digitalWrite(DB, LOW);

  myServo.attach(D0);  // Pastikan D0 tidak bertabrakan dengan fungsi lain
  // Tidak langsung write servo!
}

void loop() {
  sensor();
  readUdp();

  if (buff.length() > 0) {
    if (buff == "maju" && motor != -1) {
      forward(motor);
    } else if (buff == "kiri" && motor != -1) {
      kiri(motor);
    } else if (buff == "kanan" && motor != -1) {
      kanan(motor);
    } else if (buff == "mundur" && motor != -1) {
      backward(motor);
    } else if (buff == "stop") {
      stopMotors();
    } else if (buff.startsWith("M")) {
      String temp = buff.substring(2);
      motor = constrain(temp.toInt(), 0, 255);
      Serial.print("Motor speed set to: ");
      Serial.println(motor);
    } else if (buff.startsWith("S")) {
      String temp = buff.substring(2);
      servo = constrain(temp.toInt(), 0, 180);
      myServo.write(servo);
      Serial.print("Servo angle set to: ");
      Serial.println(servo);
    }
    buff = "";
  }
  delay(20);  // agar lebih responsif
}

void readUdp() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int n = udp.read(incomingPacket, 254);
    if (n > 0) {
      incomingPacket[n] = 0;
      buff = String(incomingPacket);
      buff.trim();
      Serial.print("Received UDP: ");
      Serial.println(buff);

      if (buff == "ping") {
        const char* pongMsg = "pong";
        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write(pongMsg);
        udp.endPacket();
        Serial.println("Sent pong");
        buff = "";
      }
    }
  }
}

void sensor() {
  sensor1 = digitalRead(S1);
  sensor2 = digitalRead(S2);
  sensor3 = analogRead(S3);
  if (sensor3 > 500) {
    sensor3 = 1;
  } else {
    sensor3 = 0;
  }
  sensor4 = digitalRead(S4);
  sensor5 = digitalRead(S5);

  String sensorData = String(sensor1) + "," + String(sensor2) + "," + String(sensor3) + "," + String(sensor4) + "," + String(sensor5);

  IPAddress remoteIP = udp.remoteIP();
  uint16_t remotePort = udp.remotePort();

  if (remoteIP != INADDR_NONE && remotePort != 0) {
    udp.beginPacket(remoteIP, remotePort);
    udp.write(sensorData.c_str());
    udp.endPacket();
  }

  Serial.println(sensorData);
}

void forward(int num) {
  Serial.println("Moving forward...");
  digitalWrite(DA, HIGH);
  digitalWrite(DB, LOW);
  analogWrite(PWMA, num);
  analogWrite(PWMB, num);
}

void kanan(int num) {
  Serial.println("Moving TurnRight...");
  digitalWrite(DA, HIGH);
  digitalWrite(DB, LOW);
  analogWrite(PWMA, 0);
  analogWrite(PWMB, num);
}

void kiri(int num) {
  Serial.println("Moving TurnLeft...");
  digitalWrite(DA, HIGH);
  digitalWrite(DB, LOW);
  analogWrite(PWMA, num);
  analogWrite(PWMB, 0);
}

void backward(int num) {
  Serial.println("Moving backward...");
  digitalWrite(DA, LOW);
  digitalWrite(DB, HIGH);
  analogWrite(PWMA, num);
  analogWrite(PWMB, num);
}

void stopMotors() {
  Serial.println("Stopping motors...");
  digitalWrite(DA, LOW);
  digitalWrite(DB, LOW);
  digitalWrite(PWMA, LOW);
  digitalWrite(PWMB, LOW);
}
