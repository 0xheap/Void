# Icon Detection Fix - Quick Summary

## What Was Fixed

Applications installed by Void now properly detect and display their icons in the application menu.

## The Problem

Before this fix:
- Apps showed generic terminal icons instead of their actual icons
- Icon search was too shallow (only 3 levels deep)
- Didn't parse `.desktop` files that come with apps
- Didn't prioritize app-specific icon names

## The Solution

Enhanced icon detection that:
1. ✅ Parses `.desktop` files to extract icon paths
2. ✅ Searches deeper (5 levels) in app directories
3. ✅ Prioritizes icons matching the app name
4. ✅ Looks in standard locations (`share/icons/`, `share/pixmaps/`)
5. ✅ Prefers vector graphics (.svg) over raster images
6. ✅ Shows debug output when creating desktop entries

## How to Use

### For New Installations
Just install apps normally - icons will be detected automatically:
```bash
./void.py install vscode
```

### For Existing Installations
Refresh desktop entries to fix missing icons:
```bash
# Fix all installed apps
./void.py refresh-icons

# Fix specific app
./void.py refresh-icons discord
```

## What You'll See

When installing or refreshing:
```
Creating desktop entry for vscode...
Found icon: /goinfre/user/void/apps/vscode/.../code.png
Created desktop entry: ~/.local/share/applications/void_vscode.desktop
```

If no icon is found:
```
No icon found for myapp, using default
```

## Files Changed

- `modules/installer.py` - Enhanced `find_icon()` function
- `void.py` - Added `refresh-icons` command
- `README.md` - Updated documentation

## Testing

Verified with:
- Unit tests for icon detection logic
- Manual testing with various app structures
- Desktop file parsing tests

---

**Result:** Apps now show their proper icons in your application menu! 🎨
