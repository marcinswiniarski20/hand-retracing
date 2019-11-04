1 ' ---------------------------------------------
2 ' Title: HAND-RETRACING
3 ' author: Dawid Sza³wiñski
4 ' data: 15.10.2019
5 ' ---------------------------------------------
6 '
7 '
8 '
9 ' ---------------------------------------------
10 ' VAR DEFINITIONS:
11 Def Inte CONNECTED, Xcord, Ycord, Zcord
12 Def Pos GoalPosition
13 ' ---------------------------------------------
14 '
15 ' START
16 '
17 Mov PHome
18 CONNECTED% = 0
19 GoalPosition = P_Curr
20 GoSub *SetCommunication
21 While CONNECTED% And 1
22     Print #1, P_Curr
23     Input #1, GoalPosition
24     'Input #1, Ycord%
25     'Input #1, Zcord%
26     'GoalPosition = SetPos(Xcord%, Ycord%, Zcord%)
27     Mov GoalPosition
28     Dly 0.1
29     Print #1, "DONE"
30 WEnd
31 Close #1
32 Hlt
33 End
34 ' ---------------------------------------------
35 '
36 '
37 '
38 ' ---------------------------------------------
39 *SetCommunication
40 ' This function goal is to start communication
41 ' and define its parameters. #1 - File.No.
42 C_Com(2) = "ETH:192.168.0.221, 10002"
43 *CONNECT
44     Open "COM2:" As #1
45     If M_Open(1)<>1 Then *CONNECT
46 CONNECTED% = 1
47 Print #1, "SUCCESFULL CONNECTION"
48 Return
49 ' ---------------------------------------------
50 '
GoalPosition=(+729.25,+0.00,+993.39,+180.00,-0.17,+180.00)(7,0)
PHome=(+700.00,+0.00,+991.04,-180.00,-0.17,-180.00)(7,0)
