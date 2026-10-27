# Here They Lie / PSVR project handoff

Read `docs/RESUME-HERE.md` before changes or advice about the current runtime. Read `docs/DEVELOPMENT-HISTORY.md` for failed experiments and evidence. For other PSVR titles, read `docs/PSVR-PORTING-PLAYBOOK.md`; reuse methods, not title-specific ABI layouts, memory offsets, asset signatures or patches.

The latest physical Quest candidate differs from normal desktop/audio launchers. Preserve the user-confirmed upright tracking, audio and native comfort behavior. Do not reintroduce the failed upright-pose gate, global image flip, forced no-vignette asset, or broad stack-protection setting as though it were a demonstrated fix. The narrow stack reservation is opt-in and exact-function-checked; the user's crash-free retest was battery-limited.

After new results update RESUME-HERE and label evidence as code/unit/model test, desktop replay, physical user observation or hypothesis. Do not erase historical failures. Never commit game assets, keys/modules, private saves/captures or build binaries. Source changes are exported as pinned patches; check patch application before documenting a rebuild as reproducible.
