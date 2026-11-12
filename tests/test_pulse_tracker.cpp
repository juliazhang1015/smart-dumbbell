#include "../firmware/demo/PulseTracker.h"
#include <cassert>
#include <cmath>
#include <iostream>

static void wave(PulseTracker& p, int rate, int seconds, float dc=30000,
                 float amplitude=100, float noise=0) {
  for(int i=0;i<seconds*100;++i) {
    float signal=dc+amplitude*std::sin(6.283185307f*rate*i/6000.0f);
    signal+=noise*std::sin(2.13f*i);
    p.update(static_cast<uint32_t>(signal));
  }
}
int main(){
  for(int rate : {40,60,90,120,180,200}) {
    PulseTracker p; wave(p,rate,15,30000,100,5);
    std::cout << rate << " -> " << p.bpm << '\n';
    assert(std::abs(int(p.bpm)-rate)<=3);
  }
  PulseTracker p;
  wave(p,75,10,18000,45,3); assert(std::abs(int(p.bpm)-75)<=2);
  p.update(0); assert(p.bpm==0 && p.status==PulseTracker::NO_CONTACT);
  wave(p,90,10); assert(std::abs(int(p.bpm)-90)<=2);
  p.update(262143); assert(p.bpm==0 && p.status==PulseTracker::CLIPPED);
  p.reset();
  for(int i=0;i<1500;++i)p.update(30000+(i%3));
  assert(p.bpm==0);
  p.reset(); wave(p,60,10); wave(p,120,10);
  assert(std::abs(int(p.bpm)-120)<=2);
  for(int i=0;i<300;++i)p.update(30000);
  assert(p.bpm==0);
  p.reset(); wave(p,90,10); assert(p.bpm>0);
  p.reset(); assert(p.bpm==0); wave(p,90,1); assert(p.bpm==0);
  // Processing in batches must not alter beat timing or output.
  PulseTracker a,b;
  for(int batch=0;batch<100;++batch){
    uint32_t data[15];
    for(int j=0;j<15;++j){
      data[j]=uint32_t(30000+100*std::sin(6.283185307*72*(batch*15+j)/6000));
      a.update(data[j]);
    }
    for(auto sample:data)b.update(sample);
    assert(a.bpm==b.bpm);
  }
  std::cout << "Pulse tracker synthetic checks passed\n";
}
