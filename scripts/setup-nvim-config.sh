#!/bin/bash
#
# Neovim Config Setup Script
# Clones nvim config to /goinfre and symlinks ALL nvim data
#

set -e

USER=${USER:-$(whoami)}
GOINFRE_BASE="/goinfre/$USER/nvim"
HOME_CONFIG="$HOME/.config/nvim"
HOME_DATA="$HOME/.local/share/nvim"
HOME_STATE="$HOME/.local/state/nvim"
HOME_CACHE="$HOME/.cache/nvim"

echo "=== Neovim Complete Setup ==="
echo ""

# Function to move and symlink
move_and_link() {
    local home_path="$1"
    local goinfre_path="$2"
    local name="$3"
    
    # Remove broken symlink
    if [ -L "$home_path" ] && [ ! -e "$home_path" ]; then
        echo "Removing broken symlink: $home_path"
        rm "$home_path"
    fi
    
    # Move existing directory to goinfre
    if [ -d "$home_path" ] && [ ! -L "$home_path" ]; then
        echo "Moving $name to goinfre..."
        mkdir -p "$(dirname "$goinfre_path")"
        mv "$home_path" "$goinfre_path"
    fi
    
    # Create directory in goinfre if doesn't exist
    if [ ! -e "$goinfre_path" ]; then
        echo "Creating $name in goinfre..."
        mkdir -p "$goinfre_path"
    fi
    
    # Create symlink
    echo "Linking $name..."
    mkdir -p "$(dirname "$home_path")"
    ln -sf "$goinfre_path" "$home_path"
}

# 1. Move config (or clone from GitHub)
if [ -d "$GOINFRE_BASE/config" ]; then
    echo "Config exists in goinfre, pulling latest..."
    cd "$GOINFRE_BASE/config"
    git pull 2>/dev/null || echo "Not a git repo, skipping pull"
else
    if [ -d "$HOME_CONFIG" ] && [ ! -L "$HOME_CONFIG" ]; then
        echo "Moving existing config to goinfre..."
        mkdir -p "$GOINFRE_BASE"
        mv "$HOME_CONFIG" "$GOINFRE_BASE/config"
    else
        echo "Cloning nvim config to goinfre..."
        mkdir -p "$GOINFRE_BASE"
        # Clone your nvim config
        git clone git@github.com:0xheap/nvim.git "$GOINFRE_BASE/config"
    fi
fi

# Remove old symlink if exists
[ -L "$HOME_CONFIG" ] && rm "$HOME_CONFIG"

# Create config symlink
echo "Linking config..."
mkdir -p "$HOME/.config"
ln -sf "$GOINFRE_BASE/config" "$HOME_CONFIG"

# 2. Move data directory (plugins, lazy.nvim, mason, etc.)
move_and_link "$HOME_DATA" "$GOINFRE_BASE/data" "data"

# 3. Move state directory (shada, logs, etc.)
move_and_link "$HOME_STATE" "$GOINFRE_BASE/state" "state"

# 4. Move cache directory
move_and_link "$HOME_CACHE" "$GOINFRE_BASE/cache" "cache"

echo ""
echo "✓ Success! All nvim data moved to goinfre"
echo ""
echo "Locations:"
echo "  Config:  $HOME_CONFIG -> $GOINFRE_BASE/config"
echo "  Data:    $HOME_DATA -> $GOINFRE_BASE/data"
echo "  State:   $HOME_STATE -> $GOINFRE_BASE/state"
echo "  Cache:   $HOME_CACHE -> $GOINFRE_BASE/cache"
echo ""
echo "Space saved in home directory!"
