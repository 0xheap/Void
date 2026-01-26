# Archive Inspector Scoring Logic

## How the Inspector Finds the "Perfect" Executable

The inspector uses a **scoring system** to rank potential executables. The highest-scoring executable is recommended as the `bin_path`.

### Scoring Breakdown

#### Base Scores (Always Applied)
- **+10 points**: File is executable (has execute permissions)
- **+5 points**: File matches binary patterns (no extension, common binary names, etc.)
- **+8 points**: Located in common binary directories (`bin/`, `usr/bin/`, `usr/local/bin/`)
- **+3 points**: No file extension (common for Linux binaries)

#### Size-Based Scoring
- **+1 to +10 points**: Based on file size
  - 1 point per 10MB of file size
  - Maximum 10 points
  - **Why**: Main applications are usually larger than helper utilities
  - Example: 47MB file = +4 points, 5MB file = +0 points

#### Name-Based Scoring

**Penalties (Negative Scores):**
- **-15 points**: Contains helper/worker keywords:
  - `worker`, `helper`, `daemon`, `service`
  - `gfx`, `gui`, `backend`, `server`, `client`
  - `plugin`, `extension`, `launcher`, `wrapper`, `shim`, `proxy`
  - **Why**: These are usually support processes, not the main app

**Bonuses (Positive Scores):**
- **+5 points**: Simple name (no hyphens or underscores)
  - Example: `megasync` gets bonus, `mega-desktop-app-gfxworker` doesn't
- **+3 points**: Short name (≤10 characters)
- **-3 points**: Very long name (>25 characters)
- **+5 points**: Common main executable names (`run`, `start`, `main`, `app`)
- **+2 points**: Ends with `sync` or `app` (common patterns)

### Example: Mega App Comparison

**File 1: `usr/bin/megasync`** (47MB)
```
Base scores:           +26 points (executable, binary pattern, in bin/, no extension)
Size bonus:            +4 points (47MB = ~4.7 × 10MB)
Simple name bonus:     +5 points (no hyphens)
Short name bonus:      +3 points (8 characters)
─────────────────────────────────────────────────────
TOTAL SCORE:           38 points ⭐ WINNER
```

**File 2: `usr/bin/mega-desktop-app-gfxworker`** (39MB)
```
Base scores:           +26 points (executable, binary pattern, in bin/, no extension)
Size bonus:            +3 points (39MB = ~3.9 × 10MB)
Worker penalty:        -15 points (contains "worker" and "gfx")
Complex name penalty:  -5 points (3 hyphens)
Long name penalty:     -3 points (28 characters)
─────────────────────────────────────────────────────
TOTAL SCORE:           6 points ❌ Helper utility
```

### Result
The inspector recommends `usr/bin/megasync` because it has a **much higher score** (38 vs 6).

## Why This Works

1. **Main apps are bigger**: The primary executable usually contains more code
2. **Main apps have simpler names**: `megasync` vs `mega-desktop-app-gfxworker`
3. **Helper processes are identifiable**: Names like "worker", "helper", "daemon" indicate support processes
4. **Location matters**: Files in `bin/` directories are more likely to be main executables

## Manual Override

If the inspector picks the wrong file, you can:
1. Check the list of all potential executables (top 10 are shown)
2. Look at the scores to understand why each was ranked
3. Manually choose a different `bin_path` from the list

The inspector is a **helper tool** - it makes educated guesses, but you always have the final say!
