Coherence;
Point(1) = {0, 0, 0, .0000000001};
Point(2) = {.00000001, 0, 0, .0000000001};
Point(3) = {.00000002, 0, 0, .0000000001};
Point(4) = {.00000003, 0, 0, .0000000001};

Line(5) = {1, 2};
Line(6) = {2, 3};
Line(7) = {3, 4};

Physical Point("Top") = {1};
Physical Point("Bottom") = {4};
Physical Point("ETL-EL") = {2};
Physical Point("EL-HTL") = {3};
Physical Line("ETL") = {1, 2};
Physical Line("EL") = {2, 3};
Physical Line("HTL") = {3, 4};
