1 ' ---------------------------------------------
2 ' Title: "HAND-RETRACING"
3 ' Author: Dawid Sza³wiñski
4 ' Data: 26-10-2019
5 ' ---------------------------------------------
6 '
7 '
8 '
9 ' ---------------------------------------------
10 ' User Variables Definitions:
11 Def Inte IsConnected
12 Def Inte temp
13 Def Inte MovingAvailable
14 Def Inte Ypos, Zpos
15 Def Pos GoalPosition
16 Def Char WorkMode
17 Def Char ReceivedData
18 Def Char Command
19 ' ---------------------------------------------
20 '
21 '
22 '
23 ' ---------------------------------------------
24 ' MAIN
25     GoSub *StartConditions
26     GoSub *SetCommunication
27     GoSub *SetModeIDLE
28 ' Program Main Loop
29 While 1 = 1
30     If (Ypos% >= -300) And (Ypos% <= 300) And (Zpos% >= 700) And (Zpos% <= 1300) Then GoalPosition = SetPos(820, Ypos%, Zpos%)
31     If MovingAvailable% Then Mov GoalPosition
32     Dly 0.2
33 WEnd
34 GoSub *EndProgram
35 ' ---------------------------------------------
36 '
37 '
38 '
39 ' ---------------------------------------------
40 *StartConditions
41     ' Function that sets starting conditions such
42     ' as initializing variables.
43     temp% = 1
44     IsConnected% = 0
45     MovingAvailable% = 1
46     WorkMode$ = "START"
47     ReceivedData$ = "NONE"
48     Command$ = "NONE"
49     GoalPosition = P_Curr
50     Ypos% = 0
51     Zpos% = 990
52     Servo On
53     Spd 100
54     Ovrd 10
55     Close
56     Return
57 ' ---------------------------------------------
58 '
59 '
60 '
61 ' ---------------------------------------------
62 *ReceiveInterrupt
63     ' Function that is called everytime that some
64     ' data comes in from the server as an
65     ' Interrupt.
66     Input #1, ReceivedData$
67     Command$ = Left$(ReceivedData$, 3)
68     Com Off
69     Select Command$
70         Case "IDL"
71             Print #1, "The current mode is: IDLE."
72             GoSub *SetModeIDLE
73             Break
74         Case "STP"
75             Print #1, "Turning Off and halting the robot."
76             GoSub *EndProgram
77             Break
78         Case "MOV"
79             Print #1, "The current mode is: MOV."
80             GoSub *SetModeMOV
81             Break
82         Case "POS"
83             Print #1, P_Curr
84             Break
85         Case "SPD"
86             GoSub *ChangeSpeed
87             Break
88         Case "SET"
89             GoSub *SetGoalPos
90             Break
91         Case "CHK"
92             Break
93         Default
94             Print #1, "There's no such an Action."
95             Break
96     End Select
97     Com On
98     Return 1
99 ' ---------------------------------------------
100 '
101 '
102 '
103 ' ---------------------------------------------
104 *SetGoalPos
105     If WorkMode$ = "MOV" Then
106         Ypos% = Val(Mid$(ReceivedData$, 5, 5))
107         Zpos% = Val(Right$(ReceivedData$, 5))
108         Print #1, "Moving to the point."
109     Else
110         Print #1, "Moving not possible. Robot must be in MoV mode."
111     EndIf
112     Return
113 ' ---------------------------------------------
114 '
115 '
116 '
117 ' ---------------------------------------------
118 *SetModeIDLE
119     ' Function sets the idle mode on Robot. During
120     ' Idle mode the Movement Is not available, motors
121     ' are turned Off and before that robot reaches
122     ' the Home position.
123     If WorkMode$ <> "IDLE" Then
124         GoalPosition = Phome
125         Ovrd 10
126         Mov GoalPosition
127         Dly 3
128         MovingAvailable% = 0
129         Servo Off
130         WorkMode$ = "IDLE"
131         Dly 2
132     EndIf
133     Return
134 ' ---------------------------------------------
135 '
136 '
137 '
138 ' ---------------------------------------------
139 *SetModeMOV
140     ' MOV mode sets the robot to follow hand pos.
141     ' Servo motors turns On, and the speed is set
142     ' to 50.
143     If WorkMode$ <> "MOV" Then
144         WorkMode$ = "MOV"
145         Servo On
146         Dly 0.5
147         Ovrd 50
148         MovingAvailable% = 1
149     EndIf
150     Return
151 ' ---------------------------------------------
152 '
153 '
154 '
155 ' ---------------------------------------------
156 *SetCommunication
157     ' This function goal is to start communication
158     ' and define its parameters. #1 - File.No.
159     C_Com(2) = "ETH:192.168.0.221, 10002"
160     While IsConnected% = 0
161         Open "COM2:" As #1
162         If M_Open(1) = 1 Then
163             On Com(1) GoSub *ReceiveInterrupt
164             Com(1) On
165             IsConnected% = 1
166             Break
167         EndIf
168     WEnd
169     Return
170 ' ---------------------------------------------
171 '
172 '
173 '
174 ' ---------------------------------------------
175 *ChangeSpeed
176     ' Function that changes the speed in MOV mode.
177     If WorkMode$ = "MOV" Then
178         Spd Val(Right$(ReceivedData$, 3))
179         Print #1, "Actual Speed: ", M_Spd
180     Else
181         Print #1, "You must be in MOV mode to change speed."
182     EndIf
183     Return
184 ' ---------------------------------------------
185 '
186 '
187 '
188 ' ---------------------------------------------
189 *EndProgram
190     ' Ending procedure. Closes all connections
191     ' and turning motors Off. It also moves the
192     ' robot to home position.
193     If M_Svo(1) = 0 Then
194         Servo On
195         Dly 0.5
196         Ovrd 10
197         Mov Phome, -100
198         Dly 3
199         Servo Off
200     EndIf
201     Close #1
202     Hlt
203     End
204 ' ---------------------------------------------
GoalPosition=(+820.00,-176.00,+952.00,+180.00,-0.17,+180.00)(7,0)
Phome=(+820.00,+0.00,+990.00,+180.00,-0.17,+180.00)(7,0)
