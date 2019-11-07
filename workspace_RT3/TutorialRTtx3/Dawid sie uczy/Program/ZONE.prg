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
12 Def Inte MovingAvailable
13 Def Inte Ypos, Zpos
14 Def Inte InZone
15 '
16 Def Pos P1, P2
17 Def Pos GoalPosition
18 Def Pos temp
19 '
20 Def Char WorkMode
21 Def Char ReceivedData
22 Def Char Command
23 ' ---------------------------------------------
24 '
25 '
26 '
27 ' ---------------------------------------------
28 ' MAIN
29     GoSub *StartConditions
30     GoSub *SetCommunication
31     GoSub *SetModeIDLE
32 ' Program Main Loop
33 While 1 = 1
34     'If (Ypos% >= -300) And (Ypos% <= 300) And (Zpos% >= 700) And (Zpos% <= 1300) Then GoalPosition = SetPos(820, Ypos%, Zpos%)
35     'If MovingAvailable% Then Mov GoalPosition
36     Dly 10
37     Dly 1E-006#
38 WEnd
39 GoSub *EndProgram
40 ' ---------------------------------------------
41 '
42 '
43 '
44 ' ---------------------------------------------
45 *StartConditions
46     ' Function that sets starting conditions such
47     ' as initializing variables.
48     P1 = Phome
49     P2 = Phome
50     P1 = SetPos(Phome.X - 20,  Phome.Y - 500, Phome.Z + 300)
51     P2 = SetPos(Phome.X + 20,  Phome.Y + 500, Phome.Z - 300)
52     IsConnected% = 0
53     MovingAvailable% = 1
54     WorkMode$ = "START"
55     ReceivedData$ = "NONE"
56     Command$ = "NONE"
57     GoalPosition = P_Curr
58     Ypos% = 0
59     Zpos% = 990
60     Servo On
61     Spd 100
62     Ovrd 10
63     Close
64     Return
65 ' ---------------------------------------------
66 '
67 '
68 '
69 ' ---------------------------------------------
70 *ReceiveInterrupt
71     ' Function that is called everytime that some
72     ' data comes in from the server as an
73     ' Interrupt.
74     Input #1, ReceivedData$
75     Command$ = Left$(ReceivedData$, 3)
76     Com Off
77     Select Command$
78         Case "IDL"
79             Print #1, "IDLE - Actual mode."
80             GoSub *SetModeIDLE
81             Break
82         Case "MOV"
83             Print #1, "MOVING - Actual mode."
84             GoSub *SetModeMOV
85             Break
86         Case "STP"
87             Print #1, "Turning Off and halting the robot."
88             GoSub *EndProgram
89             Break
90         Case "POS"
91             Print #1, "CURR:", P_Curr, P1, P2
92             Break
93         Case "HOM"
94             Print #1, "HOME:", Phome
95             Break
96         Case "SPD"
97             GoSub *ChangeSpeed
98             Break
99         Case "SET"
100             GoSub *SetGoalPos
101             Break
102         Case "CHK"
103             Break
104         Default
105             Print #1, "There's no such an Action."
106             Break
107     End Select
108     Com On
109     Return 1
110 ' ---------------------------------------------
111 '
112 '
113 '
114 ' ---------------------------------------------
115 *SetGoalPos
116     If WorkMode$ = "MOV" Then
117         Ypos% = Val(Mid$(ReceivedData$, 5, 5))
118         Zpos% = Val(Right$(ReceivedData$, 5))
119         temp = GoalPosition
120         GoalPosition = SetPos(Phome.X, Ypos%, Zpos%)
121         InZone% = Zone(GoalPosition, P1, P2)
122         If InZone% = 1 Then
123             Mov GoalPosition
124             Dly 1
125             Print #1, "Moving to the point in zone.", GoalPosition
126         Else
127             Print #1, "Position not in zone."
128             GoalPosition = temp
129         EndIf
130     Else
131         Print #1, "Moving not possible. Robot must be in MoV mode."
132     EndIf
133     Return
134 ' ---------------------------------------------
135 '
136 '
137 '
138 ' ---------------------------------------------
139 *SetModeIDLE
140     ' Function sets the idle mode on Robot. During
141     ' Idle mode the Movement Is not available, motors
142     ' are turned Off and before that robot reaches
143     ' the Home position.
144     If WorkMode$ <> "IDLE" Then
145         GoalPosition = Phome
146         Ovrd 10
147         Mov GoalPosition
148         Dly 3
149         MovingAvailable% = 0
150         Servo Off
151         WorkMode$ = "IDLE"
152         Dly 2
153     EndIf
154     Return
155 ' ---------------------------------------------
156 '
157 '
158 '
159 ' ---------------------------------------------
160 *SetModeMOV
161     ' MOV mode sets the robot to follow hand pos.
162     ' Servo motors turns On, and the speed is set
163     ' to 50.
164     If WorkMode$ <> "MOV" Then
165         WorkMode$ = "MOV"
166         Servo On
167         Dly 0.5
168         Ovrd 50
169         MovingAvailable% = 1
170     EndIf
171     Return
172 ' ---------------------------------------------
173 '
174 '
175 '
176 ' ---------------------------------------------
177 *SetCommunication
178     ' This function goal is to start communication
179     ' and define its parameters. #1 - File.No.
180     C_Com(2) = "ETH:192.168.0.221, 10001"
181     While IsConnected% = 0
182         Open "COM2:" As #1
183         If M_Open(1) = 1 Then
184             On Com(1) GoSub *ReceiveInterrupt
185             Com(1) On
186             IsConnected% = 1
187             Break
188         EndIf
189     WEnd
190     Return
191 ' ---------------------------------------------
192 '
193 '
194 '
195 ' ---------------------------------------------
196 *ChangeSpeed
197     ' Function that changes the speed in MOV mode.
198     If WorkMode$ = "MOV" Then
199         Spd Val(Right$(ReceivedData$, 3))
200         Print #1, "Actual Speed: ", M_Spd
201     Else
202         Print #1, "You must be in MOV mode to change speed."
203     EndIf
204     Return
205 ' ---------------------------------------------
206 '
207 '
208 '
209 ' ---------------------------------------------
210 *EndProgram
211     ' Ending procedure. Closes all connections
212     ' and turning motors Off. It also moves the
213     ' robot to home position.
214     If M_Svo(1) = 0 Then
215         Servo On
216         Dly 0.5
217         Ovrd 10
218         Mov Phome, -100
219         Dly 3
220         Servo Off
221     EndIf
222     Close #1
223     Hlt
224     End
225 ' ---------------------------------------------
P1=(+800.00,-500.00,+1290.00,+180.00,-0.17,+180.00)(7,0)
P2=(+840.00,+500.00,+690.00,+180.00,-0.17,+180.00)(7,0)
GoalPosition=(+820.00,+0.00,+1200.00,+180.00,-0.17,+180.00)(7,0)
temp=(+820.00,-100.00,+1000.00,+180.00,-0.17,+180.00)(7,0)
Phome=(+820.00,+0.00,+990.00,+180.00,-0.17,+180.00)(7,0)
