# RUSH RUNNER - ENDLESS ADVENTURE

Offline endless runner for Android. Built with **Kivy + Buildozer** (see "Framework note"), APK built by GitHub Actions - no PC needed.

## Framework note (important, honest)
Your brief asked for Pygame. Pygame has no official, maintained Android packaging path (no recipe for current pygame releases that I could verify, and community pygame-ce recipes are experimental). You said to use something else if a phone + GitHub-only build is not possible with Pygame, so this project uses **Kivy** (still Python, SDL2-based, built by the standard Buildozer/python-for-android toolchain). Rendering is 2D with perspective scaling - it is **not** a 3D engine.

## Upload from your Android phone (browser)
1. Open github.com, sign in, tap **+ > New repository**, name it `rush-runner-game`, create it.
2. Unzip `rush-runner-game.zip` on the phone (Files app). Open the repo > **Add file > Upload files** and select ALL files from the folder (`*.py`, `buildozer.spec`, `assets` folder contents). Android browsers often cannot upload folders: upload files in groups, and for `assets/sounds/*.wav` and `assets/icons/icon.png` use **Add file > Create new file**, type the path in the name box (e.g. `assets/sounds/`) - or simply skip the assets: the workflow regenerates them automatically (`generate_assets.py`), but `icon.png` must exist before the build, so keep `generate_assets.py` uploaded.
3. Create the workflow: **Add file > Create new file**, name it `.github/workflows/android-apk.yml` (typing `/` creates folders), paste the contents of that file, **Commit changes** to `main`.
4. Open the **Actions** tab > **Build Android APK** > **Run workflow** (it also runs on every push to `main`).
5. First build takes roughly 20-40 min (downloads SDK/NDK). Tap the running job to watch the log. Red X = failure: open the failed step; the `build-log` artifact has the full log.
6. When green, open the run, scroll to **Artifacts**, download **RUSH-RUNNER-ANDROID-APK** (a zip), unzip, tap the `.apk`, allow "install unknown apps" for your browser/Files app, install.

## Controls
- Swipe left/right = change lane, up = jump, down = slide.
- Tilt (Settings > Control Style: Touch / Phone Tilt / Both). Sensitivity Low/Medium/High. **CALIBRATE NOW** takes your current holding angle as neutral. The bar in Settings shows the live sensor value.
- Android Back: pauses in game, goes back in menus, press twice on Home to quit.

## Files
`main.py` app/lifecycle - `game.py` renderer, HUD, pause, results - `game_logic.py` rules - `controls.py` swipe/tilt logic - `sensors.py` accelerometer (plyer) - `menu.py` screens - `ui_components.py` neon UI - `player.py` `obstacles.py` `coins.py` art - `save_manager.py` offline JSON saves - `settings.py` options/languages - `generate_assets.py` creates sounds + icon - `test_logic.py` unit tests.

## Testing checklist (tick on your phone)
Home opens - Play starts - Character select changes runner (locked ones need coins) - swipes - tilt + calibrate - coins - obstacles hurt - pause/resume/restart/home - game over - level complete - high score + settings persist after closing - airplane mode - Back button.

## Troubleshooting
- Build red at "Build debug APK": open the log, look for the first `ERROR`. Re-run once (network hiccups happen).
- "App not installed": uninstall any older version first.
- Tilt does nothing: Settings shows "No accelerometer found" if the sensor/plyer failed; use Touch.
- Free-tier Actions minutes are limited; don't re-run needlessly.
