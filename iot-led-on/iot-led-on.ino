// LED 常亮程序
// 板载 LED 连接到 Pin 13

const int LED_PIN = 13;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // 打开 LED
}

void loop() {
  // 保持 LED 常亮，什么都不做
  delay(1000);
}
