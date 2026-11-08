# Update presentation, Tuesday 10 Nov 09:10: script, Q&A notes, checklist

Format: 7 minutes of progress + 8 minutes of Q&A per the instructor announcement (the project overview PDF said 5 + 5), prototype in hand, laptop allowed. The teaching team "will be looking for progress, but we aren't expecting a finished project". A late presenter loses 50 % at once, an absence scores 0: **the whole group is there before 09:10.**

Slides: `presentation/Smart_Dumbbell_Update_2026-11-10.pptx` (8 slides, UW Engineering template; PDF next to it for offline use; speaker notes in the file; rebuilt from `presentation/build_update_deck_2026-11-10.py`). The script below is timed per slide, 4 minutes 30 seconds in total, leaving 30 seconds to hold up the bench rig.

## 1. Script (4:30)

The script runs about 4:30 against a 7-minute slot. Spend the spare time on the bench demonstration after slide 2 and on a slower pace; do not add slides.

**Slide 1, cover (0:20)**
We are Group 57. Our project is a smart dumbbell for CCCARE's at-home rehab participants. The dumbbell itself recognizes and counts bicep curls, reads heart rate at the grip, and logs each set to a laptop. What you see on the right is a concept render, not the prototype. The prototype is here on the table.

**Slide 2, status in three columns (0:40)**
Three weeks after parts arrived, every module works on the bench and the system is about half integrated. On the left: the controller, the IMU, the pulse sensor and the display all share one I2C bus with no conflicts; the IMU streams at 104 hertz; Wi-Fi works; an integrated firmware with one button, display, pulse sampling and the model call has run on the board. Also merged this week: the schematic drawn in EasyEDA and Zoe's Bluetooth web dashboard. In the middle, this week: we are rewiring the bench after the first breadboard failed; the rep counter and the heart-rate detector in the integrated app are placeholders that still need tuning on real motion; the recording rig is ready. On the right, honestly not started: a model trained on real data, the device-side Bluetooth service for the dashboard, all ten acceptance tests, and the printed enclosure.
(If the bench is wired: hold it up here, press the button, say "This is the bench version; the counter is a placeholder", put it down within 20 seconds.)

**Slide 3, bench measurements (0:45)**
This is the schematic as built, and the numbers we read from the serial port. Four of four I2C devices; 104.0 hertz with zero lost samples while the display is on; pulse sampling at 100 hertz; model inference 2.3 milliseconds; button events logged. Two things are not done: the rep counter has not been tested on a real curl, and the heart-rate value is still 9 to 14 beats high. One bug we found and fixed: the display library quietly dropped the bus to 100 kilohertz and a full-frame refresh delayed IMU samples, so we now send the frame in 64-byte chunks between samples.

**Slide 4, counting and classification (0:45)**
Counting is two parts. A classifier looks at 2-second windows of IMU data, computes 31 simple features and runs logistic regression on the Nano: curl, idle or other. A counter watches the gyro for an up-then-down cycle, and it only counts while the label is curl. Either part alone fails: the counter alone counts any swing, the classifier alone cannot tell one rep from two. Status: the training pipeline and the on-device code agree to one part in a million, but only on synthetic data; the counter thresholds are guesses and have not been tested on a real curl. Real recordings start this week, and we evaluate by person, never by random windows. Targets: macro-F1 at least 0.85, count within one on 18 of 20 sets. Those are proposed targets, not results.

**Slide 5, training data (0:35)**
You will ask where the training data comes from, so here is the plan. Until the enclosure is printed we tape the IMU to a three-pound hex dumbbell, X axis along the grip, photograph that orientation and never change it; the printed head mounts the sensor the same way. Six people with anonymous IDs, each recording slow, normal and fast curls, three kinds of idle, two minutes of other movements and a minute of half reps, as 104 hertz CSV over USB. We evaluate by person, never by random windows. The weight: we record at 0.9 and 1.4 kilograms, a 2 and a 3 pound dumbbell, bracketing our target. The specification says no more than 1 kilogram and no added training ballast, and the evidence supports that: senior strength classes use 1 to 3 pound dumbbells and early cardiac rehab starts at 1 to 5. As of today we have zero recordings; the first three people are this week.

**Slide 6, heart rate (0:45)**
Heart rate at the grip is our biggest open risk, and we want your advice on it. At rest, with a still finger, the pulse is only 0.1 to 0.4 percent of the DC level, and our best offline estimate is 9 to 14 beats above a watch reading 86. The library's beat detector is worse; a band-pass and peak-picking replacement is planned but not on the board yet. A curl is about one hertz, the same band as heart rate, so motion will make it harder, not easier. The firmware already does the safe thing: no finger, too few beats or stale data shows dashes and logs invalid. Next: the new detector, a borrowed reference device, and a 60-second synchronized comparison. The question is whether we should restate the requirement before we freeze the test method.

**Slide 7, enclosure, plan, questions (0:40)**
The enclosure: electronics and the 5000 milliamp-hour power bank in one hex head, steel washers to balance the other, the pulse sensor flush in the grip. Total mass no more than 1 kilogram, as the specification says; the washers only balance the two heads. The first print is this week. The road to the 25th: real model and offline counter next week; model on the device and the assembled dumbbell the week after; freeze on the 22nd and rehearse. On the 25th we want to show a 90-second loop: start, ten counted curls, a swing that does not count, grip heart rate, and the set appearing on the laptop. Three questions for you. One: may we restate the in-motion heart-rate requirement? Two: what does the symposium look like, a table, power, how long per visitor? Three: we have spent 120 dollars of our own; is a 200-dollar ceiling reasonable?

**Slide 8, questions**
Stay on this slide. Read the three questions first so the teaching team answers them, then take their questions.

## 2. Suggested speaker assignment

| Slides | Speaker | Note |
|---|---|---|
| 1–2 | Hanson | Also holds up the bench rig (it is on his desk) |
| 3 | Zoe | Hardware owner presents the measurements |
| 4 | Julia | Counting line; Hanson adds one sentence on classification |
| 5 | Hanson | Data collection and the weight evidence (classification line) |
| 6 | Zoe | Heart rate belongs to the hardware line |
| 7 | Eric | Enclosure, plan, questions |
| 8 | All | Q&A page: the three questions; stay here for asking and answering |

All four should speak; the teaching team is assessing the team. Everyone reads their part of the script before Tuesday.

## 3. Q&A preparation (8 minutes)

| Likely question | Answer |
|---|---|
| Why not the R4 Minima the course provides? | 32 kB SRAM cannot hold the model plus Wi-Fi; its 3.3 V pin cannot power a Wi-Fi module; the Nano ESP32 solves both on one board (decisions.md, 31 Oct). The R4 stays for bench debugging. |
| Why buy an IMU? | The borrowed ADXL335 has no gyroscope; curl counting needs angular rate. The LSM6DSOX has a gyro, I2C and 104 Hz. |
| How big is the model, does it run on the board? | Logistic regression on 31 features, a few kB; measured inference 2.3 ms, Flash 10 %, RAM 12 %. |
| Where does the data come from, is it enough? | Slide 5: temporary rig plus six anonymous volunteers, at least 10 minutes per class, evaluated by person. Zero people so far; this is the largest gap. |
| Why 1 kg? | Specification: no more than 1 kg, no added training ballast in Version 1. The evidence agrees: senior strength classes ask for 1–3 lb, early cardiac rehab stays at 1–5 lb, the CCCARE material prescribes load per person, starts light and progresses at 20 reps. Recordings at 0.9 and 1.4 kg bracket the target. 5 kg is above every range we found. |
| Why both Wi-Fi and Bluetooth? | The specification says Wi-Fi, and the hotspot does not depend on campus Wi-Fi; Bluetooth is the dashboard route Zoe built, simpler to connect and lower power. Both can carry the same record; the logger does not need rewriting. We would like the teaching team's view. |
| What if in-motion heart rate cannot be done? | Honestly, the requirement as written is unlikely. The fallback is readings when signal quality allows, guaranteed readings between sets, invalid flagged as invalid; we came with the data to ask whether that restatement is acceptable. |
| How do you keep a shake from counting? | Two gates: the classifier label must be curl, and the counter needs a full raise-and-lower cycle; half reps and stalls do not count. AT-03 tests 20 interference cases. |
| Why not a phone app? | Older users: one button and one display, no phone to operate; the data reaches the laptop automatically for the kinesiologist. |
| What will you demo on 25 Nov? | A 90-second loop: start, ten counted curls, a swing not counted, grip heart rate, the set logged on the laptop. If the model is not ready, counter only, said plainly. |
| Over budget? | CAD 120 of our own so far, over the original 100; the enclosure print is about 60–80 more. We want to confirm a 200 ceiling. |
| Why one button instead of three? | Older users find one large button more easily than three small ones; short press start/pause, long press end, already in firmware. The specification still says three; it changes once the team confirms. |

If you do not know, say "We haven't measured that yet" and how you will; do not invent numbers.

## 4. Before Tuesday

**Saturday night / Sunday**

- [ ] Hanson: rewire the half-size breadboard per `hardware/wiring/halfboard-v1.png`; `bus_check` gives `rc=0` on all four addresses; flash `firmware/app`; the display shows `IDLE 0/10`. If it does not work, leave the rig at home; the slides do not change.
- [ ] Hanson: read through the slides, fix wording; keep the PDF locally in case there is no network.
- [ ] All: read your own slide's script; confirm in the group chat who speaks when.
- [ ] Zoe: have the numbers from the MAX30102 at-rest record (already on slide 6).
- [ ] Eric: if a newer CAD screenshot exists, swap the slide 7 figure; otherwise the layout drawing stays.

**Tuesday morning**

- [ ] Arrive 08:40; laptop charged; PDF local; the rig powered from the laptop's USB (not the power bank: one variable fewer).
- [ ] Power the rig once in the corridor and check the display before going in.
- [ ] Bring: the Nano rig, two USB-C cables, the spare Nano if there is one, this file printed or open on a phone.
- [ ] Afterwards, write the teaching team's answers to the three questions into `docs/decisions.md` the same day.
