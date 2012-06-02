translate([145, 115, 9.5]) rotate([0, 0, 0]) import_stl("bearing-holder-fixed.stl");
translate([120, 131, 0]) rotate([0, 0, -120]) import_stl("y-motor-split2.stl");
translate([108, 71, 9.5]) rotate([0, 0, 0]) import_stl("bearing-holder-float.stl");
translate([112, 102, 0]) rotate([0, 0, -45]) import_stl("y-idler-split2.stl");
translate([94, 104, 0]) rotate([0, 0, 45]) import_stl("y-idler-split1.stl");
