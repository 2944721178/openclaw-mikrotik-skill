// LED 闪烁 10 秒后停止
// 板载 LED 连接到 Pin 13

const int LED_PIN = 13;
const unsigned long DURATION = 10000; // 10 秒
const int BLINK_INTERVAL = 200; // 200ms 闪烁一次

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  unsigned long startTime = millis();
  
  while (millis() - startTime < DURATION) {
    digitalWrite(LED_PIN, HIGH);
    delay(BLINK_INTERVAL);
    digitalWrite(LED_PIN, LOW);
    delay(BLINK_INTERVAL);
  }
  
  // 10 秒后停止闪烁，保持关闭
  digitalWrite(LED_PIN, LOW);
  
  // 进入休眠，不再闪烁
  while (true) {
    delay(1000);
  }
}
