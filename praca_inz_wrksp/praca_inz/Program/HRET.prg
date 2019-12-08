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
15 Def Inte Command
16 '
17 Def Pos P1, P2
18 Def Pos GoalPosition
19 '
20 Def Char WorkMode
21 Def Char ReceivedData
22 ' ---------------------------------------------
23 '
24 '
25 '
26 ' ---------------------------------------------
27 ' MAIN
28     GoSub *StartConditions
29     GoSub *SetCommunication
30     GoSub *SetModeIDLE
31 ' Program Main Loop
32 While 1 = 1
33     Dly 10
34     Dly 1E-006#
35 WEnd
36 GoSub *EndProgram
37 ' ---------------------------------------------
38 '
39 '
40 '
41 ' ---------------------------------------------
42 *StartConditions
43     ' Function that sets starting conditions such
44     ' as initializing variables.
45     P1 = Phome
46     P2 = Phome
47     P1 = SetPos(Phome.X - 20,  Phome.Y - 400, Phome.Z - 400)
48     P2 = SetPos(Phome.X + 20,  Phome.Y + 400, Phome.Z + 400)
49     IsConnected% = 0
50     MovingAvailable% = 1
51     WorkMode$ = "START"
52     ReceivedData$ = "NONE"
53     Command% = 0
54     GoalPosition = P_Curr
55     Ypos% = 0
56     Zpos% = 990
57     Servo On
58     Spd 10
59     Ovrd 10
60     Mov Phome
61     Close
62     Return
63 ' ---------------------------------------------
64 '
65 '
66 '
67 ' ---------------------------------------------
68 *ReceiveInterrupt
69     ' Function that is called everytime that some
70     ' data comes in from the server as an
71     ' Interrupt.
72     Input #1, ReceivedData$
73     Command% = Val(Left$(ReceivedData$, 1))
74     Com Stop
75     Select Command%
76         Case 1
77             GoSub *SetModeIDLE
78             Print #1, "> IDL mode."
79             Break
80         Case 2
81             GoSub *SetModeMOV
82             Print #1, "> MOV mode."
83             Break
84         Case 3
85             Print #1, "> OFF"
86             GoSub *EndProgram
87             Break
88         Case 4
89             Print #1, "> POS", P_Curr.X, P_Curr.Y, P_Curr.Z
90             Break
91         Case 5
92             Print #1, "> HOM", Phome.X, Phome.Y, Phome.Z
93             Break
94         Case 6
95             GoSub *ChangeSpeed
96             Break
97         Case 7
98             Print #1, "> ZON", P1.X, P2.X, P1.Y, P2.Y, P1.Z, P2.Z
99             Break
100         Case 8
101             Print #1, "> SPD", M_Ovrd
102             Break
103         Case 9
104             Print #1, "> MOD", WorkMode$
105             Break
106         Case 0
107             GoSub *SetGoalPos
108             Break
109         Default
110             Print #1, "> There's no such an Action."
111             Break
112     End Select
113     Com On
114     Return 1
115 ' ---------------------------------------------
116 '
117 '
118 '
119 ' ---------------------------------------------
120 *SetGoalPos
121     If WorkMode$ = "MOV" Then
122         Ypos% = Val(Mid$(ReceivedData$, 4, 5))
123         Zpos% = Val(Right$(ReceivedData$, 5))
124         GoalPosition = SetPos(Phome.X, Ypos%, Zpos%)
125         InZone% = Zone(GoalPosition, P1, P2)
126         If Zone(GoalPosition, P1, P2) Then
127             Mov GoalPosition
128             Print #1, "> Moving to the point in zone."
129         Else
130             Print #1, "> Position not in zone."
131         EndIf
132     Else
133         Print #1, "> Moving not possible. Robot must be in MoV mode."
134     EndIf
135     Return
136 ' ---------------------------------------------
137 '
138 '
139 '
140 ' ---------------------------------------------
141 *SetModeIDLE
142     ' Function sets the idle mode on Robot. During
143     ' Idle mode the Movement Is not available, motors
144     ' are turned Off and before that robot reaches
145     ' the Home position.
146     If WorkMode$ <> "IDLE" Then
147         GoalPosition = Phome
148         Ovrd 10
149         Mov GoalPosition
150         MovingAvailable% = 0
151         Servo Off
152         WorkMode$ = "IDLE"
153         Dly 2
154     EndIf
155     Return
156 ' ---------------------------------------------
157 '
158 '
159 '
160 ' ---------------------------------------------
161 *SetModeMOV
162     ' MOV mode sets the robot to follow hand pos.
163     ' Servo motors turns On, and the speed is set
164     ' to 50.
165     If WorkMode$ <> "MOV" Then
166         WorkMode$ = "MOV"
167         Servo On
168         Dly 1
169         Ovrd 50
170         MovingAvailable% = 1
171     EndIf
172     Return
173 ' ---------------------------------------------
174 '
175 '
176 '
177 ' ---------------------------------------------
178 *SetCommunication
179     ' This function goal is to start communication
180     ' and define its parameters. #1 - File.No.
181     C_Com(2) = "ETH:192.168.0.221, 10002"
182     While IsConnected% = 0
183         Open "COM2:" As #1
184         If M_Open(1) = 1 Then
185             On Com(1) GoSub *ReceiveInterrupt
186             Com(1) On
187             IsConnected% = 1
188             Break
189         EndIf
190     WEnd
191     Return
192 ' ---------------------------------------------
193 '
194 '
195 '
196 ' ---------------------------------------------
197 *ChangeSpeed
198     ' Function that changes the speed in MOV mode.
199     If WorkMode$ = "MOV" Then
200         Ovrd Val(Right$(ReceivedData$, 3))
201         Print #1, "> SPD", M_Ovrd
202     Else
203         Print #1, "> You must be in MOV mode to change speed."
204     EndIf
205     Return
206 ' ---------------------------------------------
207 '
208 '
209 '
210 ' ---------------------------------------------
211 *EndProgram
212     ' Ending procedure. Closes all connections
213     ' and turning motors Off. It also moves the
214     ' robot to home position.
215     If M_Svo(1) = 0 Then
216         Servo On
217         Dly 0.5
218     Ovrd 10
219     Mov Phome, -100
220     Servo Off
221     EndIf
222     Close #1
223     Hlt
224     End
225 ' ---------------------------------------------
P1=(+480.00,-400.00,+500.00,+179.93,+1.48,+86.03)(7,0)
P2=(+520.00,+400.00,+1300.00,+179.93,+1.48,+86.03)(7,0)
GoalPosition=(+500.00,+50.00,+790.00,+179.93,+1.48,+86.03)(7,0)
Phome=(+500.00,+0.00,+900.00,+179.93,+1.48,+86.03)(7,0)
