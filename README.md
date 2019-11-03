## Check out SBPE by atomizer [Here](https://github.com/atomizer/sbpe).
### `[plugin_hp_dots]` - visually signifies how many hp packs are needed till max hp

- `dot_size`: size of the dots in pixels.
- `dot_y`: vertical offset of the dots from the top of the character.
- `dot_color`, `dot_outline`: dot colors.
### `[plugin_playerlist]` - an improvement of atomizer's *playerlist*

- `visible`: recommended to keep disabled and add a keybind.
- `size`: font size.

### `[plugin_zoom]` - atomizer's *zoom* but height based.

- `fast`: whether to use fast method or slow but correct method. Fast method has some minor inaccuracies: some background visual elements can change position when zooming (most prominently, the ai statue in eschaton), and the "outside" of "underground" rooms can be empty when zooming out instead of being filled with tiles.
- `level`: zoom level, represents internal canvas **height** in pixels. `-1` means the native 1:1 scale. Recommended to leave at `-1` and set keybind(s) for the level(s) you want. See `[plugin_keybinds]` for info about keybinds.
- `time`: transition time, set to 0 for instant. If using slow method, 0 is recommended.
