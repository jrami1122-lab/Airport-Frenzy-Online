# Airport Frenzy — Sound Library

**The audio engine and event triggers are wired in the game.** To enable playback, upload the eleven processed MP3 files from the supplied `Airport_Frenzy_Sound_Assets.zip` into **this exact folder** (`assets/audio/`) using GitHub → Add file → Upload files → Commit changes.

Expected names:
- `music_menu.mp3`: airport/terminal theme
- `music_arcade.mp3`: high-energy arcade challenges
- `music_cabin.mp3`: Flight Attendant
- `music_calm.mp3`: Terminal Assist and Document Control
- `sfx_flyover.mp3`: actual aircraft flyover
- `sfx_motor.mp3`: tugs, belts, motor systems
- `sfx_ding.mp3`: successful actions and customer orders
- `sfx_wrong.mp3`: incorrect actions
- `sfx_crash.mp3`: cart collisions
- `sfx_bag_drop.mp3`: baggage placement
- `sfx_thump.mp3`: cart coupling/impact

Music uses separate volume/fades and loops as a playlist. SFX are short and throttled; motor loops stop at game/menu transition. Browser sound requires a click or keypress before playback can begin.

This directory intentionally contains **no audio binaries yet**. The connected GitHub tools support code editing but do not support binary uploads from the chat sandbox. After the files are uploaded, Render's existing auto-deploy will serve them.
