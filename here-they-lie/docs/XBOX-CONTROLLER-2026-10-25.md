> Final update: the polling change is included in the installed audio-corrected executable and passed three complete route tests. The staging/testing notes below describe the earlier investigation. See [current acceptance results](AUDIO-FIX-2026-10-25.md).

# Xbox controller calibration

Xbox One S was detected as player 1 by SDL. Menu maps to Options, Enter also maps to Options. Hold Menu for about two seconds at startup; the user confirmed calibration cleared and gameplay began on the existing executable.

Inspection also found the 0.20 integration PollState timer only smoothed sticks, without publishing unchanged controller samples or polling held Options gestures. A native rebuild restores recurring samples, sensor data and held view gestures, while leaving HTL sticks/triggers as ordinary DualShock controls instead of Astro touchpad gestures.

The rebuild is staged as shadps4-input-polling.pending.exe in the candidate runtime. The normal launcher applies it only after confirming the previous game process has exited, retaining source-build020-before-input-polling.exe. Current gameplay is uninterrupted. Native build passed; the staged binary has not yet had a full route or physical controller test. Previous full-route qualification applies to the previous binary.

Mappings: Menu=Options, A=Cross, B=Circle, X=Square, Y=Triangle, View=touchpad click, LB/RB=L1/R1, LT/RT=L2/R2, stick clicks=L3/R3.
