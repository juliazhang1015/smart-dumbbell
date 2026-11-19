// SMART DUMBBELL — PLAN A / v0.7  (right head sized for the power bank's built-in cable)
// Status 2026-11-19: renders in OpenSCAD 2026.10.11 (manifold backend). Not printed, not fitted to
// any real part. Millimetres. Prototype enclosure only: not verified for loads.
//
// Built on the v0.6 draft (not in the repository). Only head_right changes; every other part is
// the v0.6 geometry (v0.4 interfaces), so printed v0.4/v0.6 parts other than head_right stay usable.
//
// Where v0.6 came from: the right head was rebuilt on the v0.4 interfaces; the cap_right windows
// and tabs, the side window and max30102_carrier follow a teammate's CadQuery draft of v0.5.
//
// What changed from v0.6, and why
//   The bank's built-in USB-C cable was measured at 8-9 cm (INIU lists 8 cm). Product photos show a
//   round braided cable leaving one short end of the bank and docking back into the same end as a
//   ring. Its plug has to enter the Nano's USB-C socket, which opens towards the cap at the top edge
//   of the hub board (z = 91), so the cable makes a U-turn above the bank and the board.
//   1. head_right depth 121 -> 140. v0.6 left 27 mm above the USB-C socket; the plug alone needs
//      about that much before the cable can start to bend. The depth is now derived:
//      socket 91 + plug 26 + bend 14 + cable 4 + clearance 2 = 137 inside, + 3 cap = 140.
//   2. The bank sits 16 mm higher (seat 21 -> 37), on taller ribs, so its cable end is level with
//      the top of the plug. In v0.6 the cable had to climb 16 mm first, which an 8-9 cm cable
//      cannot spare.
//   2b. The hub board moves 4 mm towards the bank (board_y 19.8 -> 15.8). The cable's two ends are
//      then 32 mm apart instead of 36. The tallest part on the board, J1 with the 4209 plug, still
//      clears the bank by about 4 mm.
//   3. A second window in the -Y flat for the bank's display. Bank orientation that the two
//      windows assume: cable end towards the cap, pad/display face against the -Y wall.
//   4. part="fit_check" draws the plug and the cable; part="clash" and part="clash_cap" must render
//      empty (see NOTES.md).
//
// Still assumed, not measured (each is one parameter below):
//   plug_above 26, cable_r 14, cable_d 4, bank_root_x 12, the bank's 80 x 38 x 29, and where its
//   button and display are. If plug_above or cable_r turn out larger, the head gets deeper by the
//   same amount; nothing else moves.
//
// Values marked UNMEASURED are catalogue numbers or estimates. Measure the real part first.
part = "assembly";  // head_left head_right cap_left cap_right grip max30102_carrier fit_coupon plate plate_right assembly fit_check clash clash_cap
$fn=96;

// ---------------- shared with v0.4 (do not change, printed parts depend on them) ----------------
hex_R=50;
head_depth=70;                 // left head
cap_t=3;
shell_h=head_depth-cap_t;
wall=3;
grip_od=34;
grip_id=24;
grip_exposed=140;
grip_insert=20;
grip_h=grip_exposed+2*grip_insert;
collar_od=44;
collar_height=14;
grip_clearance=0.45;
lip_clearance=0.4;
bolt_post_xy=[[-28,-22],[-28,22],[28,-22],[28,22]];
post_r=4.6;
apo=hex_R*cos(30)-wall;        // 40.30: centre to an inner flat (flats face +Y and -Y)

// ---------------- right head ----------------
seat_z=21;                     // underside of the hub board; grip end is at z=20

// hub perfboard 30 x 70 x 1.6, component side faces -Y (towards the centre), USB end towards the cap
board_l=70;
board_w=30;
board_t=1.6;
board_y=15.8;                  // component face; solder face is at board_y+board_t (v0.6: 19.8)
slot_w=board_t+0.8;            // 2.4
edge_grip=1.2;                 // slot overlap on each long edge: keep wires and solder off this strip
edge_clr=0.4;
guide_x1=18.5;
guide_h=55;                    // slot length above seat_z

// Nano ESP32 in 8.5 female headers on the board. Its USB-C socket opens at the board's top edge
// (hardware/wiring/gen_perfboard.py: Nano end 1.1 inside the edge, connector overhangs the Nano).
nano_l=45; nano_w=18; nano_t=1.6; nano_sock=8.5;
usb_z=seat_z+board_l;                          // 91   socket opening
usb_y=board_y-nano_sock-nano_t-1.6;            // 4.1  socket centre line

// built-in cable of the bank and its plug
cable_len=85;                  // root to plug tip. Measured 80-90 on 2026-11-19; INIU lists 80.
cable_d=4;                     // UNMEASURED. Round, braided.
cable_r=14;                    // UNMEASURED. Height of the U-turn; docked, the cable is a ring ~30 across.
plug_above=26;                 // UNMEASURED. Stiff part of the plug standing above the socket opening.
plug_in=6.5;                   // metal tip inside the socket
plug_w=12.5; plug_t=6.5;       // UNMEASURED overmould cross-section
bay_clear=2;

// power bank INIU P81, catalogue 80 x 38 x 29 (UNMEASURED). Cable end towards the cap, pad/display
// face against the -Y inner flat.
bank_l=80;
bank_w=38;
bank_t=29;
bank_xh=bank_w/2+0.7;          // 19.7  half pocket width
bank_y0=-apo;                  // -40.3 back
bank_y1=bank_y0+bank_t+0.8;    // -10.5 front stop
bank_seat_z=usb_z+plug_above-bank_l;           // 37   bank top level with the plug top (117)
bank_top_z=bank_seat_z+bank_l;                 // 117
bank_root_x=12;                // UNMEASURED: the cable leaves the end face off-centre; side unknown
bank_root_y=bank_y0+0.2+bank_t/2;              // -25.6
fence_t=2;
fence_h=45;                    // side fence height above bank_seat_z
front_h=30;                    // front post height above bank_seat_z

shell_h_r=bank_top_z+cable_r+cable_d+bay_clear; // 137  inside height to the rim
head_depth_r=shell_h_r+cap_t;                   // 140  (v0.6: 121)

// cable reach: the two ends are cable_span apart; the U-turn is drawn as a half ellipse
cable_span=norm([bank_root_x,usb_y-bank_root_y]);                 // 32.0
function half_ellipse(a,b)=PI/2*(3*(a+b)-sqrt((3*a+b)*(a+3*b)));
cable_path=half_ellipse(cable_span/2,cable_r);                    // 47.3 as drawn
cable_min=cable_span+(PI-2)*8;                                    // 41.2 with 8 mm bends: the least it can be
cable_flex=cable_len-plug_above-plug_in;                          // 52.5 bendable length
echo(str("head_right depth ",head_depth_r,"  inside ",shell_h_r,"  bank seat ",bank_seat_z,"  bank top ",bank_top_z));
echo(str("cable: bendable ",cable_flex,"  path as drawn ",cable_path,"  shortest possible ",cable_min,"  spare ",cable_flex-cable_path));
assert(cable_flex>=cable_min,"the built-in cable cannot reach the Nano: check cable_len and plug_above");

// windows in the -Y flat. Positions follow the bank and come from product photos, not from the
// real unit (UNMEASURED): button about 12 below the cable end, display about 10 above the other end.
// Set either to false to drop it.
side_win=true;                 // button
side_win_w=16;
side_win_z0=bank_top_z-25;     // 92..110 (same place as v0.6; the bank moved up to meet it)
side_win_h=18;
disp_win=true;                 // percentage display
disp_win_w=22;
disp_win_z0=bank_seat_z+3;     // 40..54
disp_win_h=14;

// Adafruit 4517, catalogue 25.4 x 17.8 (UNMEASURED). Long edge along the handle, components towards
// the +Y wall (outwards), as in ml/data-protocol.md mount v1. Glue it in: it must not rattle.
imu_l=25.4;
imu_w=17.8;
imu_t=1.6;
imu_gap=3.4;                   // connector side to the wall
imu_slot=1.9;
imu_z=70;                      // lower edge of the IMU

bolt_tap_r=1.3;                // M3 self-tapping pilot in the far collar wall

// ---------------- right cap (from B, all UNMEASURED against the real modules) ----------------
oled_win=[24,12];              // window, centred on oled_c
oled_c=[0,24];
oled_tab_xy=[[-16,13],[16,13],[-16,35],[16,35]];
oled_tab=[5.5,5.5,4];          // tabs for zip tie or adhesive, not a real screw pitch
oled_tab_hole_d=2.3;
button_xy=[-22,-5];
button_d=6.6;
led_xy=[22,-5];
led_d=4.0;
cap_bank_port=true;            // v0.4 opening at the -Y edge; in this layout it is above the bank end

module hexa(r,h){linear_extrude(height=h)circle(r=r,$fn=6);}
module grip_bore(h){cylinder(h=h,r=grip_od/2+grip_clearance/2,$fn=128);}

// ---------------- v0.4 left head, unchanged ----------------
module shell_left(){
 difference(){
  union(){
   difference(){
    hexa(hex_R,shell_h);
    translate([0,0,wall])hexa(hex_R-wall/cos(30),shell_h-wall+.2);
   }
   translate([0,0,wall])difference(){
    cylinder(h=collar_height,r=collar_od/2,$fn=128);
    translate([0,0,-.15])grip_bore(collar_height+.3);
   }
   for(p=bolt_post_xy) translate([p[0],p[1],wall])cylinder(h=shell_h-wall-0.4,r=post_r,$fn=48);
   for(x=[-20,20],y=[-20,20])translate([x,y,wall])cylinder(h=4,r=3.5,$fn=32);
  }
  translate([0,0,-.15])grip_bore(wall+collar_height+.35);
  translate([-25,0,wall+8])rotate([0,90,0])cylinder(h=50,r=1.8,$fn=40);
  translate([19,0,wall+8])rotate([0,90,0])cylinder(h=6,r=3.25,$fn=6);
  for(p=bolt_post_xy)translate([p[0],p[1],shell_h-13])cylinder(h=13.5,r=1.3,$fn=40);
  for(x=[-20,20],y=[-20,20])translate([x-1.2,y-3,wall+1.2])cube([2.4,6,3.2]);
 }
}

// ---------------- right head ----------------
// Everything inside is a vertical extrusion from the floor: no bridges, no support material.
module post_web(p,h){
 // ties a screw post to the slanted wall behind it
 ang=atan2(sign(p[1])*0.5,sign(p[0])*cos(30));
 translate([p[0],p[1],wall])rotate([0,0,ang])translate([0,-3,0])cube([7,6,h]);
}
module bank_cradle(){
 for(s=[-1,1]){
  // bottom ribs carry the bank at bank_seat_z; they stop short of the grip bore
  translate([s*15-1.2,bank_y0-0.1,wall])cube([2.4,-12-(bank_y0-0.1),bank_seat_z-wall]);
  // side fences on the back wall
  translate([s>0?bank_xh:-bank_xh-fence_t,bank_y0-0.1,wall])cube([fence_t,10.4,bank_seat_z+fence_h-wall]);
  // front L posts
  translate([s>0?16.5:-bank_xh-fence_t,bank_y1,wall])cube([bank_xh+fence_t-16.5,4,bank_seat_z+front_h-wall]);
  translate([s>0?bank_xh:-bank_xh-fence_t,bank_y1-3.5,wall])cube([fence_t,7.5,bank_seat_z+front_h-wall]);
 }
}
module board_guides(){
 gx0=board_w/2-edge_grip;             // 13.8
 gy0=board_y-0.4-1.8;                 // 17.6
 gy1=board_y+board_t+0.4+1.8;         // 23.6
 for(s=[-1,1]){
  translate([s>0?gx0:-guide_x1,gy0,wall])cube([guide_x1-gx0,gy1-gy0,seat_z+guide_h-wall]);
  // brace from the guide to the +Y wall
  translate([s>0?guide_x1-2:-guide_x1,gy1-0.1,wall])cube([2,apo-gy1+0.2,seat_z+guide_h-wall]);
 }
}
module board_slots(){
 sx0=board_w/2-edge_grip;             // 13.8
 sx1=board_w/2+edge_clr;              // 15.4
 for(s=[-1,1])
  translate([s>0?sx0-0.01:-sx1,board_y-0.4,seat_z])cube([sx1-sx0+0.01,slot_w,guide_h+1]);
}
module imu_rails(){
 ry0=apo-imu_gap-imu_t-1.7;           // 33.6
 for(s=[-1,1])
  translate([s>0?imu_w/2-1.2:-imu_w/2-2.5,ry0,wall])cube([3.7,apo-ry0+0.1,imu_z+imu_l+5-wall]);
}
module imu_slots(){
 sy0=apo-imu_gap-imu_t-(imu_slot-imu_t)/2;
 for(s=[-1,1])
  translate([s>0?imu_w/2-1.21:-imu_w/2-0.3,sy0,imu_z])cube([1.51,imu_slot,imu_l+6]);
}
module shell_right(){
 h=shell_h_r;
 difference(){
  union(){
   difference(){
    hexa(hex_R,h);
    translate([0,0,wall])hexa(hex_R-wall/cos(30),h-wall+.2);
   }
   translate([0,0,wall])difference(){
    cylinder(h=collar_height,r=collar_od/2,$fn=128);
    translate([0,0,-.15])grip_bore(collar_height+.3);
   }
   for(p=bolt_post_xy){
    translate([p[0],p[1],wall])cylinder(h=h-wall-0.4,r=post_r,$fn=48);
    post_web(p,h-wall-2.2);           // web stops below the cap lip
   }
   bank_cradle();
   board_guides();
   imu_rails();
  }
  translate([0,0,-.15])grip_bore(wall+collar_height+.35);
  // cross bolt M3x45: clearance through the near collar wall, self-tapping pilot in the far one
  translate([-25,0,wall+8])rotate([0,90,0])cylinder(h=25,r=1.8,$fn=40);
  translate([0,0,wall+8])rotate([0,90,0])cylinder(h=25,r=bolt_tap_r,$fn=40);
  // access for the bolt and a screwdriver through the -X corner
  translate([-hex_R-1,0,wall+8])rotate([0,90,0])cylinder(h=hex_R+1-23,r=3.3,$fn=48);
  for(p=bolt_post_xy)translate([p[0],p[1],h-13])cylinder(h=13.5,r=1.3,$fn=40);
  board_slots();
  imu_slots();
  // side window through the -Y flat (idea from B)
  if(side_win)
   translate([-side_win_w/2,-hex_R*cos(30)-1,side_win_z0])cube([side_win_w,wall+2,side_win_h]);
  if(disp_win)
   translate([-disp_win_w/2,-hex_R*cos(30)-1,disp_win_z0])cube([disp_win_w,wall+2,disp_win_h]);
 }
}

// ---------------- caps ----------------
module cap(right=false){
 difference(){
  union(){
   hexa(hex_R,cap_t);
   translate([0,0,cap_t])difference(){
    hexa(hex_R-wall/cos(30)-lip_clearance,1.7);
    translate([0,0,-.1])hexa(hex_R-wall/cos(30)-lip_clearance-1.4,1.9);
   }
   // OLED mounting tabs on the inside (from B)
   if(right)for(p=oled_tab_xy)
    translate([p[0]-oled_tab[0]/2,p[1]-oled_tab[1]/2,cap_t-0.01])cube([oled_tab[0],oled_tab[1],oled_tab[2]+0.01]);
  }
  for(p=bolt_post_xy){
   translate([p[0],p[1],-.2])cylinder(h=5.2,r=1.75,$fn=40);
   translate([p[0],p[1],-.2])cylinder(h=1.7,r=3.3,$fn=48);
   translate([p[0],p[1],cap_t+0.01])cylinder(h=2,r=post_r+0.6,$fn=48);   // lip notch at the screw post
  }
  if(right){
   translate([oled_c[0]-oled_win[0]/2,oled_c[1]-oled_win[1]/2,-.2])cube([oled_win[0],oled_win[1],cap_t+.4]);
   for(p=oled_tab_xy)translate([p[0],p[1],cap_t-1])cylinder(h=oled_tab[2]+2,r=oled_tab_hole_d/2,$fn=32);
   translate([button_xy[0],button_xy[1],-.2])cylinder(h=cap_t+.4,r=button_d/2,$fn=48);
   translate([led_xy[0],led_xy[1],-.2])cylinder(h=cap_t+.4,r=led_d/2,$fn=48);
   if(cap_bank_port)translate([-6,-36,-.2])cube([12,7,5.3]);
  }
 }
}

// ---------------- pulse sensor carrier (from B, unchanged) ----------------
module max30102_carrier(){
 difference(){
  translate([-10,-9,0])cube([20,18,2.5]);
  for(x=[-7.5,7.5])translate([x-1.1,-5,-1])cube([2.2,10,5]);
 }
}

// ---------------- grip and coupon, unchanged from v0.4 ----------------
module grip(){
 difference(){
  union(){
   cylinder(h=grip_h,r=grip_od/2,$fn=144);
   for(z=[grip_insert+9:9:grip_insert+grip_exposed-8])
    translate([0,0,z])difference(){
     cylinder(h=1.1,r=17.35,$fn=144);
     translate([0,0,-.1])cylinder(h=1.3,r=16.99,$fn=144);
    }
  }
  translate([0,0,-.2])cylinder(h=grip_h+.4,r=grip_id/2,$fn=144);
  translate([-7,10.5,grip_h/2-10])cube([14,18,20]);
  for(z=[9,grip_h-9])
   translate([-20,0,z])rotate([0,90,0])cylinder(h=40,r=1.8,$fn=40);
 }
}
module fit_coupon(){
 difference(){
  union(){
   cylinder(h=12,r=collar_od/2,$fn=96);
   translate([20,-10,0])cube([24,20,8]);
  }
  translate([0,0,-.2])grip_bore(12.5);
  translate([27,0,-.2])cylinder(h=8.5,r=1.75,$fn=40);
  translate([37,0,-.2])cylinder(h=8.5,r=1.3,$fn=40);
 }
}

// ---------------- component envelopes (for the fit view and the clash checks only) ----------------
module env_bank(lift=0){translate([-bank_w/2,bank_y0+0.2,bank_seat_z+lift])cube([bank_w,bank_t,bank_l]);}
module env_board(){translate([-board_w/2,board_y,seat_z])cube([board_w,board_t,board_l]);}
module env_nano(){
 // sockets, Nano PCB and the USB-C receptacle
 translate([-nano_w/2,board_y-nano_sock,usb_z-1.1-nano_l])cube([nano_w,nano_sock,nano_l]);
 translate([-nano_w/2,board_y-nano_sock-nano_t,usb_z-1.1-nano_l])cube([nano_w,nano_t,nano_l]);
 translate([-4.5,usb_y-1.6,usb_z-7.5])cube([9,3.2,7.5]);
}
module env_plug(){translate([-plug_w/2,usb_y-plug_t/2,usb_z])cube([plug_w,plug_t,plug_above]);}
// J1 with the 4209 plug in it: the tallest thing on the board, 22.5 (estimate in gen_perfboard.py), at row 19.
// Drawn across the full board width because the drawing does not fix which side columns A-D are on.
module env_j1(){translate([-12.7,board_y-22.5,usb_z-5.79-18*2.54-1.3])cube([25.4,22.5,2.6]);}
module env_imu(){translate([-imu_w/2,apo-imu_gap-imu_t,imu_z])cube([imu_w,imu_t,imu_l]);}
// U-turn from the bank's cable root to the top of the plug, a half ellipse cable_r high
function cable_pt(t)=let(a=cable_span/2,
  c=[bank_root_x/2,(bank_root_y+usb_y)/2,bank_top_z],
  u=[-bank_root_x,usb_y-bank_root_y,0]/cable_span)
  c+u*(-a*cos(t))+[0,0,cable_r*sin(t)];
module env_cable(){
 for(t=[0:6:174])hull(){
  translate(cable_pt(t))sphere(d=cable_d,$fn=20);
  translate(cable_pt(t+6))sphere(d=cable_d,$fn=20);
 }
}
// the bank rests on its ribs: lift it a hair so that the contact face does not count as a clash
module envelopes(){env_bank(0.02);env_board();env_nano();env_j1();env_plug();env_imu();env_cable();}
module cap_installed(){translate([0,0,shell_h_r+cap_t])rotate([0,180,0])cap(true);}

module assembly(){
 color("#348aa7",0.45)shell_right();
 // the cap is modelled outer face down; installed it is turned over about the Y axis, so +Y stays +Y
 color("#95cfe2",0.6)cap_installed();
 color("#55646f")translate([0,0,-grip_exposed-grip_insert])grip();
 color("#418b9d")translate([0,0,-grip_exposed])mirror([0,0,1])shell_left();
 color("#94c3d5")translate([0,0,-grip_exposed-shell_h-cap_t])cap(false);
 color("#ff9800")env_bank();
 color("#3a9a60")env_board();
 color("#1565c0")env_nano();
 color("#9c27b0")env_imu();
 color("#8d6e63")env_j1();
 color("#222222")env_plug();
 color("#e53935")env_cable();
}
// right head cut open along the Y-Z plane, with everything that goes inside
module fit_check(){
 color("#348aa7")difference(){shell_right();translate([0,-hex_R-5,-5])cube([hex_R+5,2*hex_R+10,head_depth_r+10]);}
 color("#95cfe2")difference(){cap_installed();translate([0,-hex_R-5,-5])cube([hex_R+5,2*hex_R+10,head_depth_r+10]);}
 color("#ff9800")env_bank();
 color("#3a9a60")env_board();
 color("#1565c0")env_nano();
 color("#9c27b0")env_imu();
 color("#8d6e63")env_j1();
 color("#222222")env_plug();
 color("#e53935")env_cable();
}

// ---------------- print plate: the six production parts in print orientation, one file ----------------
// Heads stand on their closed floor, open end up. Caps lie on their outer face, lip up. The grip stands
// upright in the gap between the four hexagons. 212 x 186 footprint, 180 tall.
plate_gap=12;
module plate(){
 dx=hex_R+plate_gap/2;               // 56
 dy=hex_R*cos(30)+plate_gap/2;       // 49.3
 translate([ dx, dy,0])shell_right();
 translate([-dx, dy,0])shell_left();
 translate([ dx,-dy,0])cap(true);
 translate([-dx,-dy,0])cap(false);
 grip();
 translate([2*dx-16,0,0])rotate([0,0,90])max30102_carrier();
}

// the two parts that are new relative to the v0.4 set already sent for printing: right head and right cap
module plate_right(){
 dy=hex_R*cos(30)+plate_gap/2;       // 49.3
 translate([0, dy,0])shell_right();
 translate([0,-dy,0])cap(true);
}

if(part=="head_left")shell_left();
else if(part=="head_right")shell_right();
else if(part=="cap_left")cap(false);
else if(part=="cap_right")cap(true);
else if(part=="grip")grip();
else if(part=="max30102_carrier")max30102_carrier();
else if(part=="fit_coupon")fit_coupon();
else if(part=="plate")plate();
else if(part=="plate_right")plate_right();
else if(part=="fit_check")fit_check();
else if(part=="clash")intersection(){shell_right();envelopes();}
else if(part=="clash_cap")intersection(){cap_installed();envelopes();}
else assembly();
