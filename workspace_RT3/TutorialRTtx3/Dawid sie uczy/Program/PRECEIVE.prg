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
71             Print #1, "IDLE - Actual mode."
72             GoSub *SetModeIDLE
73             Break
74         Case "MOV"
75             Print #1, "MOVING - Actual mode."
76             GoSub *SetModeMOV
77             Break
78         Case "STP"
79             Print #1, "Turning Off and halting the robot."
80             GoSub *EndProgram
81             Break
82         Case "POS"
83             Print #1, "CURR:", P_Curr
84             Break
85         Case "HOM"
86             Print #1, "HOME:", Phome
87             Break
88         Case "SPD"
89             GoSub *ChangeSpeed
90             Break
91         Case "SET"
92             GoSub *SetGoalPos
93             Break
94         Case "CHK"
95             Break
96         Default
97             Print #1, "There's no such an Action."
98             Break
99     End Select
100     Com On
101     Return 1
102 ' ---------------------------------------------
103 '
104 '
105 '
106 ' ---------------------------------------------
107 *SetGoalPos
108     If WorkMode$ = "MOV" Then
109         Ypos% = Val(Mid$(ReceivedData$, 5, 5))
110         Zpos% = Val(Right$(ReceivedData$, 5))
111         Print #1, "Moving to the point."
112     Else
113         Print #1, "Moving not possible. Robot must be in MoV mode."
114     EndIf
115     Return
116 ' ---------------------------------------------
117 '
118 '
119 '
120 ' ---------------------------------------------
121 *SetModeIDLE
122     ' Function sets the idle mode on Robot. During
123     ' Idle mode the Movement Is not available, motors
124     ' are turned Off and before that robot reaches
125     ' the Home position.
126     If WorkMode$ <> "IDLE" Then
127         GoalPosition = Phome
128         Ovrd 10
129         Mov GoalPosition
130         Dly 3
131         MovingAvailable% = 0
132         Servo Off
133         WorkMode$ = "IDLE"
134         Dly 2
135     EndIf
136     Return
137 ' ---------------------------------------------
138 '
139 '
140 '
141 ' ---------------------------------------------
142 *SetModeMOV
143     ' MOV mode sets the robot to follow hand pos.
144     ' Servo motors turns On, and the speed is set
145     ' to 50.
146     If WorkMode$ <> "MOV" Then
147         WorkMode$ = "MOV"
148         Servo On
149         Dly 0.5
150         Ovrd 50
151         MovingAvailable% = 1
152     EndIf
153     Return
154 ' ---------------------------------------------
155 '
156 '
157 '
158 ' ---------------------------------------------
159 *SetCommunication
160     ' This function goal is to start communication
161     ' and define its parameters. #1 - File.No.
162     C_Com(2) = "ETH:192.168.0.221, 10001"
163     While IsConnected% = 0
164         Open "COM2:" As #1
165         If M_Open(1) = 1 Then
166             On Com(1) GoSub *ReceiveInterrupt
167             Com(1) On
168             IsConnected% = 1
169             Break
170         EndIf
171     WEnd
172     Return
173 ' ---------------------------------------------
174 '
175 '
176 '
177 ' ---------------------------------------------
178 *ChangeSpeed
179     ' Function that changes the speed in MOV mode.
180     If WorkMode$ = "MOV" Then
181         Spd Val(Right$(ReceivedData$, 3))
182         Print #1, "Actual Speed: ", M_Spd
183     Else
184         Print #1, "You must be in MOV mode to change speed."
185     EndIf
186     Return
187 ' ---------------------------------------------
188 '
189 '
190 '
191 ' ---------------------------------------------
192 *EndProgram
193     ' Ending procedure. Closes all connections
194     ' and turning motors Off. It also moves the
195     ' robot to home position.
196     If M_Svo(1) = 0 Then
197         Servo On
198         Dly 0.5
199         Ovrd 10
200         Mov Phome, -100
201         Dly 3
202         Servo Off
203     EndIf
204     Close #1
205     Hlt
206     End
207 ' ---------------------------------------------
GoalPosition=(+820.00,-100.00,+1000.00,+180.00,-0.17,+180.00)(7,0)
Phome=(+820.00,+0.00,+990.00,+180.00,-0.17,+180.00)(7,0)
