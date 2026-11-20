// ECE198 bench prototype. Arduino Nano ESP32, default Arduino pin numbering.
#include <Wire.h>
#include <WiFi.h>
// BLE ADDITION BEGIN
#include <BLEDevice.h>
#include <BLE2902.h>

// Little-endian packet: version, state, session (4), active ms (4),
// reps (4), estimated BPM (2; zero means unavailable).
const char* serviceId="823ef401-1d82-41f6-b689-68aedcbb1960";
const char* sampleId="823ef402-1d82-41f6-b689-68aedcbb1960";
BLEServer* bleServer;
BLECharacteristic* bleSample;

class ConnectionEvents : public BLEServerCallbacks {
  void onDisconnect(BLEServer* server) override { server->startAdvertising(); }
};
void beginBluetooth(){
  BLEDevice::init("SmartDumbbell");
  bleServer=BLEDevice::createServer();
  static ConnectionEvents events;
  bleServer->setCallbacks(&events);
  BLEService* service=bleServer->createService(serviceId);
  bleSample=service->createCharacteristic(sampleId,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  bleSample->addDescriptor(new BLE2902());
  uint8_t initial[16]={1};
  bleSample->setValue(initial,sizeof(initial));
  service->start();
  BLEAdvertising* advertising=BLEDevice::getAdvertising();
  advertising->addServiceUUID(serviceId);
  advertising->setScanResponse(true);
  advertising->start();
}

// BLE ADDITION END
#include <WebServer.h>
#include <Adafruit_LSM6DSOX.h>
#include <Adafruit_SSD1306.h>
#include <MAX30105.h>
#include <heartRate.h>

Adafruit_LSM6DSOX imu;
Adafruit_SSD1306 oled(128,64,&Wire,-1);
MAX30105 ppg;
WebServer server(80);
enum State { READY, RUNNING, PAUSED, DONE };
State state=READY;
const char* names[]={"Ready","Running","Paused","Done"};
bool hasImu,hasPpg,hasOled;
unsigned reps=0, bpm=0;
unsigned long activeMs=0, started=0, lastBeat=0, beepAt=0, session=0;
unsigned long phaseAt=0, signalSince=0;
bool lifting=false, contact=false;
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
  lifting=false; contact=false; bpm=0; lastBeat=0;
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
void samplePulse(){
  if(!hasPpg)return;
  ppg.check();
  while(ppg.available()){
    long ir=ppg.getFIFOIR(); ppg.nextSample();
    bool beat=checkForBeat(ir);
    unsigned long now=millis();
    if(state!=RUNNING || ir<50000){
      contact=false; bpm=0; lastBeat=0; continue;
    }
    if(!contact){contact=true;signalSince=now;}
    if(beat && now-signalSince>=1500){
      unsigned long interval=now-lastBeat;
      bpm=(lastBeat && interval>=300 && interval<=1500) ? 60000/interval : 0;
      lastBeat=now;
    }
    if(now-lastBeat>2000)bpm=0;
  }
}
// Bench baseline: mount the gyro X axis along the elbow rotation axis.
// Count two opposite strokes followed by a return to low angular speed.
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
<h1>Smart dumbbell</h1><p>Session, state, active milliseconds, reps, estimated BPM</p>
<pre id="live">Connecting...</pre><button id="save">Download CSV</button>
<script>const rows=["session,state,active_ms,reps,bpm"];
async function poll(){try{const r=await fetch('/sample',{cache:'no-store'});if(!r.ok)throw Error();
const s=await r.text();live.textContent=s;if(rows[rows.length-1]!==s)rows.push(s)}
catch(e){live.textContent='Disconnected'}setTimeout(poll,500)}
save.onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\n')],{type:'text/csv'}));a.download='dumbbell.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};poll()</script>)HTML";
void setup(){
  Serial.begin(115200);
  pinMode(D2,INPUT_PULLUP);pinMode(D5,OUTPUT);pinMode(D7,OUTPUT);
  Wire.begin();Wire.setClock(400000);
  hasImu=imu.begin_I2C(0x6A,&Wire);
  hasPpg=ppg.begin(Wire,I2C_SPEED_FAST);
  if(hasPpg)ppg.setup(0x1F,4,2,400,411,4096); // 100 FIFO samples/s
  Wire.beginTransmission(0x3C);
  hasOled=Wire.endTransmission()==0 && oled.begin(SSD1306_SWITCHCAPVCC,0x3C,false,false);
  Serial.printf("IMU=%d MAX30102=%d OLED=%d\n",hasImu,hasPpg,hasOled);
  WiFi.softAP("SmartDumbbell","curl198demo");
  Serial.println(WiFi.softAPIP());
  server.on("/",[](){server.send_P(200,"text/html",page);});
  server.on("/sample",[](){server.send(200,"text/plain",row());});
  server.begin();
  // BLE ADDITION BEGIN
  beginBluetooth();
  // BLE ADDITION END
}
void loop(){
  if (Serial.available() && Serial.read() == '?') {
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
  samplePulse();sampleMotion();server.handleClient();
  static unsigned long lastDisplay=0;
  if(millis()-lastDisplay<250)return;
  lastDisplay=millis();
  // BLE ADDITION BEGIN
  uint8_t packet[16]={1,static_cast<uint8_t>(state)};
  uint32_t active=elapsed();
  uint16_t rate=bpm;
  memcpy(packet+2,&session,4);
  memcpy(packet+6,&active,4);
  memcpy(packet+10,&reps,4);
  memcpy(packet+14,&rate,2);
  bleSample->setValue(packet,sizeof(packet));
  if(bleServer->getConnectedCount()) bleSample->notify();
  // BLE ADDITION END
  Serial.println(row());
  if(hasOled){
    oled.clearDisplay();oled.setCursor(0,0);oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(2);oled.println(names[state]);
    oled.printf("Reps %u\n",reps);oled.print("BPM  ");
    if(bpm)oled.println(bpm);else oled.println("--");
    oled.setTextSize(1);oled.printf("%lus  IMU:%s HR:%s",elapsed()/1000,hasImu?"OK":"ERR",hasPpg?"OK":"ERR");
    oled.display();
  }
}

