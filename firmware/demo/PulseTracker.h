#pragma once
#include <stdint.h>
#include <math.h>

// One update per FIFO sample, at exactly 100 Hz (400 Hz / averaging of 4).
// Engineering heuristic, not a validated motion-artifact classifier.
class PulseTracker {
public:
  static constexpr uint32_t CONTACT_ON = 10000;
  static constexpr uint32_t CONTACT_OFF = 7000;
  static constexpr float MIN_AMPLITUDE = 20.0f;
  enum Status { NO_CONTACT, SETTLING, WEAK, ACQUIRING, TRACKING, CLIPPED };
  Status status = NO_CONTACT;
  unsigned bpm = 0;
  uint32_t raw = 0;
  float ac = 0, envelope = 0;

  void reset() { *this = PulseTracker(); }
  void update(uint32_t ir) {
    raw = ir;
    if (ir >= 260000) { reset(); raw = ir; status = CLIPPED; return; }
    if (ir < (contact ? CONTACT_OFF : CONTACT_ON)) {
      reset(); raw = ir; return;
    }
    if (!contact) { contact = true; dc = float(ir); }
    ++samples;
    // Remove slow baseline changes; suppress high-frequency noise.
    dc += 0.02f * (float(ir) - dc);
    ac += 0.25f * ((float(ir) - dc) - ac);
    envelope *= 0.995f;
    if (fabsf(ac) > envelope) envelope = fabsf(ac);
    if (samples < 80) { status = SETTLING; return; }
    if (lastBeat && samples - lastBeat > 200) {
      bpm = 0; count = 0; next = 0; lastBeat = 0;
    }
    if (envelope < MIN_AMPLITUDE) {
      bpm = 0; count = 0; next = 0; lastBeat = 0; armed = false;
      status = WEAK; return;
    }
    float threshold = fmaxf(MIN_AMPLITUDE * 0.5f, envelope * 0.35f);
    if (ac < -threshold) armed = true;
    if (armed && ac > threshold) {
      armed = false;
      if (!lastBeat) lastBeat = samples;
      else {
        uint32_t interval = samples - lastBeat;
        // Ignore double triggers without moving the preceding beat timestamp.
        if (interval >= 30) {
          lastBeat = samples;
          if (interval <= 150) {
            intervals[next] = interval;
            next = (next + 1) % 3;
            if (count < 3) ++count;
            // Require two similar intervals before displaying any estimate.
            if (count >= 2) {
              uint32_t lo = intervals[0], hi = lo, sum = 0;
              for (unsigned i = 0; i < count; ++i) {
                if (intervals[i] < lo) lo = intervals[i];
                if (intervals[i] > hi) hi = intervals[i];
                sum += intervals[i];
              }
              bpm = (hi - lo <= lo / 4) ? (6000 * count + sum / 2) / sum : 0;
            }
          } else { count = 0; next = 0; bpm = 0; }
        }
      }
    }
    status = bpm ? TRACKING : ACQUIRING;
  }
  const char* label() const {
    switch (status) {
      case NO_CONTACT: return "Place finger";
      case SETTLING: return "Settling";
      case WEAK: return "Weak signal";
      case ACQUIRING: return "Hold steady";
      case TRACKING: return "Tracking";
      case CLIPPED: return "IR saturated";
    }
    return "Unknown";
  }
private:
  bool contact = false, armed = false;
  float dc = 0;
  uint32_t samples = 0, lastBeat = 0, intervals[3] = {};
  unsigned count = 0, next = 0;
};
