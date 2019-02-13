Coherence;
Point(1) = {-0.2, 0, 0, 1.0};
Point(2) = {, 0, 0, 1.0};
Point(2) = {0, 0, 0, 1.0};
Delete {
  Point{1};
}
Point(3) = {1, 0, 0, 1.0};
Line(1) = {2, 3};
Delete {
  Point{2, 3};
}
Delete {
  Line{1};
}
Delete {
  Point{2, 3};
}
Point(3) = {-0.5, -0.1, 0, 1.0};
Delete {
  Point{3};
}
Point(3) = {0, 0, 0, 1.0};
Point(4) = {1e-7, 0, 0, 1.0};
Point(5) = {.0000001, 0, 0, 1.0};
Point(6) = {0.01, 0, 0, 1.0};
Point(7) = {0.001, 0, 0, 1.0};
Point(8) = {0.001, 0, 0, 1.0};
Point(9) = {0.0001, 0, 0, 1.0};
Point(10) = {0.00001, 0, 0, 1.0};
Delete {
  Point{3, 4, 10, 9, 7, 6};
}
Delete {
  Point{5};
}
Delete {
  Point{8};
}
Point(8) = {0, 0, 0, 1.0};
Point(9) = {.0000007, 0, 0, 1.0};
Point(10) = {.0000007, 0, 0, 1.0};
Delete {
  Point{9};
}
Delete {
  Point{10};
}
Point(10) = {.0000001, 0, 0, 1.0};
Line(1) = {8, 10};
Physical Line(2) = {1};
Delete {
  Line{1};
}
Coherence;
Point(9) = {.0000001, 0, -0, 1.0};
Delete {
  Point{9};
}
Point(9) = {.0000001, 0, 0, 1.0};
Line(3) = {8, 9};
Delete {
  Line{3};
}
Line(3) = {8, 9};
Physical Line(4) = {3};
Delete {
  Line{3};
}
Delete {
  Point{8, 9};
}
Point(9) = {.0000001, 0, 0, .000000001};
Point(10) = {0, 0, 0, .000000001};
Line(5) = {10, 9};
Physical Line(6) = {5};
