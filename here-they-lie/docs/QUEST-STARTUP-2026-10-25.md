# Physical Quest startup follow-up

User saw inverted splash/calibration screens, which became upright after Menu, then a loading crash. Preserved log ends with CopyCmdBuffers assertion: dcb copy buffer out of reserved space. Initial OpenXR quaternion is near a180-degree roll; later it is upright. This is distinct from the previously tested texture Y flip. No unconditional flip or gravity override was added.

The isolated candidate keeps the normal fixed arena path, serializes reservations with SubmitDone, and allocates independently owned overflow copies when a submission exceeds remaining capacity. The graphics/CE coroutine frames retain those copies through parsing. No in-flight arena reallocation, disabled-copy workaround or GPU wait was introduced. Audio gain/protection settings remain intact. Added startup tracking-flag logging to distinguish stale valid poses from active tracking.

Native build and command_copy_smoke checks passed. The incremental patch htl-quest-startup-copyfix.patch applies after the stable integration patch; it is not part of the default stable Build-Integration020 workflow yet. Candidate requires physical loading and orientation retest before promotion. Normal preview remains the qualified audio build. A separate local Test-Here-They-Lie-Quest-Startup.cmd targets the isolated profile with copied warm caches. User was asked to wear/recenter the headset before testing. No claim that orientation is fixed yet.


## October 26 follow-up

The user subsequently played through several checkpoints with working physical head tracking, but startup remained inverted and a later guest render-thread read of address 0x58 ended the session. The newest candidate adds an eight-consecutive-tracked-upright-pose startup gate, defers theatre anchoring, and adds fault register logging. Physical validation of this newest change is pending. See [current status](PROJECT-STATUS-2026-10-26.md) for exact build hashes, evidence and unresolved limits.
