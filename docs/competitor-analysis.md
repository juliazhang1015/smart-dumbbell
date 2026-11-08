# Smart Dumbbell: Market Research and Competitor Analysis

**ECE 198 — Group 57**  
**Research snapshot:** 2026-11-08  
**Status:** Desk research, not competitive product testing or user validation. All described product features are manufacturer/retailer claims unless explicitly noted. Listings and prices may change.

## 1. Research question and user context

**Question:** How does our proposed lightweight at-home smart dumbbell compare with existing adjustable/connected dumbbells and simple low-cost strength-training options?

Our intended users are CCCARE graduates/participants **who can independently perform prescribed bicep curls at home**. This is not a general clinical device and does not prescribe exercises, diagnose conditions or certify form.

The current project baseline ([specification](specification.md), [decisions](decisions.md)) calls for:
- **One exercise:** bicep curl; planned model labels `curl`, `idle`, `other`.
- **Motion:** Nano ESP32 with the Adafruit LSM6DSOX + LIS3MDL board (product 4517); only accelerometer + gyroscope planned for v1 inference. A valid repetition requires a complete movement cycle, not just a positive classification window.
- **Heart rate:** borrowed GY-MAX30102, with explicit invalid/signal-quality status; **reliable readings while moving have not been demonstrated**.
- **Interaction:** OLED and **three physical buttons**, target set on the computer, on-device progress feedback, local Wi-Fi and computer CSV logging; no personal smartwatch required.
- **Physical design:** proposed total prototype mass **<=1 kg**, no added exercise ballast in v1, custom hollow enclosure; mechanical fit and grip performance still unverified.
- **Cost:** the original purchase ceiling was CAD 100 including taxes/shipping, but [decisions](decisions.md) record spending CAD 119.55 by 2026-11-01; an updated ceiling remains to be agreed. **Do not claim the current prototype costs less than CAD 100**.

These are design requirements/targets, **not proven performance**.

## 2. Competitor comparison

Weights below are **per dumbbell unless noted**, and prices are **not normalized for currency, number of units, subscriptions or sales tax**. An unverified current price is recorded as such rather than estimated.

| Product / category | Intended use and weight | Relevant documented features | Price / availability evidence | Relevance or limitation for our project |
|---|---|---|---|---|
| **Kabata AI Dumbbells** | Connected strength-training dumbbells; approximately **5–60 lb (2.3–27.2 kg)** per dumbbell | Onboard motion sensing; advertised rep tracking, form feedback/coaching, and electronically adjustable resistance/weight; connected experience | **Premium connected product.** Confirm current checkout total, subscription terms and stock for the relevant region before quoting a price. | Closest **feature competitor** for integrated movement tracking. Our focus differs: lightweight, one prescribed curl exercise, simple physical controls and experimental integrated heart-rate sensing. Kabata's existence means rep counting/AI feedback alone is **not** a novel claim. |
| **BowFlex SelectTech 560** | Home strength training, adjustable approximately **5–60 lb (2.3–27.2 kg)** | Advertised **3DT** motion tracking, repetition and set recording, and Bluetooth-connected training information | **Legacy/discontinued model**; current retail price not used. | Demonstrates motion sensing built into a dumbbell predates our concept; useful engineering precedent but not a currently equivalent lightweight rehab product. |
| **JAXJOX DumbbellConnect** | Connected adjustable strength training; approximately **8–50 lb (3.6–22.7 kg)** | Electronic weight selection, connected workouts and repetition tracking | Historical product and reviews; **current app/service support and new-product availability must be checked**. Historic reviews are **not** present-day price evidence. | Adjustable/connected alternative, but entry weight and dependence on connected ecosystem may not fit all intended users. Do not claim it is actively sold today. |
| **Xiaowo Smart Dumbbell** (Red Dot design entry) | A smart-dumbbell design with adjustable/removable weight components | Award/design description reports integrated sensing for **heart rate and blood oxygen**, plus a charging/storage arrangement | **Design-award entry, not verified current retail availability or clinical measurement performance.** Price unknown. | Important **prior-art/design precedent**: integrating heart-rate sensing into a dumbbell is not, by itself, unprecedented. Evidence is design documentation, not an independent accuracy study. |
| **PowerBlock Sport 24** | Conventional adjustable dumbbells for home exercise, **3–24 lb (1.4–10.9 kg)** | Manual weight selection, compact adjustable-weight approach; no embedded rep/heart-rate monitoring claimed | See current manufacturer pricing; confirm whether listing is for a **pair** and whether it ships to Canada. | Mechanical comparator for weight adjustment and grip/size; lacks automatic session logging. |
| **DOMYOS / Decathlon 1 kg dumbbells** | Simple lightweight beginner exercise, **1 kg per dumbbell** in a twin pack | No electronics; simple lift-and-set-down interaction | Canadian retail listing; verify current **CAD** price and stock before using in a report budget. | Strong **low-cost, low-complexity baseline**. A paper checklist or basic app plus a conventional dumbbell is an alternative that our design must justify outperforming in usability/value. |

### Original product/source links

1. **Kabata:** [manufacturer technology page](https://www.kabatafitness.com/tech) and [manufacturer website](https://www.kabatafitness.com/).
2. **BowFlex SelectTech 560:** [BowFlex Canada product page](https://www.bowflex.ca/products/selecttech-560-dumbbells).
3. **JAXJOX DumbbellConnect:** [Live Science product review](https://www.livescience.com/jaxjox-dumbbellconnect-review) — secondary/historical evidence; do not use it to establish present-day availability.
4. **Xiaowo Smart Dumbbell:** [Red Dot Design Award project entry](https://www.red-dot.org/project/smart-dumbbell-56893) — design/award evidence only.
5. **PowerBlock:** [manufacturer adjustable-dumbbell comparison](https://powerblock.com/pages/compare-powerblock-adjustable-dumbbells).
6. **Decathlon:** [Decathlon Canada 1 kg twin-pack listing](https://www.decathlon.ca/en/p/dumbbells-twin-pack-1-kg-2-2-lb/130386/c344c344m8336571).

**Source caveat:** Page contents, stock, model lineup and pricing may change after this snapshot. Manufacturer marketing claims are not independent proof of rep-counting accuracy, older-adult usability or optical pulse performance. Check live checkout screenshots for any final CAD price comparison, and record unit count, date, taxes, exchange rate and subscription assumptions.

## 3. Interaction workflows

The following are **high-level interaction interpretations**, not observational usability measurements.

| Solution | Typical user steps | Potential friction to investigate |
|---|---|---|
| Connected adjustable dumbbell (Kabata / historical JAXJOX) | Set weight / configure connected workout → grip and lift → review feedback or recorded sets | Setup, weight adjustment, device connectivity, screen/app familiarity, ongoing service support |
| Motion-tracking adjustable dumbbell (historical SelectTech 560) | Choose resistance → perform exercise → sync or review data | Device complexity and heavier minimum weight compared with a lightweight concept |
| Conventional 1 kg dumbbells + paper log | Pick up dumbbell → perform prescribed exercise → manually write counts | Manual log may be forgotten or miscounted; cannot directly measure heart rate |
| **Our proposal (not tested)** | Set target on computer → press physical controls → exercise while reading OLED → review local computer record | Computer setup, on-grip optical contact during motion, display readability and correct classification still need testing |

## 4. Three evidence-based needs and a potential gap

1. **Approachable exercise hardware.** Unlike common 5 lb+ connected/adjustable dumbbells, the team's planned prototype is **<=1 kg total mass**. This is a design target, **not proof of appropriateness for all older adults**. Suitable resistance depends on the prescribed activity and individual assessment.
2. **Low-friction recording of prescribed repetitions.** Existing connected products show that automated tracking is feasible in commercial systems, while a conventional dumbbell requires separate logging. The project could provide targeted curl counting with fewer moving parts and simpler controls, **if its counting and interface meet the acceptance tests**.
3. **Transparent heart-rate data quality.** A heart-rate number during gripping/movement is technically challenging: motion, contact pressure, ambient light and sensor geometry may degrade optical measurements. Providing an explicit invalid status is more defensible than always displaying a number. Independent testing is required before safety or accuracy claims.

**Proposed market opportunity (hypothesis):** A simple, low-mass, no-smartwatch-required device for independently prescribed at-home curls that combines **on-device count/progress, validity-aware experimental heart-rate measurements, and local computer records**. The claim is about **integration and user focus**, not being the first smart, AI, or heart-rate-enabled dumbbell.

## 5. Design implications for ECE198 v1

| Competitive observation | Project response (current baseline or proposed investigation) | Evidence required |
|---|---|---|
| AI rep counting already exists | Limit v1 to reliable bicep-curl cycle counting and `curl/idle/other` classification | Held-out classification metrics; counts for complete, partial, paused and unrelated movements (AT-01 to AT-03) |
| Adjustable products often start at several pounds | Prototype a **<=1 kg** hollow enclosure without added ballast; test ergonomics against an ordinary 1 kg dumbbell | Actual assembled mass, grip dimensions, retention, comfort and accessibility observations (AT-09/10) |
| Screen/app complexity may be a barrier | Physical **three-button** controls and clear **OLED** information, with local Wi-Fi + computer CSV | Timed usability tasks; visibility/readability feedback; offline/disconnection tests |
| Heart-rate-enabled dumbbell concepts already exist | Prioritize feasibility of **GY-MAX30102 while curling**, signal quality and invalid-value handling | Synchronized reference readings and valid-output coverage + MAE during movement (AT-04 to AT-06) |
| Low-tech dumbbells are inexpensive | Compare overall benefit and total implementation cost against **1 kg dumbbell + manual log** | Dated CAD bill of materials, accessory/subscription requirements, actual purchase totals and a documented value argument |

The [CDC guidance for older adults](https://www.cdc.gov/physical-activity-basics/guidelines/older-adults.html) identifies muscle-strengthening activity as part of an overall activity program. **It does not validate our specific dumbbell weight, exercise plan or heart-rate thresholds**.

For technical caution, see [Analog Devices: optical biosensing error sources](https://www.analog.com/en/resources/design-notes/how-common-noise-and-error-sources-affect-optical-biosensing.html) and the [MAX30102 manufacturer page](https://www.analog.com/en/products/max30102.html). These support why contact and motion effects must be investigated, not a claim that our sensor meets AT-04/05.

## 6. Follow-up research and validation

- [ ] Capture date-stamped Canada-specific prices for at least three comparable products or alternatives, explicitly marking **currency, pair vs single, shipping, taxes and subscriptions**. Do not mix historical/list/promotional prices.
- [ ] Confirm manufacturer specification details against the exact models sold in Canada; archive bibliographic notes rather than reproducing proprietary marketing photos.
- [ ] Compare the actual prototype's dimensions, mass and handle feel with a lightweight conventional dumbbell.
- [ ] Test older-adult interface assumptions with appropriate approved representative users; do not present student testing as clinical validation.
- [ ] Evaluate motion-model performance and optical signal validity against the repository's acceptance-test methods.
- [ ] Reconcile the current **CAD 119.55** purchase total and obtain a documented revised budget before claiming affordability.

## 7. Summary for a report or presentation

Commercial smart dumbbells demonstrate that connected repetition tracking, embedded sensing and automated coaching are established product features. An award-documented smart-dumbbell design has also proposed optical physiological monitoring. Lightweight conventional dumbbells provide a much simpler and less expensive alternative, but without integrated sensing or automated session records. Our concept targets a narrower at-home use case: a **<=1 kg** bicep-curl device with on-device cycle counting, an OLED and three buttons, experimental during-movement heart-rate capture with validity flags, and local computer logging. Its distinctiveness will depend on measured usability, sensing performance and a credible total-cost comparison—not on broad claims of first-to-market innovation.

---

*Prepared by Julia Zhang using public product information and the repository's specification/decision files. Team review and additional evidence are required before inclusion in final assessed deliverables. No competitive hardware was purchased or tested as part of this research.*
