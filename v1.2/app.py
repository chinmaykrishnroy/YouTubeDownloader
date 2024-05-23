# YouTube Audio Downloader (also downloads video)
# Downloads YouTube Audio @128kBps and Video @480p
# Created by Chinmay Krishn Roy
# https://github.com/chinmaykrishnroy
# https://www.linkedin.com/in/chinmaykrishnroy/

dta = " CjwhRE9DVFlQRSBodG1sPgo8aHRtbCBsYW5nPSJlbiI+Cgo8aGVhZD4KICAgIDxtZXRhIGNoYXJzZXQ9IlVURi04IiAvPgogICAgPG1ldGEgaHR0cC1lcXVpdj0iWC1VQS1Db21wYXRpYmxlIiBjb250ZW50PSJJRT1lZGdlIiAvPgogICAgPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiIC8+CiAgICA8dGl0bGU+WW91VHViZSBEb3dubG9hZGVyPC90aXRsZT4KICAgIDxzdHlsZT4KICAgICAgICAvKiBHRU5FUkFMICovCiAgICAgICAgQGltcG9ydCB1cmwoImh0dHBzOi8vZm9udHMuZ29vZ2xlYXBpcy5jb20vY3NzP2ZhbWlseT1SdWJpayIpOwoKICAgICAgICAuY3JlZGl0IHsKICAgICAgICAgICAgcG9zaXRpb246IGZpeGVkOwogICAgICAgICAgICByaWdodDogMnJlbTsKICAgICAgICAgICAgYm90dG9tOiAycmVtOwogICAgICAgICAgICBjb2xvcjogd2hpdGU7CiAgICAgICAgfQoKICAgICAgICAuY3JlZGl0IGEgewogICAgICAgICAgICBjb2xvcjogaW5oZXJpdDsKICAgICAgICB9CgogICAgICAgIGJvZHkgewogICAgICAgICAgICBtYXJnaW46IDA7CiAgICAgICAgICAgIHBhZGRpbmc6IDA7CiAgICAgICAgICAgIGZvbnQtZmFtaWx5OiAiUnViaWsiLCAtYXBwbGUtc3lzdGVtLCBCbGlua01hY1N5c3RlbUZvbnQsICJTZWdvZSBVSSIsCiAgICAgICAgICAgICAgICAiUm9ib3RvIiwgIk94eWdlbiIsICJVYnVudHUiLCAiQ2FudGFyZWxsIiwgIkZpcmEgU2FucyIsICJEcm9pZCBTYW5zIiwKICAgICAgICAgICAgICAgICJIZWx2ZXRpY2EgTmV1ZSIsIHNhbnMtc2VyaWY7CiAgICAgICAgfQoKICAgICAgICAuYm9keSB7CiAgICAgICAgICAgIHBvc2l0aW9uOiByZWxhdGl2ZTsKICAgICAgICAgICAgd2lkdGg6IDEwMHZ3OwogICAgICAgICAgICBoZWlnaHQ6IDEwMHZoOwogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjZmZmOwogICAgICAgICAgICBvdmVyZmxvdzogaGlkZGVuOwogICAgICAgICAgICBkaXNwbGF5OiBmbGV4OwogICAgICAgICAgICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAgdHJhbnNpdGlvbjogYmFja2dyb3VuZC1jb2xvciAwLjFzOwogICAgICAgIH0KCiAgICAgICAgLyogTWFpbiBDaXJjbGUgKi8KICAgICAgICAubWFpbi1jaXJjbGUgewogICAgICAgICAgICB3aWR0aDogNDByZW07CiAgICAgICAgICAgIGhlaWdodDogNDByZW07CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEwMCU7CiAgICAgICAgICAgIGJhY2tncm91bmQ6IGxpbmVhci1ncmFkaWVudCg0MGRlZywgI2ZmMDA4MCwgI2ZmOGMwMCA3MCUpOwogICAgICAgICAgICBwb3NpdGlvbjogYWJzb2x1dGU7CiAgICAgICAgICAgIHotaW5kZXg6IDE7CiAgICAgICAgICAgIGxlZnQ6IDUwJTsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGUoLTUwJSwgLTcwJSk7CiAgICAgICAgfQoKICAgICAgICAvKiBQaG9uZSAqLwogICAgICAgIC5waG9uZSB7CiAgICAgICAgICAgIHBvc2l0aW9uOiByZWxhdGl2ZTsKICAgICAgICAgICAgei1pbmRleDogMjsKICAgICAgICAgICAgd2lkdGg6IDIxcmVtOwogICAgICAgICAgICBoZWlnaHQ6IDQ1cmVtOwogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiBpbmhlcml0OwogICAgICAgICAgICBib3gtc2hhZG93OiAwIDRweCAzNXB4IHJnYmEoMCwgMCwgMCwgMC4xKTsKICAgICAgICAgICAgYm9yZGVyLXJhZGl1czogNDBweDsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjsKICAgICAgICB9CgogICAgICAgIC5zd2lwZSB7CiAgICAgICAgICAgIHdpZHRoOiA0MCU7CiAgICAgICAgICAgIGhlaWdodDogMC4yNXJlbTsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogYmxhY2s7CiAgICAgICAgICAgIG9wYWNpdHk6IDAuMTU7CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEwcHg7CiAgICAgICAgICAgIG1hcmdpbjogMC41cmVtIGF1dG87CiAgICAgICAgfQoKICAgICAgICAvKiBUb3AgKi8KICAgICAgICAubWVudSB7CiAgICAgICAgICAgIC8qICAgYmFja2dyb3VuZC1jb2xvcjogYmx1ZTsgKi8KICAgICAgICAgICAgZm9udC1zaXplOiA4MCU7CiAgICAgICAgICAgIG9wYWNpdHk6IDAuNDsKICAgICAgICAgICAgcGFkZGluZzogMC44cmVtIDEuOHJlbTsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAganVzdGlmeS1jb250ZW50OiBzcGFjZS1iZXR3ZWVuOwogICAgICAgICAgICBhbGlnbi1pdGVtczogY2VudGVyOwogICAgICAgIH0KCiAgICAgICAgLmljb25zIHsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAgbWFyZ2luLXRvcDogMC41cmVtOwogICAgICAgIH0KCiAgICAgICAgLmJhdHRlcnkgewogICAgICAgICAgICB3aWR0aDogMC44NXJlbTsKICAgICAgICAgICAgaGVpZ2h0OiAwLjQ1cmVtOwogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiBibGFjazsKICAgICAgICB9CgogICAgICAgIC5uZXR3b3JrIHsKICAgICAgICAgICAgd2lkdGg6IDA7CiAgICAgICAgICAgIGhlaWdodDogMDsKICAgICAgICAgICAgYm9yZGVyLXN0eWxlOiBzb2xpZDsKICAgICAgICAgICAgYm9yZGVyLXdpZHRoOiAwIDYuOHB4IDcuMnB4IDYuOHB4OwogICAgICAgICAgICBib3JkZXItY29sb3I6IHRyYW5zcGFyZW50IHRyYW5zcGFyZW50IGJsYWNrIHRyYW5zcGFyZW50OwogICAgICAgICAgICB0cmFuc2Zvcm06IHJvdGF0ZSgxMzVkZWcpOwogICAgICAgICAgICBtYXJnaW46IDAuMTJyZW0gMC41cmVtOwogICAgICAgIH0KCiAgICAgICAgLyogTWlkZGxlICovCiAgICAgICAgLmNvbnRlbnQgewogICAgICAgICAgICBkaXNwbGF5OiBmbGV4OwogICAgICAgICAgICBmbGV4LWRpcmVjdGlvbjogY29sdW1uOwogICAgICAgICAgICBtYXJnaW46IGF1dG87CiAgICAgICAgICAgIHRleHQtYWxpZ246IGNlbnRlcjsKICAgICAgICAgICAgd2lkdGg6IDcwJTsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVZKDUlKTsKICAgICAgICB9CgogICAgICAgIC5jaXJjbGUgewogICAgICAgICAgICBwb3NpdGlvbjogcmVsYXRpdmU7CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEwMCU7CiAgICAgICAgICAgIHdpZHRoOiA4cmVtOwogICAgICAgICAgICBoZWlnaHQ6IDhyZW07CiAgICAgICAgICAgIGJhY2tncm91bmQ6IGxpbmVhci1ncmFkaWVudCg0MGRlZywgI2ZmMDA4MCwgI2ZmOGMwMCA3MCUpOwogICAgICAgICAgICBtYXJnaW46IGF1dG87CiAgICAgICAgfQoKICAgICAgICAuY3Jlc2NlbnQgewogICAgICAgICAgICBwb3NpdGlvbjogYWJzb2x1dGU7CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEwMCU7CiAgICAgICAgICAgIHJpZ2h0OiAwOwogICAgICAgICAgICB3aWR0aDogNnJlbTsKICAgICAgICAgICAgaGVpZ2h0OiA2cmVtOwogICAgICAgICAgICBiYWNrZ3JvdW5kOiB3aGl0ZTsKICAgICAgICAgICAgdHJhbnNmb3JtOiBzY2FsZSgwKTsKICAgICAgICAgICAgdHJhbnNmb3JtLW9yaWdpbjogdG9wIHJpZ2h0OwogICAgICAgICAgICB0cmFuc2l0aW9uOiB0cmFuc2Zvcm0gMC42cyBjdWJpYy1iZXppZXIoMC42NDUsIDAuMDQ1LCAwLjM1NSwgMSk7CiAgICAgICAgfQoKICAgICAgICBwIHsKICAgICAgICAgICAgZm9udC1zaXplOiA5MCU7CiAgICAgICAgfQoKICAgICAgICBpbnB1dCB7CiAgICAgICAgICAgIGZvbnQtZmFtaWx5OiAiUnViaWsiLCAtYXBwbGUtc3lzdGVtLCBCbGlua01hY1N5c3RlbUZvbnQsICJTZWdvZSBVSSIsCiAgICAgICAgICAgICAgICAiUm9ib3RvIiwgIk94eWdlbiIsICJVYnVudHUiLCAiQ2FudGFyZWxsIiwgIkZpcmEgU2FucyIsICJEcm9pZCBTYW5zIiwKICAgICAgICAgICAgICAgICJIZWx2ZXRpY2EgTmV1ZSIsIHNhbnMtc2VyaWY7CiAgICAgICAgICAgIG1hcmdpbi10b3A6IDFlbTsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogI2YzZjNmMzsKICAgICAgICAgICAgYm9yZGVyOiAwcHggc29saWQgI2UwZTBlMDsKICAgICAgICAgICAgYm9yZGVyLWNvbG9yOiB0cmFuc3BhcmVudCB0cmFuc3BhcmVudCBibGFjayB0cmFuc3BhcmVudDsKICAgICAgICAgICAgYm9yZGVyLXJhZGl1czogNTBweDsKICAgICAgICAgICAgcGFkZGluZzogMTBweDsKICAgICAgICAgICAgZm9udC1zaXplOiAxNHB4OwogICAgICAgICAgICB3aWR0aDogMjIwcHg7CiAgICAgICAgICAgIGhlaWdodDogMjBweDsKICAgICAgICAgICAgdGV4dC1hbGlnbjogbGVmdDsKICAgICAgICAgICAgYWxpZ24tc2VsZjogY2VudGVyOwogICAgICAgICAgICBhbGlnbi1jb250ZW50OiBjZW50ZXI7CiAgICAgICAgICAgIGNvbG9yOiAjMzYzNjM2OwogICAgICAgIH0KCiAgICAgICAgaW5wdXQ6OnBsYWNlaG9sZGVyIHsKICAgICAgICAgICAgY29sb3I6ICM5OTk5OTk7CiAgICAgICAgICAgIGZvbnQtc2l6ZTogODsKICAgICAgICB9CgogICAgICAgIGlucHV0OmZvY3VzIHsKICAgICAgICAgICAgb3V0bGluZTogMXB4IHNvbGlkICM0Y2FmNTA7CiAgICAgICAgfQoKICAgICAgICAuaGVhZGluZyB7CiAgICAgICAgICAgIGZvbnQtc2l6ZTogMTQwJTsKICAgICAgICAgICAgZm9udC13ZWlnaHQ6IGJvbGRlcjsKICAgICAgICAgICAgbWFyZ2luOiAzcmVtIDAgMC4ycmVtIDA7CiAgICAgICAgfQoKICAgICAgICBsYWJlbCwKICAgICAgICAudG9nZ2xlIHsKICAgICAgICAgICAgaGVpZ2h0OiAyLjhyZW07CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEwMHB4OwogICAgICAgIH0KCiAgICAgICAgbGFiZWwgewogICAgICAgICAgICB3aWR0aDogMTAwJTsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogcmdiYSgwLCAwLCAwLCAwLjEpOwogICAgICAgICAgICBib3JkZXItcmFkaXVzOiAxMDBweDsKICAgICAgICAgICAgcG9zaXRpb246IHJlbGF0aXZlOwogICAgICAgICAgICBtYXJnaW46IDEuOHJlbSAwIDRyZW0gMDsKICAgICAgICAgICAgY3Vyc29yOiBwb2ludGVyOwogICAgICAgIH0KCiAgICAgICAgLmZpbmFsIHsKICAgICAgICAgICAgZm9udC1mYW1pbHk6ICJSdWJpayIsIC1hcHBsZS1zeXN0ZW0sIEJsaW5rTWFjU3lzdGVtRm9udCwgIlNlZ29lIFVJIiwKICAgICAgICAgICAgICAgICJSb2JvdG8iLCAiT3h5Z2VuIiwgIlVidW50dSIsICJDYW50YXJlbGwiLCAiRmlyYSBTYW5zIiwgIkRyb2lkIFNhbnMiLAogICAgICAgICAgICAgICAgIkhlbHZldGljYSBOZXVlIiwgc2Fucy1zZXJpZjsKICAgICAgICAgICAgcGFkZGluZzogMTBweDsKICAgICAgICAgICAgbWFyZ2luOiAwIGF1dG87CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICNmZjhjMDA7CiAgICAgICAgICAgIGNvbG9yOiB3aGl0ZTsKICAgICAgICAgICAgYm9yZGVyOiBub25lOwogICAgICAgICAgICBkaXNwbGF5OiBpbmxpbmUtYmxvY2s7CiAgICAgICAgICAgIGp1c3RpZnktY29udGVudDogY2VudGVyOwogICAgICAgICAgICB0ZXh0LWFsaWduOiBjZW50ZXI7CiAgICAgICAgICAgIGZvbnQtc2l6ZTogMTY7CiAgICAgICAgICAgIHRyYW5zaXRpb246IDAuMTVzOwogICAgICAgICAgICBtYXJnaW46IDJweCBhdXRvOwogICAgICAgICAgICBib3JkZXItcmFkaXVzOiA1MHB4OwogICAgICAgICAgICBib3JkZXI6IDFweCBzb2xpZCAjZTBlMGUwOwogICAgICAgICAgICBjdXJzb3I6IHBvaW50ZXI7CiAgICAgICAgICAgIGp1c3RpZnktY29udGVudDogc3BhY2UtYmV0d2VlbjsKICAgICAgICB9CgogICAgICAgIC5maW5hbDpob3ZlciB7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICNmZjAwODA7CiAgICAgICAgfQoKICAgICAgICAudG9nZ2xlIHsKICAgICAgICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICAgICAgICB3aWR0aDogNTAlOwogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjZmZmOwogICAgICAgICAgICBib3gtc2hhZG93OiAwIDJweCAxNXB4IHJnYmEoMCwgMCwgMCwgMC4xNSk7CiAgICAgICAgICAgIHRyYW5zaXRpb246IHRyYW5zZm9ybSAwLjNzIGN1YmljLWJlemllcigwLjI1LCAwLjQ2LCAwLjQ1LCAwLjk0KTsKICAgICAgICB9CgogICAgICAgIC5uYW1lcyB7CiAgICAgICAgICAgIGZvbnQtc2l6ZTogOTAlOwogICAgICAgICAgICBmb250LXdlaWdodDogYm9sZGVyOwogICAgICAgICAgICB3aWR0aDogNjUlOwogICAgICAgICAgICBtYXJnaW4tbGVmdDogMTcuNSU7CiAgICAgICAgICAgIG1hcmdpbi10b3A6IDAuNSU7CiAgICAgICAgICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAganVzdGlmeS1jb250ZW50OiBzcGFjZS1iZXR3ZWVuOwogICAgICAgICAgICB1c2VyLXNlbGVjdDogbm9uZTsKICAgICAgICB9CgogICAgICAgIC5kYXJrIHsKICAgICAgICAgICAgb3BhY2l0eTogMC41OwogICAgICAgIH0KCiAgICAgICAgLm1hcmsgewogICAgICAgICAgICBib3JkZXItcmFkaXVzOiAxMDBweDsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogYmxhY2s7CiAgICAgICAgfQoKICAgICAgICAubWFyayB7CiAgICAgICAgICAgIHdpZHRoOiA3JTsKICAgICAgICAgICAgbWFyZ2luOiBhdXRvOwogICAgICAgICAgICBwb3NpdGlvbjogcmVsYXRpdmU7CiAgICAgICAgICAgIGhlaWdodDogMC4yNXJlbTsKICAgICAgICB9CgogICAgICAgIC5tYXJrOjpiZWZvcmUgewogICAgICAgICAgICBjb250ZW50OiAiIjsKICAgICAgICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICAgICAgICB3aWR0aDogMC4yNXJlbTsKICAgICAgICAgICAgaGVpZ2h0OiAxMDAlOwogICAgICAgICAgICBsZWZ0OiAtNzAlOwogICAgICAgICAgICBvcGFjaXR5OiAwLjE1OwogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiBpbmhlcml0OwogICAgICAgIH0KCiAgICAgICAgLm1hcms6OmFmdGVyIHsKICAgICAgICAgICAgY29udGVudDogIiI7CiAgICAgICAgICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTsKICAgICAgICAgICAgd2lkdGg6IDAuMjVyZW07CiAgICAgICAgICAgIGhlaWdodDogMTAwJTsKICAgICAgICAgICAgcmlnaHQ6IC03MCU7CiAgICAgICAgICAgIG9wYWNpdHk6IDAuMTU7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6IGluaGVyaXQ7CiAgICAgICAgfQoKICAgICAgICAvKiBCb3R0b20gKi8KICAgICAgICAuc2tpcCB7CiAgICAgICAgICAgIHBhZGRpbmc6IDEuNXJlbSAxLjhyZW07CiAgICAgICAgICAgIGRpc3BsYXk6IGZsZXg7CiAgICAgICAgICAgIGp1c3RpZnktY29udGVudDogc3BhY2UtYmV0d2VlbjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICB9CgogICAgICAgIC5za2lwIHAgewogICAgICAgICAgICBvcGFjaXR5OiAwLjU1OwogICAgICAgICAgICBmb250LXNpemU6IDkwJTsKICAgICAgICAgICAgY3Vyc29yOiBwb2ludGVyOwogICAgICAgICAgICB0cmFuc2l0aW9uOiBhbGwgMnMgZWFzZTsKICAgICAgICB9CgogICAgICAgIC5za2lwIHA6aG92ZXIgewogICAgICAgICAgICB0ZXh0LWRlY29yYXRpb246IHVuZGVybGluZTsKICAgICAgICB9CgogICAgICAgIC5mYWIgewogICAgICAgICAgICBib3gtc2hhZG93OiAwIDJweCAxMHB4IHJnYmEoMCwgMCwgMCwgMC4yKTsKICAgICAgICAgICAgYm9yZGVyLXJhZGl1czogMTAwJTsKICAgICAgICAgICAgd2lkdGg6IDNyZW07CiAgICAgICAgICAgIGhlaWdodDogM3JlbTsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAganVzdGlmeS1jb250ZW50OiBjZW50ZXI7CiAgICAgICAgICAgIGFsaWduLWl0ZW1zOiBjZW50ZXI7CiAgICAgICAgICAgIHBvc2l0aW9uOiByZWxhdGl2ZTsKICAgICAgICAgICAgY3Vyc29yOiBwb2ludGVyOwogICAgICAgICAgICB0cmFuc2l0aW9uOiB0cmFuc2Zvcm0gMC41cyBjdWJpYy1iZXppZXIoMC4xOSwgMSwgMC4yMiwgMSk7CiAgICAgICAgfQoKICAgICAgICAuZmFiOmhvdmVyIHsKICAgICAgICAgICAgdHJhbnNmb3JtOiBzY2FsZSgxLjIpOwogICAgICAgIH0KCiAgICAgICAgLmFycm93IHsKICAgICAgICAgICAgd2lkdGg6IDQwJTsKICAgICAgICAgICAgaGVpZ2h0OiAwLjFyZW07CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6IGJsYWNrOwogICAgICAgIH0KCiAgICAgICAgLmFycm93OjpiZWZvcmUgewogICAgICAgICAgICBjb250ZW50OiAiIjsKICAgICAgICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICAgICAgICBoZWlnaHQ6IDAuMXJlbTsKICAgICAgICAgICAgd2lkdGg6IDIwJTsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogaW5oZXJpdDsKICAgICAgICAgICAgdHJhbnNmb3JtOiByb3RhdGUoNDVkZWcpOwogICAgICAgICAgICByaWdodDogMjYlOwogICAgICAgICAgICB0b3A6IDQyJTsKICAgICAgICB9CgogICAgICAgIC5hcnJvdzo6YWZ0ZXIgewogICAgICAgICAgICBjb250ZW50OiAiIjsKICAgICAgICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICAgICAgICBoZWlnaHQ6IDAuMXJlbTsKICAgICAgICAgICAgd2lkdGg6IDIwJTsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogaW5oZXJpdDsKICAgICAgICAgICAgdHJhbnNmb3JtOiByb3RhdGUoLTQ1ZGVnKTsKICAgICAgICAgICAgcmlnaHQ6IDI2JTsKICAgICAgICAgICAgYm90dG9tOiA0MiU7CiAgICAgICAgfQoKICAgICAgICAuc3dpdGNoIHsKICAgICAgICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICAgICAgICBkaXNwbGF5OiBmbGV4OwogICAgICAgICAgICBtYXJnaW4tdG9wOiA0cHg7CiAgICAgICAgICAgIG1hcmdpbi1sZWZ0OiA0MHB4OwogICAgICAgICAgICB3aWR0aDogMzBweDsKICAgICAgICAgICAgaGVpZ2h0OiAzMHB4OwogICAgICAgICAgICBib3JkZXI6IDJweCBzb2xpZCAjZGNkY2RjOwogICAgICAgICAgICBiYWNrZ3JvdW5kOiAjZjBmMGYwOwogICAgICAgICAgICAvKiBib3gtc2hhZG93OiAycHggMnB4IDdweCAjYmViZWJlLCAtMnB4IC0ycHggN3B4ICNmZmZmZmY7ICovCiAgICAgICAgICAgIG92ZXJmbG93OiBoaWRkZW47CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDYwcHg7CiAgICAgICAgfQoKICAgICAgICAuc3dpdGNoIGlucHV0IHsKICAgICAgICAgICAgb3BhY2l0eTogMDsKICAgICAgICAgICAgd2lkdGg6IDA7CiAgICAgICAgICAgIGhlaWdodDogMDsKICAgICAgICB9CgogICAgICAgIC5zbGlkZXIgewogICAgICAgICAgICBwb3NpdGlvbjogYWJzb2x1dGU7CiAgICAgICAgICAgIGN1cnNvcjogcG9pbnRlcjsKICAgICAgICAgICAgdG9wOiAwOwogICAgICAgICAgICBsZWZ0OiAwOwogICAgICAgICAgICByaWdodDogMDsKICAgICAgICAgICAgYm90dG9tOiAwOwogICAgICAgICAgICAtd2Via2l0LXRyYW5zaXRpb246IDAuMTI1czsKICAgICAgICAgICAgdHJhbnNpdGlvbjogMC4xMjVzOwogICAgICAgIH0KCiAgICAgICAgaW5wdXQ6Y2hlY2tlZCsuc2xpZGVyOmJlZm9yZSB7CiAgICAgICAgICAgIGJhY2tncm91bmQ6IHdoaXRlOwogICAgICAgICAgICBib3gtc2hhZG93OiBub25lOwogICAgICAgIH0KCiAgICAgICAgaW5wdXQ6Zm9jdXMrLnNsaWRlciB7CiAgICAgICAgICAgIGJveC1zaGFkb3c6IDAgMCAxcHggIzIxOTZmMzsKICAgICAgICB9CgogICAgICAgIC5zbGlkZXIgewogICAgICAgICAgICBjb2xvcjogIzgxODE4MTsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAganVzdGlmeS1jb250ZW50OiBjZW50ZXI7CiAgICAgICAgICAgIGZvbnQtc2l6ZTogOHB4OwogICAgICAgICAgICBmb250LWZhbWlseTogc2Fucy1zZXJpZjsKICAgICAgICB9CgogICAgICAgIC5zbGlkZXItLTAgewogICAgICAgICAgICBjb2xvcjogd2hpdGU7CiAgICAgICAgICAgIGZvbnQtd2VpZ2h0OiA2MDA7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICM2OTY5Y2U7CiAgICAgICAgfQoKICAgICAgICAuc2xpZGVyLS0xIGRpdiB7CiAgICAgICAgICAgIHRyYW5zaXRpb246IDAuMTI1czsKICAgICAgICB9CgogICAgICAgIC5zbGlkZXItLTEgZGl2IHsKICAgICAgICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICAgICAgICB3aWR0aDogMTAwJTsKICAgICAgICAgICAgaGVpZ2h0OiA1MCU7CiAgICAgICAgICAgIGxlZnQ6IDA7CiAgICAgICAgfQoKICAgICAgICBpbnB1dDpjaGVja2Vkfi5zbGlkZXItLTEgZGl2OmZpcnN0LWNoaWxkIHsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVZKC0xMDAlKTsKICAgICAgICAgICAgdHJhbnNpdGlvbi1kZWxheTogMC4xMjVzOwogICAgICAgIH0KCiAgICAgICAgaW5wdXQ6Y2hlY2tlZH4uc2xpZGVyLS0xIGRpdjpsYXN0LWNoaWxkIHsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVZKDEwMCUpOwogICAgICAgICAgICB0cmFuc2l0aW9uLWRlbGF5OiAwLjEyNXM7CiAgICAgICAgfQoKICAgICAgICBpbnB1dDpjaGVja2Vkfi5zbGlkZXItLTIgewogICAgICAgICAgICB0cmFuc2Zvcm06IHRyYW5zbGF0ZVgoMTAwJSk7CiAgICAgICAgICAgIHRyYW5zaXRpb24tZGVsYXk6IDAuMTI1czsKICAgICAgICB9CgogICAgICAgIGlucHV0OmNoZWNrZWR+LnNsaWRlci0tMyB7CiAgICAgICAgICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlWCgtMTAwJSk7CiAgICAgICAgICAgIHRyYW5zaXRpb24tZGVsYXk6IDBzOwogICAgICAgIH0KCiAgICAgICAgLnNsaWRlci0tMSBkaXY6Zmlyc3QtY2hpbGQgewogICAgICAgICAgICB0cmFuc2Zvcm06IHRyYW5zbGF0ZVkoMCk7CiAgICAgICAgICAgIHRvcDogMDsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogI2YzZjNmMzsKICAgICAgICAgICAgdHJhbnNpdGlvbi1kZWxheTogMHM7CiAgICAgICAgfQoKICAgICAgICAuc2xpZGVyLS0xIGRpdjpsYXN0LWNoaWxkIHsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVZKDApOwogICAgICAgICAgICBib3R0b206IDA7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICNmM2YzZjM7CiAgICAgICAgICAgIGJvcmRlci10b3A6IDFweCBzb2xpZCAjZTBlMGUwOwogICAgICAgICAgICB0cmFuc2l0aW9uLWRlbGF5OiAwczsKICAgICAgICB9CgogICAgICAgIC5zbGlkZXItLTIgewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjZTZlNmU2OwogICAgICAgICAgICB0cmFuc2l0aW9uLWRlbGF5OiAwLjEyNXM7CiAgICAgICAgICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlWCgwKTsKICAgICAgICAgICAgYm9yZGVyLWxlZnQ6IDFweCBzb2xpZCAjZDJkMmQyOwogICAgICAgIH0KCiAgICAgICAgLnNsaWRlci0tMyB7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICNlYmViZWI7CiAgICAgICAgICAgIHRyYW5zaXRpb24tZGVsYXk6IDAuMTI1czsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGV4KDApOwogICAgICAgICAgICBib3JkZXItcmlnaHQ6IDFweCBzb2xpZCAjZDJkMmQyOwogICAgICAgIH0KCiAgICAgICAgLyogLS0tLS0tLS0gU3dpdGNoIFN0eWxlcyAtLS0tLS0tLS0tLS0qLwogICAgICAgIFt0eXBlPSJjaGVja2JveCJdIHsKICAgICAgICAgICAgZGlzcGxheTogbm9uZTsKICAgICAgICB9CgogICAgICAgIC8qIFRvZ2dsZSAqLwogICAgICAgIFt0eXBlPSJjaGVja2JveCJdOmNoZWNrZWQrLmFwcCAudG9nZ2xlIHsKICAgICAgICAgICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVYKDEwMCUpOwogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMzQzMjNkOwogICAgICAgIH0KCiAgICAgICAgW3R5cGU9ImNoZWNrYm94Il06Y2hlY2tlZCsuYXBwIC5kYXJrIHsKICAgICAgICAgICAgb3BhY2l0eTogMTsKICAgICAgICB9CgogICAgICAgIFt0eXBlPSJjaGVja2JveCJdOmNoZWNrZWQrLmFwcCAubGlnaHQgewogICAgICAgICAgICBvcGFjaXR5OiAwLjU7CiAgICAgICAgfQoKICAgICAgICAvKiBBcHAgKi8KICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLmJvZHkgewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjYyNDJlOwogICAgICAgICAgICBjb2xvcjogd2hpdGU7CiAgICAgICAgfQoKICAgICAgICAvKiBDaXJjbGUgKi8KICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLmNyZXNjZW50IHsKICAgICAgICAgICAgdHJhbnNmb3JtOiBzY2FsZSgxKTsKICAgICAgICAgICAgYmFja2dyb3VuZDogIzI2MjQyZTsKICAgICAgICB9CgogICAgICAgIFt0eXBlPSJjaGVja2JveCJdOmNoZWNrZWQrLmFwcCAuY2lyY2xlIHsKICAgICAgICAgICAgYmFja2dyb3VuZDogbGluZWFyLWdyYWRpZW50KDQwZGVnLCAjODk4M2Y3LCAjYTNkYWZiIDcwJSk7CiAgICAgICAgfQoKICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLm1haW4tY2lyY2xlIHsKICAgICAgICAgICAgYmFja2dyb3VuZDogbGluZWFyLWdyYWRpZW50KDQwZGVnLCAjODk4M2Y3LCAjYTNkYWZiIDcwJSk7CiAgICAgICAgfQoKICAgICAgICAvKiBGYWIgKi8KICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLmZhYiB7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICMzNDMyM2Q7CiAgICAgICAgfQoKICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLmFycm93LAogICAgICAgIFt0eXBlPSJjaGVja2JveCJdOmNoZWNrZWQrLmFwcCAubWFyaywKICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLmJhdHRlcnkgewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiB3aGl0ZTsKICAgICAgICB9CgogICAgICAgIFt0eXBlPSJjaGVja2JveCJdOmNoZWNrZWQrLmFwcCAubmV0d29yayB7CiAgICAgICAgICAgIGJvcmRlci1jb2xvcjogdHJhbnNwYXJlbnQgdHJhbnNwYXJlbnQgd2hpdGUgdHJhbnNwYXJlbnQ7CiAgICAgICAgfQoKICAgICAgICBbdHlwZT0iY2hlY2tib3giXTpjaGVja2VkKy5hcHAgLnN3aXBlIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzM0MzIzZDsKICAgICAgICAgICAgb3BhY2l0eTogMTsKICAgICAgICB9CiAgICA8L3N0eWxlPgo8L2hlYWQ+Cgo8Ym9keT4KICAgIDxpbnB1dCB0eXBlPSJjaGVja2JveCIgaWQ9InN3aXRjaCIgLz4KICAgIDxkaXYgY2xhc3M9ImFwcCI+CiAgICAgICAgPGRpdiBjbGFzcz0iYm9keSI+CiAgICAgICAgICAgIDxkaXYgY2xhc3M9Im1haW4tY2lyY2xlIj48L2Rpdj4KICAgICAgICAgICAgPGRpdiBjbGFzcz0icGhvbmUiPgogICAgICAgICAgICAgICAgPCEtLSBUb3AgLS0+CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJtZW51Ij4KICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJ0aW1lIj52MS4yPC9kaXY+CiAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzcz0iaWNvbnMiPgoKICAgICAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgPCEtLSBNaWRkbGUgLS0+CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJjb250ZW50Ij4KICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJjaXJjbGUiPgogICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJjcmVzY2VudCI+PC9kaXY+CiAgICAgICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICAgICAgPHAgY2xhc3M9ImhlYWRpbmciPllvdVR1YmUgRG93bmxvYWRlcjwvcD4KICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSIiPgogICAgICAgICAgICAgICAgICAgICAgICA8Zm9ybSBhY3Rpb249Ii9wcm9jZXNzX2RhdGEiIG1ldGhvZD0icG9zdCI+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8aW5wdXQgdHlwZT0idGV4dCIgbmFtZT0iaW5wdXRfZGF0YSIgcGxhY2Vob2xkZXI9IkVudGVyIHRoZSBuYW1lIG9mIHRoZSBzb25nLi4uIj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxsYWJlbCBjbGFzcz0ic3dpdGNoIj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8aW5wdXQgdHlwZT0iY2hlY2tib3giIG5hbWU9ImFfdiI+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzcz0ic2xpZGVyIHNsaWRlci0tMCI+VklERU88L2Rpdj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJzbGlkZXIgc2xpZGVyLS0xIj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPGRpdj48L2Rpdj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPGRpdj48L2Rpdj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJzbGlkZXIgc2xpZGVyLS0yIj48L2Rpdj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJzbGlkZXIgc2xpZGVyLS0zIj5BVURJTzwvZGl2PgogICAgICAgICAgICAgICAgICAgICAgICAgICAgPC9sYWJlbD4KICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxidXR0b24gY2xhc3M9ImZpbmFsIiB0eXBlPSJzdWJtaXQiPlN1Ym1pdDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgICAgICA8L2Zvcm0+CiAgICAgICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICAgICAgPGg1IHN0eWxlPSJhbGlnbi1jb250ZW50OiBsZWZ0OyI+CiAgICAgICAgICAgICAgICAgICAgICAgIFdhbm5hIGdldCByaWQgb2Ygb25saW5lIG11c2ljPyA8YnI+VGhpcyBpcyBmb3IgeW91ISAmbmJzcCBKdXN0IGVudGVyIHRoZSAmbmJzcDxicj4gdGl0bGUKICAgICAgICAgICAgICAgICAgICAgICAgYW5kIHRoZXJlCiAgICAgICAgICAgICAgICAgICAgICAgIHlvdSBoYXZlIGl0ISAmbmJzcCZuYnNwJm5ic3AmbmJzcCZuYnNwJm5ic3AmbmJzcCZuYnNwCiAgICAgICAgICAgICAgICAgICAgPC9oNT4KICAgICAgICAgICAgICAgICAgICA8bGFiZWwgZm9yPSJzd2l0Y2giPgogICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJ0b2dnbGUiPjwvZGl2PgogICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJuYW1lcyI+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8cCBjbGFzcz0ibGlnaHQiPkxpZ2h0PC9wPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgPHAgY2xhc3M9ImRhcmsiPkRhcms8L3A+CiAgICAgICAgICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgICAgIDwvbGFiZWw+CgogICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9Im1hcmsiPjwvZGl2PgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICA8IS0tIEJvdHRvbSAtLT4KICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9InNraXAiPgogICAgICAgICAgICAgICAgPC9kaXY+CgogICAgICAgICAgICAgICAgPCEtLSA8ZGl2IGNsYXNzPSJzd2lwZSI+PC9kaXY+IC0tPgogICAgICAgICAgICA8L2Rpdj4KICAgICAgICA8L2Rpdj4KICAgICAgICA8ZGl2IGNsYXNzPSJjcmVkaXQiPgogICAgICAgICAgICA8cD4KICAgICAgICAgICAgICAgIENyZWF0ZWQgYnkKICAgICAgICAgICAgICAgIDxhIGhyZWY9Imh0dHBzOi8vZ2l0aHViLmNvbS9jaGlubWF5a3Jpc2hucm95IiB0YXJnZXQ9Il9ibGFuayI+Q2hpbm1heSBLcmlzaG4gUm95PC9hPgogICAgICAgICAgICA8L3A+CiAgICAgICAgPC9kaXY+CiAgICA8L2Rpdj4KPC9ib2R5PgoKPC9odG1sPgo="

invalidFilenameChars, txt, alert, display_alert, message = ['|', '"', "'", ':', '*', '?', '\\', '/', '<', '>'], 'utf-8', "", False, "Downloaded"
logo = ("\033[7m\033[93mP\033[0m\033[7m\033[1;37mR\033[0m\033[7m\033[93mE\033[0m\033[7m\033"
        "[1;37mF\033[0m\033[7m\033[93mE\033[0m\033[7m\033[1;37mC\033[0m\033[7m\033[93mT\033[0m")

def validFileName(fileName, invalidASCII):
    invalidCharIndex = []
    for i in range(len(invalidASCII)):
        for j in range(len(fileName)):
            if fileName[j] == invalidASCII[i]: invalidCharIndex.append(j)
    if len(invalidCharIndex) == 0: return fileName
    invalidCharIndex.sort()
    if len(fileName[:invalidCharIndex[0]].strip()): return fileName[:invalidCharIndex[0]].strip()
    else: return ''.join(list(filter(lambda x: fileName.index(x) not in invalidCharIndex, fileName)))

def topResults(videoName, mode=False, maxLimit=5):
    tryURL = videoName.strip()[::-1]
    if (tryURL.endswith('=v?hctaw/moc.ebutuoy.www//:sptth')):
        try: downloadMedia(videoName, tryURL[0:10], mode)
        except Exception as e: print("\033[91mERROR!\033[0m\t\033[3m\033[0;37m%s\033[0m\033[0m"%e)
        return
    try:
        global alert, display_alert, message
        alert, display_alert, message = "", False, "Downloaded"
        from youtubesearchpython import VideosSearch
        videosSearch = VideosSearch(videoName, limit=maxLimit)
        results = videosSearch.result()["result"]
        if not len(results):
            print("\033[0;31mnot found any search result!\033[0m\033[0m")
            return
        for i, video in enumerate(results, 1):
            print(f"\033[1m{i}\033[0m. \033[95m{video['title']}\033[0m - {video['link']}")
        selectedIndex = 1 #int(input("\033[93mEnter the number of the video you want to download: \033[0m"))
        if 1 <= selectedIndex <= maxLimit:
            selectedVideo = results[selectedIndex - 1]
            mediaName = validFileName(selectedVideo["title"], invalidFilenameChars)
            try: downloadMedia(selectedVideo["id"], mediaName, mode)
            except: downloadMedia(selectedVideo["id"], selectedVideo["title"], mode)
        else: print("\033[91mNot a valid choice!\033[0m\033[0m")
    except Exception as e: 
        alert, display_alert, message = "%s"%e, True, "Failed"
        print("\r\033[91mERROR!\033[0m\t\033[3m\033[0;37m%s\033[0m\033[0m"%e)

def downloadMedia(videoID, videoName, av=False):
    if (videoID.endswith('=v?hctaw/moc.ebutuoy.www//:sptth')): videoURL = videoID
    else: videoURL = f"https://www.youtube.com/watch?v={videoID}"
    from pytube import YouTube
    yt = YouTube(videoURL)
    import os, platform
    if platform.system() == "Windows": location = "C:/Users/%s/Downloads"%os.getlogin()
    elif os.getlogin()[::-1].endswith('_0u'): location = "/storage/emulated/0/Download"
    elif platform.system() == "Linux": location = "/home/%s/Downloads"%os.getlogin()
    elif platform.system() == "Darwin": location = "/Users/%s/Downloads"%os.getlogin()
    else: location = ""
    print("\r\033[6m\033[1;30mDOWNLOADING...\033[0m\033[0m", end='')
    if av:
        mediaStream, outputPath, fileName = yt.streams.get_highest_resolution(), location + "/YouTube Video", f"{videoName}.mp4"
        mediaStream.download(outputPath, filename=fileName)
    else:
        mediaStream, outputPath, fileName = yt.streams.filter(only_audio=True).first(), location + "/YouTube Audio", f"{videoName}.mp3"
        mediaStream.download(outputPath, filename=fileName)
    print("\r\033[92mDOWNLOADED SUCCESSFULLY!\033[0m")

import base64
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index(): return base64.b64decode(dta.encode(txt)).decode(txt)

@app.route('/process_data', methods=['POST'])
def process_data():
    if request.method == 'POST':
        data = request.form['input_data']
        checkbox_value = request.form.get('a_v', False)
        # Make mode=True for video downloading
        topResults(data, mode=checkbox_value, maxLimit=1)
        global alert, display_alert, message
        content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{message}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #082020;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    text-align: center;
                }}
                .logo-container {{
                    display: inline-block;
                    color: #fff;
                    position: relative;
                }}
                .youtube-logo {{
                    width: 100px;
                    height: 100px;
                    fill: #2e2950;
                    /* Red color for YouTube logo */
                    position: relative;
                    top: 2px;
                    /* Adjust the vertical position */
                }}
                .downloaded-text {{
                    display: inline-block;
                    font-size: 50px;
                    align-self: center;
                    color: #fff;
                    margin-left: 10px;
                    margin-bottom: 85px;
                    /* Adjust the space between the logo and text */
                    vertical-align: middle;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo-container">
                    <svg fill="#000000" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
                        xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 96.875 96.875" xml:space="preserve"
                        class="youtube-logo">
                        <g><path d="M95.201,25.538c-1.186-5.152-5.4-8.953-10.473-9.52c-12.013-1.341-24.172-1.348-36.275-1.341
                c-12.105-0.007-24.266,0-36.279,1.341c-5.07,0.567-9.281,4.368-10.467,9.52C0.019,32.875,0,40.884,0,48.438
                C0,55.992,0,64,1.688,71.336c1.184,5.151,5.396,8.952,10.469,9.52c12.012,1.342,24.172,1.349,36.277,1.342
                c12.107,0.007,24.264,0,36.275-1.342c5.07-0.567,9.285-4.368,10.471-9.52c1.689-7.337,1.695-15.345,1.695-22.898
                C96.875,40.884,96.889,32.875,95.201,25.538z M35.936,63.474c0-10.716,0-21.32,0-32.037c10.267,5.357,20.466,10.678,30.798,16.068
                C56.434,52.847,46.23,58.136,35.936,63.474z" />
                        </g>
                    </svg>
                    <span class="downloaded-text">{message}</span>
                </div>
            </div>
            <script>
            var message = "{alert}";
            var displayAlert = {str(display_alert).lower()};
            if (displayAlert) {{alert(message);}}
            </script>
        </body>
        </html>
        """
        return content
        
import webbrowser
if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5005")
    app.run(debug=False, port=5005)
