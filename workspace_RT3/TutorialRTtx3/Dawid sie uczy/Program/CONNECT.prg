1 C_Com(2) = "ETH:192.168.43.201, 10002"
2 *O1
3 Open "COM2:" As #1
4 If M_Open(1)<>1 Then *O1
5 Print #1, "HELLO"
6 Input #1, C1$
7 Print #1, C1$
8 Close #1
9 Hlt
10 End
