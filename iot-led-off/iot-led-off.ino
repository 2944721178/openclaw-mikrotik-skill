// LED 关闭程序
// 板载 LED 连接到 Pin 13

const int LED_PIN = 13;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // 关闭 LED
}

void loop() {
  // 保持 LED 关闭
  delay(1000);
}
