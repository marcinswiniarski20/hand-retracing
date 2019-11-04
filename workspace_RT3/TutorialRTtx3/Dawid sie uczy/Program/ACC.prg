1 Accel 50,100                            ' Heavy load designation (when acceleration/deceleration is 0.2 seconds, the acceleration will be 0.4, and the deceleration will be 0.2 seconds).
2 Mov P1
3 Accel 100,100                          ' Standard load designation.
4 Mov P2
5 Def Arch 1,10,10,25,25,1,0,0
6 Accel 100,100,20,20,20,20        ' Specify the override value to 20 when moving upward or downward due to the MvaMva instruction.
7 Mva P3,1
P1=(+931.09,-104.46,+780.27,+179.41,+5.27,+167.17)(7,0)
P2=(+931.09,-564.82,+780.27,+179.41,+5.27,+167.17)(7,0)
P3=(+273.30,-564.82,+780.27,+179.41,+5.27,+167.17)(7,0)
