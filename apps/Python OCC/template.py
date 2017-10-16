# Local variables:
# app - application instance
# app_input - input data
# app_output - if set will be sent as output data
# do not forget to press "Save" button after edit!

from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
my_box = BRepPrimAPI_MakeBox(10., 20., 30.).Shape()
display.DisplayShape(my_box)

from OCC.BRepPrimAPI import BRepPrimAPI_MakeTorus
my_torus = BRepPrimAPI_MakeTorus(20., 10.).Shape()
display.DisplayShape(my_torus)