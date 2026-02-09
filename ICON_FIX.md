# Icon Detection Fix

## Problem
When applications were installed, their icons weren't being properly detected and linked in desktop entries. This resulted in generic terminal icons appearing in application menus instead of the app's actual icon.

## Root Causes

1. **Shallow search depth** - Icon search only went 3 levels deep, missing icons in deeper directories
2. **No .desktop file parsing** - Many apps include `.desktop` files with icon references that weren't being used
3. **Poor scoring algorithm** - Didn't prioritize app-specific icon names or common icon locations
4. **Missing app name context** - Icon finder didn't know the app name to match against icon filenames

## Solution

### Enhanced Icon Detection (`find_icon` function)

The improved icon detection now:

1. **Parses .desktop files first** - Extracts `Icon=` field from bundled `.desktop` files
2. **Searches deeper** - Increased depth from 3 to 5 levels
3. **Better scoring**:
   - +10 points for icons in `icons/` or `pixmaps/` directories
   - +15 points for filenames matching the app name
   - +5 points for generic "icon" or "logo" names
   - +3 points for vector graphics (.svg)
   - +4 points for larger sizes (128, 256, 512, scalable)
4. **App name matching** - Passes app name to prioritize matching icon files

### New Command: `refresh-icons`

Regenerate desktop entries for already-installed apps to pick up the improved icon detection:

```bash
# Refresh all installed apps
./void.py refresh-icons

# Refresh specific app
./void.py refresh-icons vscode
```

## Usage

### For New Installations
Icons will be automatically detected with the improved algorithm. No action needed.

### For Existing Installations
Run the refresh command to update desktop entries:

```bash
./void.py refresh-icons
```

This will:
- Scan all installed apps
- Re-run icon detection with the improved algorithm
- Regenerate `.desktop` files with correct icon paths
- Update your application menu

## Technical Details

### Icon Search Priority

1. **Desktop file icons** - `Icon=` field in `.desktop` files
2. **App-named icons** - Files matching the app name (e.g., `vscode.png` for vscode)
3. **Standard locations** - `share/icons/`, `share/pixmaps/`
4. **Generic names** - `icon.png`, `logo.svg`, etc.
5. **Fallback** - Generic "utilities-terminal" icon if nothing found

### Supported Icon Formats

- `.svg` (preferred - vector graphics)
- `.png` (common raster format)
- `.xpm` (X11 pixmap)
- `.ico` (Windows icon format)

### Debug Output

When creating desktop entries, Void now prints:
- `Found icon: /path/to/icon.png` - Icon successfully detected
- `No icon found for <app>, using default` - Fallback to generic icon

## Examples

### Before Fix
```
Creating desktop entry: ~/.local/share/applications/void_vscode.desktop
Icon=utilities-terminal  # Generic icon
```

### After Fix
```
Creating desktop entry: ~/.local/share/applications/void_vscode.desktop
Found icon: /goinfre/user/void/apps/vscode/VSCode-linux-x64/resources/app/resources/linux/code.png
Icon=/goinfre/user/void/apps/vscode/VSCode-linux-x64/resources/app/resources/linux/code.png
```

## Testing

To verify the fix works:

1. Install an app: `./void.py install vscode`
2. Check the output for "Found icon: ..." message
3. Open your application menu and verify the icon appears
4. For existing apps: `./void.py refresh-icons`

## Related Files

- `modules/installer.py` - `find_icon()` and `create_desktop_entry()` functions
- `void.py` - `cmd_refresh_icons()` command handler
- Desktop entries: `~/.local/share/applications/void_*.desktop`
