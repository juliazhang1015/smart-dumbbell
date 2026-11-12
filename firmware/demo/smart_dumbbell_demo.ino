#include <Wire.h>
#include <WiFi.h>
#include <esp_system.h>
#include <WebServer.h>
#include <Adafruit_LSM6DSOX.h>
#include <Adafruit_SSD1306.h>
#include <MAX30105.h>
#include "PulseTracker.h"

Adafruit_LSM6DSOX imu;
Adafruit_SSD1306 oled(128,64,&Wire,-1);
MAX30105 ppg;
PulseTracker pulse;
uint32_t pulseServiceAt=0, pulseDataAt=0, pulseGaps=0;
const char* pulseFault="Starting";
bool pulseDebug=false;
WebServer server(80);
enum State { READY, RUNNING, PAUSED, DONE };
State state=READY;
const char* names[]={"Ready","Running","Paused","Done"};
bool hasImu,hasPpg,hasOled;
unsigned reps=0, bpm=0;
unsigned long activeMs=0, started=0, beepAt=0, session=0;
unsigned long phaseAt=0;
bool lifting=false;
float firstSign=0;
unsigned long elapsed(){return activeMs+(state==RUNNING ? millis()-started : 0);}
void feedback(){
  digitalWrite(D5,HIGH); beepAt=millis();
}
void changeState(bool hold){
  if(hold && state!=RUNNING && state!=PAUSED) return;
  if(state==RUNNING) activeMs+=millis()-started;
  if(hold) state=DONE;
  else if(state==RUNNING) state=PAUSED;
  else {
    if(state!=PAUSED){ activeMs=0; reps=0; session++; }
    state=RUNNING; started=millis();
  }
  lifting=false; // Keep the optical filter warm across session transitions.
  digitalWrite(D7,state==RUNNING);
  feedback();
}
void button(){
  static bool raw=false, stable=false, consumed=false;
  static unsigned long changed=0, pressed=0;
  bool down=digitalRead(D2)==LOW;
  unsigned long now=millis();
  if(raw!=down){raw=down;changed=now;}
  if(raw!=stable && now-changed>=30){
    stable=raw;
    if(stable){pressed=changed;consumed=false;}
    else if(!consumed) changeState(changed-pressed>=1200);
  }
  if(raw && stable && !consumed && now-pressed>=1200){
    consumed=true; changeState(true);
  }
}
// Read the hardware FIFO directly: SparkFun's four-entry software ring can
// overwrite unread records when the OLED or HTTP handler delays the loop.
// Do not mix this path with ppg.check(), getIR(), or getFIFOIR().
bool readPulseBytes(uint8_t reg, uint8_t* bytes, uint8_t length){
  Wire.beginTransmission(0x57); Wire.write(reg);
  if(Wire.endTransmission(false)!=0)return false;
  if(Wire.requestFrom(uint8_t(0x57),length)!=length)return false;
  for(uint8_t i=0;i<length;++i)bytes[i]=Wire.read();
  return true;
}
void resetPulseStream(const char* reason){
  pulse.reset(); bpm=0; pulseFault=reason; ++pulseGaps;
  ppg.clearFIFO();
}
void samplePulse(){
  if(!hasPpg)return;
  uint32_t now=millis();
  // 32 FIFO entries at 100 Hz: do not join beats across a sampling gap.
  if(now-pulseServiceAt>=300){
    pulseServiceAt=now; resetPulseStream("Sample gap"); return;
  }
  pulseServiceAt=now;
  uint8_t pointers[3]; // write pointer, overflow count, read pointer
  if(!readPulseBytes(0x04,pointers,3)){
    resetPulseStream("I2C error"); return;
  }
  if(pointers[1]&0x1F){resetPulseStream("FIFO overflow");return;}
  uint8_t pending=(pointers[0]-pointers[2])&0x1F;
  while(pending){
    // At most 30 bytes per transfer, portable to a 32-byte Wire buffer.
    uint8_t records=pending>5 ? 5 : pending;
    uint8_t data[30];
    if(!readPulseBytes(0x07,data,records*6)){
      resetPulseStream("I2C error"); return;
    }
    for(uint8_t i=0;i<records;++i){
      const uint8_t* ir=&data[i*6+3]; // red then IR, three bytes each
      uint32_t value=((uint32_t(ir[0])<<16)|(uint32_t(ir[1])<<8)|ir[2])&0x3FFFF;
      pulse.update(value); // Beat intervals use sample counts, not loop time.
    }
    pending-=records;
    pulseDataAt=now; pulseFault=nullptr;
  }
  if(now-pulseDataAt>500){pulse.reset();pulseFault="No samples";}
  bpm=(state==RUNNING && !pulseFault) ? pulse.bpm : 0;
}
const char* pulseStatus(){
  if(!hasPpg)return "Sensor missing";
  return pulseFault ? pulseFault : pulse.label();
}


void sampleMotion(){
  static unsigned long last=0;
  static bool returning=false;
  unsigned long now=millis();
  if(!hasImu || state!=RUNNING || now-last<10)return;
  last=now;
  sensors_event_t a,g,t;
  if(!imu.getEvent(&a,&g,&t))return;
  float speed=g.gyro.x;
  if(lifting && now-phaseAt>5000){lifting=false;return;}
  if(!lifting && fabs(speed)>0.9){
    lifting=true; returning=false; phaseAt=now; firstSign=speed>0?1:-1;
  }else if(lifting && now-phaseAt>200 && speed*firstSign< -0.9){
    returning=true;
  }else if(lifting && returning && fabs(speed)<0.35 && now-phaseAt>450){
    reps++; lifting=false; feedback();
  }
}
String row(){
  return String(session)+","+names[state]+","+String(elapsed())+","+String(reps)+","+(bpm?String(bpm):String(""));
}
const char page[] PROGMEM=R"HTML(<!doctype html><meta charset=utf-8><title>Smart dumbbell</title>
<h1>Smart dumbbell</h1><p>Session, state, active milliseconds, reps, estimated BPM</p >
<p id="quality">Checking pulse signal...</p><pre id="live">Connecting...</pre><button id="save">Download CSV</button>
<script>const rows=["session,state,active_ms,reps,bpm"];
async function poll(){try{const r=await fetch('/sample',{cache:'no-store'});if(!r.ok)throw Error();
const s=await r.text();live.textContent=s;if(rows[rows.length-1]!==s)rows.push(s);
const q=await fetch('/pulse-status',{cache:'no-store'});if(q.ok)quality.textContent=await q.text()}
catch(e){live.textContent='Disconnected'}setTimeout(poll,500)}
save.onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\n')],{type:'text/csv'}));a.download='dumbbell.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};poll()</script>)HTML";
void setup(){
  Serial.begin(115200);
  pinMode(D2,INPUT_PULLUP);pinMode(D5,OUTPUT);pinMode(D7,OUTPUT);
  Wire.begin();Wire.setClock(400000);
  hasImu=imu.begin_I2C(0x6A,&Wire);
  hasPpg=ppg.begin(Wire,I2C_SPEED_FAST);
  if(hasPpg){
    ppg.setup(0x1F,4,2,400,411,4096); // 100 FIFO samples/s; matches PulseTracker
    ppg.setPulseAmplitudeRed(0); // Only IR is used; retain red+IR FIFO layout.
    ppg.disableFIFORollover();
  }
  Wire.beginTransmission(0x3C);
  hasOled=Wire.endTransmission()==0 && oled.begin(SSD1306_SWITCHCAPVCC,0x3C,false,false);
  Serial.printf("IMU=%d MAX30102=%d OLED=%d\n",hasImu,hasPpg,hasOled);
  // Generate a fresh AP password; keep credentials out of shared source files.
  WiFi.mode(WIFI_AP);
  char apPassword[17];
  snprintf(apPassword,sizeof(apPassword),"%08lx%08lx",
    (unsigned long)esp_random(),(unsigned long)esp_random());
  WiFi.softAP("SmartDumbbell",apPassword);
  Serial.print("Wi-Fi password for this boot: "); Serial.println(apPassword);
  Serial.println(WiFi.softAPIP());
  server.on("/",[](){server.send_P(200,"text/html",page);});
  server.on("/sample",[](){server.send(200,"text/plain",row());});
  server.on("/pulse-status",[](){server.send(200,"text/plain",pulseStatus());});
  server.begin();
  if(hasPpg)ppg.clearFIFO();
  pulseServiceAt=pulseDataAt=millis();
}
void loop(){
  int command=Serial.available() ? Serial.read() : -1;
  if(command=='p')pulseDebug=!pulseDebug;
  if (command == '?') {
    Serial.printf("IMU=%d MAX30102=%d OLED=%d\n", hasImu, hasPpg, hasOled);
    Serial.print("I2C addresses:");
    for (uint8_t addr = 8; addr < 120; ++addr) {
      Wire.beginTransmission(addr);
      if (Wire.endTransmission() == 0) Serial.printf(" 0x%02X", addr);
    }
    Serial.println();
  }
  button();
  if(millis()-beepAt>=80)digitalWrite(D5,LOW);
  samplePulse();sampleMotion();samplePulse();server.handleClient();samplePulse();
  static unsigned long lastDisplay=0;
  if(millis()-lastDisplay<250)return;
  lastDisplay=millis();
  Serial.println(row());
  if(pulseDebug)Serial.printf("# HR %s IR=%lu AC=%.1f envelope=%.1f gaps=%lu\n",
    pulseStatus(),(unsigned long)pulse.raw,pulse.ac,pulse.envelope,(unsigned long)pulseGaps);
  if(hasOled){
    oled.clearDisplay();oled.setCursor(0,0);oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(2);oled.println(names[state]);
    oled.printf("Reps %u\n",reps);oled.print("BPM  ");
    if(bpm)oled.println(bpm);else oled.println("--");
    oled.setTextSize(1);oled.printf("%lus IMU:%s\n",elapsed()/1000,hasImu?"OK":"ERR");
    oled.print(pulseStatus());
    oled.display();
    samplePulse();
  }
}
