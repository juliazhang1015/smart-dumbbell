# Dumbbell Weight Selection Research — 1 kg

**Project:** ECE 198 Smart Dumbbell (CCCARE use case)  
**Research date:** 2026-11-08  
**Design decision:** Select **1 kg (approximately 2.2 lb)** as the **nominal total mass** of the first smart-dumbbell prototype. The existing [project specification](specification.md) sets a **maximum total prototype mass of 1 kg**, including the enclosure, electronics, power source, and any added mass. The finished device has not yet been weighed or evaluated with CCCARE participants.

## 1. User and project context

University of Waterloo's Centre for Community, Clinical and Applied Research Excellence (CCCARE) offers exercise programs for people receiving or recovering from cancer treatment (UW WELL-FIT), people living with the effects of stroke (STEPS), and people experiencing cognitive impairment or dementia (Brain and Body). This means physical abilities and appropriate exercise resistance can vary substantially across participants [1, 2].

Our prototype is intended for CCCARE participants or graduates **who can already perform prescribed bicep curls independently**. The engineering objective is to track exercise activity (e.g., completed repetitions and progress), **not** to prescribe exercise intensity or determine a clinically appropriate weight.

## 2. Evidence on starting weights

| Source | Relevant finding | Design implication |
| --- | --- | --- |
| CDC / Tufts University, *Growing Stronger*, p. 45 [3] | In the weighted phase of its older-adult strength-training program, the guide recommends starting with **2–3 lb** dumbbells (about **0.91–1.36 kg**) and using slow, controlled movements. | A **1 kg / 2.2 lb** prototype falls within this example beginner range. |
| U.S. National Institute on Aging (NIA) [4] | Beginners may start with movements **without weights** and build up gradually; effort depends on ability and health status. | **1 kg is not appropriate for everyone**. The prototype is for a defined, capable user subgroup. |
| CCCARE STEPS program [2] | Exercise specialists individualize plans based on participants' medical history and health status. | Resistance should remain determined by a qualified professional, not by the device. |

**Interpretation:** These sources support 1 kg as a *reasonable lightweight engineering starting point*, not as a universal safe or optimal load for all older adults, stroke survivors, or people undergoing rehabilitation. The CDC range describes one exercise program and is not a CCCARE-specific weight prescription.

## 3. Why the team selected 1 kg

1. **Relevant lightweight reference:** 1 kg is approximately 2.2 lb, within the 2–3 lb introductory weighted-exercise example in the CDC/Tufts guide [3].
2. **Fits the planned demonstration:** A lightweight bicep-curl prototype can demonstrate the project's core features: motion sensing, repetition counting, user feedback, and session logging. These functions do not require a heavier load.
3. **Consistent with the existing project constraint:** The current specification limits the entire smart dumbbell to **no more than 1 kg**. The 1 kg figure refers to the **assembled device**, not a 1 kg weight *plus* electronic components.
4. **Leaves clinical decisions to professionals:** Users with different capabilities may require no weight, less weight, or more weight. The 1 kg prototype is only intended for people whose exercise plan permits it.

## 4. Engineering requirements and verification

- **Mass accounting:** Weigh the complete assembled device, including the enclosure, handle, batteries/power bank, controller, sensors, screen, cables, fasteners, and any ballast. **Target: approximately 1 kg; hard limit under the current specification: 1 kg total.**
- **Do not add 1 kg of ballast:** Calculate any necessary ballast *after* measuring the mass of all installed components.
- **Balance and grip:** Check center of mass, grip comfort, mechanical security, and resistance to slipping. The current CAD model is a packaging study, not evidence of safe handling.
- **Motion-tracking validation:** Test accurate repetition counting at the selected assembled mass and across the intended motion speeds. Log results; do not describe tests as passed until conducted.
- **User-safety boundary:** Do not assume the device is suitable for an individual CCCARE participant without appropriate supervision or professional clearance. Initial student-volunteer bench tests are not a clinical usability study.

**Unverified as of 2026-11-08:** actual finished mass, weight distribution, usability, and suitability for CCCARE participants. Further review is required before claiming any clinical benefit or broad user suitability.

## 5. Conclusion

The team selected **1 kg total prototype mass** for the first Smart Dumbbell. This is a reasonable proof-of-concept target for a light, instrumented bicep-curl demonstrator: **1 kg ≈ 2.2 lb**, within the CDC/Tufts introductory 2–3 lb example. The selection is an **engineering design decision**, not a one-size-fits-all clinical exercise recommendation. Prototype measurements and testing remain outstanding.

## References

1. University of Waterloo, CCCARE, *Programs*. https://uwaterloo.ca/centre-community-clinical-applied-research-excellence/programs
2. University of Waterloo, CCCARE, *STEPS exercise program*. https://uwaterloo.ca/centre-community-clinical-applied-research-excellence/programs/community-programs/steps-exercise-program
3. Seguin, R. A., Epping, J. N., Buchner, D. M., Bloch, R., & Nelson, M. E., *Growing Stronger: Strength Training for Older Adults*, CDC / Tufts University (2002), p. 45 (printed pagination; PDF page 56). https://www.cdc.gov/physicalactivity/downloads/growing_stronger.pdf
4. National Institute on Aging, *Three Types of Exercise Can Improve Your Health and Physical Ability*, section “Muscle-strengthening exercises for older adults.” https://www.nia.nih.gov/health/exercise-and-physical-activity/three-types-exercise-can-improve-your-health-and-physical
