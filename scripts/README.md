# Neovim Config Setup Script

## What It Does

1. **Clones** your nvim config from GitHub to `/goinfre/$USER/nvim-config`
2. **Symlinks** `~/.config/nvim` → `/goinfre/$USER/nvim-config`
3. **Saves space** in your home directory (5GB limit)

## Setup

### 1. Edit the Script

Open `scripts/setup-nvim-config.sh` and replace the GitHub URL:

```bash
# Line 33 - Replace with your repo
git clone https://github.com/YOUR_USERNAME/nvim-config.git "$GOINFRE_NVIM"
```

**Example:**
```bash
git clone https://github.com/abdessel/nvim-config.git "$GOINFRE_NVIM"
```

### 2. Test the Script

```bash
bash scripts/setup-nvim-config.sh
```

**Output:**
```
=== Neovim Config Setup ===

Cloning nvim config to /goinfre/abdessel/nvim-config...
Creating symlink: /home/abdessel/.config/nvim -> /goinfre/abdessel/nvim-config

✓ Success! Nvim config linked to goinfre
  Config location: /goinfre/abdessel/nvim-config
  Symlink: /home/abdessel/.config/nvim
```

### 3. Use with Void (Automatic)

Add to your `~/.config/void/custom_apps.json`:

```json
{
    "neovim": {
        "name": "Neovim",
        "url": "https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.appimage",
        "type": "appimage",
        "bin_path": "nvim-linux-x86_64.appimage",
        "link_name": "nvim",
        "post_install": [
            "bash ~/Tools/Void/scripts/setup-nvim-config.sh"
        ]
    }
}
```

Now when you install neovim:
```bash
./void.py install neovim
```

It will:
1. Install neovim to `/goinfre`
2. Automatically clone your config to `/goinfre`
3. Create symlink to `~/.config/nvim`

## Manual Usage

Run the script anytime:
```bash
bash scripts/setup-nvim-config.sh
```

## What Happens to Existing Config?

- **If `~/.config/nvim` exists** → Backed up to `~/.config/nvim.backup`
- **If it's already a symlink** → Removed and recreated
- **If config exists in goinfre** → Pulls latest changes (git pull)

## Benefits

- ✅ **Saves space** - Config in goinfre, not home
- ✅ **Automatic** - Runs on neovim install
- ✅ **Safe** - Backs up existing config
- ✅ **Updates** - Pulls latest if already cloned
- ✅ **Portable** - Same config across workstations

## Verify It Works

```bash
# Check symlink
ls -la ~/.config/nvim

# Should show:
# ~/.config/nvim -> /goinfre/abdessel/nvim-config

# Check config location
ls /goinfre/$USER/nvim-config

# Should show your nvim config files
```

## Troubleshooting

### Script fails with "permission denied"
```bash
chmod +x scripts/setup-nvim-config.sh
```

### Wrong GitHub URL
Edit line 33 in `scripts/setup-nvim-config.sh`

### Config not loading in nvim
```bash
# Check symlink
ls -la ~/.config/nvim

# Should point to goinfre, not be a regular directory
```

### Want to use different repo
Edit the script and change the git clone URL

## Advanced: Multiple Configs

You can create similar scripts for other tools:

**VSCode:**
```bash
# scripts/setup-vscode-config.sh
git clone https://github.com/user/vscode-config.git /goinfre/$USER/vscode-config
ln -sf /goinfre/$USER/vscode-config ~/.config/Code/User
```

**Zsh:**
```bash
# scripts/setup-zsh-config.sh
git clone https://github.com/user/zsh-config.git /goinfre/$USER/zsh-config
ln -sf /goinfre/$USER/zsh-config/.zshrc ~/.zshrc
```

Then add to post_install for each app!
