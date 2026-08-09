#include<Servo.h> 
 
Servo servo; 
int servoPin = 7; 

void setup() 
{ 
  Serial.begin(9600);
  servo.attach(servoPin);
  servo.write(0); //0도
  delay(500);
} 
 
void loop()
{
  if(Serial.available()) //시리얼 통신을 할 떄 데이터 수신 시 사용
  {
    int angle = Serial.parseInt();

    servo.write(angle);
  }
}