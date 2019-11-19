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
34     Dly 10
35     Dly 1E-006#
36 WEnd
37 GoSub *EndProgram
38 ' ---------------------------------------------
39 '
40 '
41 '
42 ' ---------------------------------------------
43 *StartConditions
44     ' Function that sets starting conditions such
45     ' as initializing variables.
46     P1 = Phome
47     P2 = Phome
48     P1 = SetPos(Phome.X - 20,  Phome.Y - 600, Phome.Z - 450)
49     P2 = SetPos(Phome.X + 20,  Phome.Y + 600, Phome.Z + 450)
50     IsConnected% = 0
51     MovingAvailable% = 1
52     WorkMode$ = "START"
53     ReceivedData$ = "NONE"
54     Command$ = "NONE"
55     GoalPosition = P_Curr
56     Ypos% = 0
57     Zpos% = 990
58     Servo On
59     Spd 10
60     Ovrd 10
61     Mov Phome
62     Close
63     Return
64 ' ---------------------------------------------
65 '
66 '
67 '
68 ' ---------------------------------------------
69 *ReceiveInterrupt
70     ' Function that is called everytime that some
71     ' data comes in from the server as an
72     ' Interrupt.
73     Input #1, ReceivedData$
74     Command$ = Left$(ReceivedData$, 3)
75     Com Stop
76     Select Command$
77         Case "IDL"
78             GoSub *SetModeIDLE
79             Print #1, "> IDL mode."
80             Break
81         Case "MOV"
82             GoSub *SetModeMOV
83             Print #1, "> MOV mode."
84             Break
85         Case "STP"
86             Print #1, "> OFF"
87             GoSub *EndProgram
88             Break
89         Case "POS"
90             Print #1, "> POS", P_Curr.X, P_Curr.Y, P_Curr.Z
91             Break
92         Case "HOM"
93             Print #1, "> HOM", Phome.X, Phome.Y, Phome.Z
94             Break
95         Case "SPD"
96             GoSub *ChangeSpeed
97             Break
98         Case "ZON"
99             Print #1, "> ZON", P1.X, P2.X, P1.Y, P2.Y, P1.Z, P2.Z
100             Break
101         Case "OVR"
102             Print #1, "> SPD", M_Spd
103             Break
104         Case "MOD"
105             Print #1, "> MOD", WorkMode$
106             Break
107         Case "SET"
108             GoSub *SetGoalPos
109             Break
110         Default
111             Print #1, "> There's no such an Action."
112             Break
113     End Select
114     Com On
115     Return 1
116 ' ---------------------------------------------
117 '
118 '
119 '
120 ' ---------------------------------------------
121 *SetGoalPos
122     If WorkMode$ = "MOV" Then
123         Ypos% = Val(Mid$(ReceivedData$, 5, 5))
124         Zpos% = Val(Right$(ReceivedData$, 5))
125         temp = GoalPosition
126         GoalPosition = SetPos(Phome.X, Ypos%, Zpos%)
127         InZone% = Zone(GoalPosition, P1, P2)
128         If Zone(GoalPosition, P1, P2) Then
129             Mov GoalPosition
130             Print #1, "> Moving to the point in zone."
131         Else
132             Print #1, "> Position not in zone."
133             GoalPosition = temp
134         EndIf
135     Else
136         Print #1, "> Moving not possible. Robot must be in MoV mode."
137     EndIf
138     Return
139 ' ---------------------------------------------
140 '
141 '
142 '
143 ' ---------------------------------------------
144 *SetModeIDLE
145     ' Function sets the idle mode on Robot. During
146     ' Idle mode the Movement Is not available, motors
147     ' are turned Off and before that robot reaches
148     ' the Home position.
149     If WorkMode$ <> "IDLE" Then
150         GoalPosition = Phome
151         Ovrd 10
152         Mov GoalPosition
153         MovingAvailable% = 0
154         Servo Off
155         WorkMode$ = "IDLE"
156         Dly 2
157     EndIf
158     Return
159 ' ---------------------------------------------
160 '
161 '
162 '
163 ' ---------------------------------------------
164 *SetModeMOV
165     ' MOV mode sets the robot to follow hand pos.
166     ' Servo motors turns On, and the speed is set
167     ' to 50.
168     If WorkMode$ <> "MOV" Then
169         WorkMode$ = "MOV"
170         Servo On
171         Dly 1
172         Ovrd 50
173         MovingAvailable% = 1
174     EndIf
175     Return
176 ' ---------------------------------------------
177 '
178 '
179 '
180 ' ---------------------------------------------
181 *SetCommunication
182     ' This function goal is to start communication
183     ' and define its parameters. #1 - File.No.
184     C_Com(2) = "ETH:192.168.0.59, 10001"
185     While IsConnected% = 0
186         Open "COM2:" As #1
187         If M_Open(1) = 1 Then
188             On Com(1) GoSub *ReceiveInterrupt
189             Com(1) On
190             IsConnected% = 1
191             Break
192         EndIf
193     WEnd
194     Return
195 ' ---------------------------------------------
196 '
197 '
198 '
199 ' ---------------------------------------------
200 *ChangeSpeed
201     ' Function that changes the speed in MOV mode.
202     If WorkMode$ = "MOV" Then
203         Ovrd Val(Right$(ReceivedData$, 3))
204         Print #1, "> SPD", M_Spd
205     Else
206         Print #1, "> You must be in MOV mode to change speed."
207     EndIf
208     Return
209 ' ---------------------------------------------
210 '
211 '
212 '
213 ' ---------------------------------------------
214 *EndProgram
215     ' Ending procedure. Closes all connections
216     ' and turning motors Off. It also moves the
217     ' robot to home position.
218     If M_Svo(1) = 0 Then
219         Servo On
220         Dly 0.5
221     Ovrd 10
222     Mov Phome, -100
223     Servo Off
224     EndIf
225     Close #1
226     Hlt
227     End
228 ' ---------------------------------------------
P1=(+580.00,-600.00,+200.00,-178.36,+2.72,+85.61)(7,0)
P2=(+620.00,+600.00,+1100.00,-178.36,+2.72,+85.61)(7,0)
GoalPosition=(+600.00,-152.00,+285.00,-178.36,+2.72,+85.61)(7,0)
temp=(+600.00,-115.00,+287.00,-178.36,+2.72,+85.61)(7,0)
Phome=(+600.00,+0.00,+650.00,-178.36,+2.72,+85.61)(7,0)
