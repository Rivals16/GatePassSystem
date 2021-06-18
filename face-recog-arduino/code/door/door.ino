
#include<Servo.h>
Servo myservo;
char d;
int pos;
void setup() {
  delay(2000);
  // put your setup code here, to run once:
Serial.begin(9600);
pinMode(5,OUTPUT);
myservo.attach(8); 
  myservo.write(0);
  delay(1000);
  myservo.write(90);
  delay(1000);
  myservo.write(0);
}

void loop() {
  // put your main code here, to run repeatedly:
if(Serial.available())
{
  d=Serial.read();
}
if(d=='a')
{
  Serial.print(d);
  delay(300);
  for(pos=0;pos<=90;pos+=5)
   { myservo.write(pos);
   delay(20);
   }
   delay(5000);
   for(pos=90;pos>=0;pos-=5)
   { 
   myservo.write(pos);
   delay(20);
   }
   }
   d=' ';

}
