
# Dictionary of supported applications and their metadata
SUPPORTED_APPS = {
    # --- IDEs & Editors ---
    "vscode": {
        "name": "Visual Studio Code",
        "url": "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64",
        "type": "tar.gz",
        "bin_path": "VSCode-linux-x64/bin/code",
        "link_name": "code",
        "data_paths": [
            ".vscode",         # Extensions (Home relative)
            ".config/Code"     # Cache & Config
        ]
    },
    "vscodium": {
        "name": "VSCodium",
        "url": "https://github.com/VSCodium/vscodium/releases/download/1.108.10359/VSCodium-1.108.10359.glibc2.30-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "VSCodium-1.108.10359.glibc2.30-x86_64.AppImage",
        "link_name": "codium"
    },
    "sublime": {
        "name": "Sublime Text 4",
        "url": "https://download.sublimetext.com/sublime_text_build_4169_x64.tar.xz",
        "type": "tar.xz",
        "bin_path": "sublime_text/sublime_text",
        "link_name": "subl"
    },
    "neovim": {
        "name": "Neovim",
        "url": "https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.appimage",
        "type": "appimage",
        "bin_path": "nvim-linux-x86_64.appimage",
        "link_name": "nvim"
    },
    "zed": {
         "name": "Zed Editor (Preview)",
         "url": "https://zed.dev/api/releases/stable/latest/zed-linux-x86_64.tar.gz",
         "type": "tar.gz",
         "bin_path": "zed.app/bin/zed",
         "link_name": "zed"
    },

    # --- JetBrains ---
    "pycharm-community": {
        "name": "PyCharm Community",
        "url": "https://download.jetbrains.com/python/pycharm-community-2023.3.3.tar.gz",
        "type": "tar.gz",
        "bin_path": "pycharm-community-2023.3.3/bin/pycharm.sh",
        "link_name": "pycharm"
    },
    "intellij-community": {
        "name": "IntelliJ IDEA Community",
        "url": "https://download.jetbrains.com/idea/ideaIC-2023.3.3.tar.gz",
        "type": "tar.gz",
        "bin_path": "idea-IC-233.14015.106/bin/idea.sh",
        "link_name": "idea"
    },
    "webstorm": {
        "name": "WebStorm",
        "url": "https://download.jetbrains.com/webstorm/WebStorm-2023.3.3.tar.gz",
        "type": "tar.gz",
        "bin_path": "WebStorm-233.14015.89/bin/webstorm.sh",
        "link_name": "webstorm"
    },
    "clion": {
        "name": "CLion",
        "url": "https://download.jetbrains.com/cpp/CLion-2023.3.3.tar.gz",
        "type": "tar.gz",
        "bin_path": "clion-2023.3.3/bin/clion.sh",
        "link_name": "clion"
    },
    "goland": {
        "name": "GoLand",
        "url": "https://download.jetbrains.com/go/goland-2023.3.3.tar.gz",
        "type": "tar.gz",
        # NOTE: Folder names update with versions. Fixed paths are brittle.
        # Ideally installer finds the bin automatically.
        "bin_path": "GoLand-2023.3.3/bin/goland.sh",
        "link_name": "goland"
    },
    "rider": {
        "name": "Rider",
        "url": "https://download.jetbrains.com/rider/JetBrains.Rider-2023.3.3.tar.gz",
        "type": "tar.gz",
        "bin_path": "JetBrains Rider-2023.3.3/bin/rider.sh",
        "link_name": "rider"
    },
    "datagrip": {
        "name": "DataGrip",
        "url": "https://download.jetbrains.com/datagrip/datagrip-2023.3.4.tar.gz",
        "type": "tar.gz",
        "bin_path": "DataGrip-2023.3.4/bin/datagrip.sh",
        "link_name": "datagrip"
    },
    "android-studio": {
        "name": "Android Studio",
        "url": "https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.1.1.28/android-studio-2023.1.1.28-linux.tar.gz",
        "type": "tar.gz",
        "bin_path": "android-studio/bin/studio.sh",
        "link_name": "studio"
    },

    # --- Communication ---
    "discord": {
        "name": "Discord",
        "url": "https://discord.com/api/download?platform=linux&format=tar.gz",
        "type": "tar.gz",
        "bin_path": "Discord/Discord",
        "link_name": "discord",
        "data_paths": [".config/discord"]
    },
    "telegram": {
        "name": "Telegram Desktop",
        "url": "https://telegram.org/dl/desktop/linux",
        "type": "tar.xz",
        "bin_path": "Telegram/Telegram",
        "link_name": "telegram"
    },
    "slack": {
         "name": "Zoom",
         "url": "https://zoom.us/client/latest/zoom_x86_64.tar.xz",
         "type": "tar.xz",
         "bin_path": "zoom/zoom",
         "link_name": "zoom"
    },
    "teams": {
        "name": "Teams for Linux",
        "url": "https://github.com/IsmaelMartinez/teams-for-linux/releases/download/v2.6.18/teams-for-linux-2.6.18.AppImage",
        "type": "appimage",
        "bin_path": "teams-for-linux-2.6.18.AppImage",
        "link_name": "teams"
    },
    "signal": {
        "name": "Beeper",
        "url": "https://download.beeper.com/linux/appImage/x64",
        "type": "appimage",
        "bin_path": "beeper.AppImage",
        "link_name": "beeper"
    },

    # --- API & DB Clients ---
    "postman": {
        "name": "Postman",
        "url": "https://dl.pstmn.io/download/latest/linux64",
        "type": "tar.gz",
        "bin_path": "Postman/app/Postman",
        "link_name": "postman"
    },
    "insomnia": {
        "name": "Insomnia",
        "url": "https://github.com/Kong/insomnia/releases/download/core%402023.5.8/Insomnia.Core-2023.5.8.AppImage",
        "type": "appimage",
        "bin_path": "Insomnia.Core-2023.5.8.AppImage",
        "link_name": "insomnia"
    },
    
    "dbeaver": {
        "name": "DBeaver Community",
        "url": "https://dbeaver.io/files/dbeaver-ce-latest-linux.gtk.x86_64.tar.gz",
        "type": "tar.gz",
        "bin_path": "dbeaver/dbeaver",
        "link_name": "dbeaver"
    },
    # "beekeeper": {
    #     "name": "Beekeeper Studio",
    #     "url": "https://github.com/beekeeper-studio/beekeeper-studio/releases/download/v5.5.4/Beekeeper-Studio-5.5.4-x86_64.AppImage",
    #     "type": "appimage",
    #     "bin_path": "Beekeeper-Studio-5.5.4-x86_64.AppImage",
    #     "link_name": "beekeeper"
    # },
    "mongodb-compass": {
        "name": "MongoDB Compass",
        # URL often specific version.
        "url": "https://downloads.mongodb.com/compass/mongodb-compass-1.40.4-linux-x64.tar.gz",
        "type": "tar.gz",
        "bin_path": "mongodb-compass-1.40.4-linux-x64/MongoDB-Compass",
        "link_name": "compass"
    },
    "redisinsight": {
        "name": "RedisInsight",
        "url": "https://download.redisinsight.redis.com/latest/Redis-Insight-linux-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "Redis-Insight-linux-x86_64.AppImage",
        "link_name": "redisinsight"
    },
    "bruno": {
        "name": "Bruno",
        "url": "https://github.com/usebruno/bruno/releases/download/v3.0.2/bruno_3.0.2_x86_64_linux.AppImage",
        "type": "appimage",
        "bin_path": "bruno_3.0.2_x86_64_linux.AppImage",
        "link_name": "bruno"
    },

    # --- Creative ---
    "blender": {
        "name": "Blender",
        "url": "https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz",
        "type": "tar.xz",
        "bin_path": "blender-4.0.2-linux-x64/blender",
        "link_name": "blender"
    },
    # "gimp": {
    #     "name": "GIMP",
    #     # "url": "https://download.gimp.org/gimp/v3.0/linux/gimp-3.0.6-x86_64.AppImage", # Official 404
    #     # Using alternate build or disable. 
    #     "url": "https://github.com/TasMania17/Gimp-Appimages/releases/download/v2.10.36/GIMP_2.10.36-x86_64.AppImage", # Guessing
    #     "type": "appimage",
    #     "bin_path": "GIMP_2.10.36-x86_64.AppImage",
    #     "link_name": "gimp"
    # },
    "krita": {
        "name": "Krita",
        "url": "https://download.kde.org/stable/krita/5.2.2/krita-5.2.2-x86_64.appimage",
        "type": "appimage",
        "bin_path": "krita-5.2.2-x86_64.appimage",
        "link_name": "krita"
    },
    "inkscape": {
        "name": "Inkscape",
        "url": "https://inkscape.org/gallery/item/44616/Inkscape-e7c3feb-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "Inkscape-e7c3feb-x86_64.AppImage",
        "link_name": "inkscape"
    },
    "audacity": {
        "name": "Audacity",
        "url": "https://github.com/audacity/audacity/releases/download/Audacity-3.4.2/audacity-linux-3.4.2-x64.AppImage",
        "type": "appimage",
        "bin_path": "audacity-linux-3.4.2-x64.AppImage",
        "link_name": "audacity"
    },
    
    # --- Utilities ---
    "obsidian": {
        "name": "Obsidian",
        "url": "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.5.3/Obsidian-1.5.3.AppImage",
        "type": "appimage",
        "bin_path": "Obsidian-1.5.3.AppImage",
        "link_name": "obsidian"
    },
    "notion-enhanced": {
        "name": "Notion Enhanced",
        "url": "https://github.com/notion-enhancer/notion-repackaged/releases/download/v2.0.18-1/Notion-2.0.18-1.AppImage",
        "type": "appimage",
        "bin_path": "Notion-2.0.18-1.AppImage",
        "link_name": "notion"
    },
    "joplin": {
        "name": "Joplin",
        "url": "https://github.com/laurent22/joplin/releases/download/v2.13.15/Joplin-2.13.15.AppImage",
        "type": "appimage",
        "bin_path": "Joplin-2.13.15.AppImage",
        "link_name": "joplin"
    },
    "bitwarden": {
        "name": "Bitwarden",
        "url": "https://github.com/bitwarden/clients/releases/download/desktop-v2024.1.0/Bitwarden-2024.1.0-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "Bitwarden-2024.1.0-x86_64.AppImage",
        "link_name": "bitwarden"
    },
    "keepassxc": {
        "name": "KeePassXC",
        "url": "https://github.com/keepassxreboot/keepassxc/releases/download/2.7.6/KeePassXC-2.7.6-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "KeePassXC-2.7.6-x86_64.AppImage",
        "link_name": "keepassxc"
    },
    "librewolf": {
        "name": "LibreWolf",
        "url": "https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/latest/LibreWolf.x86_64.AppImage",
        "type": "appimage",
        "bin_path": "LibreWolf.x86_64.AppImage",
        "link_name": "librewolf"
    },
    "cpu-x": {
        "name": "CPU-X",
        "url": "https://github.com/X0rg/CPU-X/releases/download/v5.4.0/CPU-X-5.4.0-x86_64.AppImage",
        "type": "appimage",
        "bin_path": "CPU-X-5.4.0-x86_64.AppImage",
        "link_name": "cpu-x"
    },
    "etcher": {
        "name": "Balena Etcher",
        "url": "https://github.com/balena-io/etcher/releases/download/v1.18.11/balenaEtcher-1.18.11-x64.AppImage",
        "type": "appimage",
        "bin_path": "balenaEtcher-1.18.11-x64.AppImage",
        "link_name": "etcher"
    },

    # --- CLI Tools (Binaries) ---
    "docker-client": {
        "name": "Docker CLI (Client only)",
        "url": "https://download.docker.com/linux/static/stable/x86_64/docker-25.0.1.tgz",
        "type": "tar.gz",
        "bin_path": "docker/docker",
        "link_name": "docker"
    },
    "lazygit": {
        "name": "Lazygit",
        "url": "https://github.com/jesseduffield/lazygit/releases/download/v0.40.2/lazygit_0.40.2_Linux_x86_64.tar.gz",
        "type": "tar.gz",
        "bin_path": "lazygit",
        "link_name": "lazygit"
    },
    "lazydocker": {
        "name": "Lazydocker",
        "url": "https://github.com/jesseduffield/lazydocker/releases/download/v0.23.1/lazydocker_0.23.1_Linux_x86_64.tar.gz",
        "type": "tar.gz",
        "bin_path": "lazydocker",
        "link_name": "lazydocker"
    },
    "btop": {
        "name": "Btop++",
        "url": "https://github.com/aristocratos/btop/releases/download/v1.3.0/btop-x86_64-linux-musl.tbz",
        "type": "tar.bz2",
        "bin_path": "btop/bin/btop",
        "link_name": "btop"
    },
    "bat": {
        "name": "Bat (Cat clone)",
        "url": "https://github.com/sharkdp/bat/releases/download/v0.24.0/bat-v0.24.0-x86_64-unknown-linux-musl.tar.gz",
        "type": "tar.gz",
        "bin_path": "bat-v0.24.0-x86_64-unknown-linux-musl/bat",
        "link_name": "bat"
    },
    "exa": {
        # Exa is unmaintained -> Eza
        "name": "Eza (Ls clone)",
        "url": "https://github.com/eza-community/eza/releases/download/v0.18.10/eza_x86_64-unknown-linux-gnu.tar.gz",
        "type": "tar.gz",
        "bin_path": "eza",
        "link_name": "eza"
    },
    "fd": {
        "name": "Fd (Find clone)",
        "url": "https://github.com/sharkdp/fd/releases/download/v9.0.0/fd-v9.0.0-x86_64-unknown-linux-musl.tar.gz",
        "type": "tar.gz",
        "bin_path": "fd-v9.0.0-x86_64-unknown-linux-musl/fd",
        "link_name": "fd"
    },
    "ripgrep": {
        "name": "Ripgrep",
        "url": "https://github.com/BurntSushi/ripgrep/releases/download/14.1.0/ripgrep-14.1.0-x86_64-unknown-linux-musl.tar.gz",
        "type": "tar.gz",
        "bin_path": "ripgrep-14.1.0-x86_64-unknown-linux-musl/rg",
        "link_name": "rg"
    },
    "fzf": {
        "name": "Fzf",
        "url": "https://github.com/junegunn/fzf/releases/download/0.46.0/fzf-0.46.0-linux_amd64.tar.gz",
        "type": "tar.gz",
        "bin_path": "fzf",
        "link_name": "fzf"
    },
    "nodejs": {
        "name": "Node.js (LTS)",
        "url": "https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz",
        "type": "tar.xz",
        "bin_path": "node-v20.11.0-linux-x64/bin/node",
        "link_name": "node"
    },
    "go": {
        "name": "Go (Language)",
        "url": "https://go.dev/dl/go1.21.6.linux-amd64.tar.gz",
        "type": "tar.gz",
        "bin_path": "go/bin/go",
        "link_name": "go"
    },
    "rust": {
        "name": "Rust (Language)",
        # "url": "https://github.com/rust-lang/rust/archive/refs/tags/1.92.0.tar.gz", # User's was source code
        # Using a valid standalone linux-gnu binary of Rust 1.75 (newer versions widely available but 1.75 is reliable)
        # Actually Search for "rust tar.gz binary" -> found static.rust-lang.org
        "url": "https://static.rust-lang.org/dist/rust-1.75.0-x86_64-unknown-linux-gnu.tar.gz",
        "type": "tar.gz",
        # Binaries are deep: rust-1.75.0.../rustc/bin/rustc
        # Installer might need deeper path or user meant 'rustup'. 
        # But 'rustup' is a script.
        # Let's set bin_path to the main rustc binary.
        "bin_path": "rust-1.75.0-x86_64-unknown-linux-gnu/rustc/bin/rustc",
        "link_name": "rustc"
        # Note: Cargo is separate in 'cargo/bin/cargo' in this tarball. 
        # Installer only links ONE bin. This is a limitation for Rust which needs cargo too.
        # For now, let's enable 'rustc'. 
    },
    
    # --- Student Essentials ---
    "helix": {
        "name": "Helix (Editor)",
        "url": "https://github.com/helix-editor/helix/releases/download/25.07.1/helix-25.07.1-x86_64-linux.tar.xz",
        "type": "tar.xz",
        "bin_path": "helix-25.07.1-x86_64-linux/hx",
        "link_name": "hx"
    },
    "glow": {
        "name": "Glow (Markdown Viewer)",
        "url": "https://github.com/charmbracelet/glow/releases/download/v2.1.1/glow_2.1.1_Linux_x86_64.tar.gz",
        "type": "tar.gz",
        "bin_path": "glow_2.1.1_Linux_x86_64/glow",
        "link_name": "glow"
    },
    "zoxide": {
        "name": "Zoxide (Smarter cd)",
        "url": "https://github.com/ajeetdsouza/zoxide/releases/download/v0.9.8/zoxide-0.9.8-x86_64-unknown-linux-musl.tar.gz",
        # Note: 448 search result said "zoxide-0.9.8-x86_64..." NOT "zoxide-x86_64..."
        "type": "tar.gz",
        "bin_path": "zoxide",
        "link_name": "zoxide"
    },
    "tealdeer": {
        "name": "Tldr (Tealdeer)",
        "url": "https://github.com/tealdeer-rs/tealdeer/releases/download/v1.7.0/tealdeer-linux-x86_64-musl",
        # Treating raw binary as appimage to chmod+x
        "type": "appimage",
        "bin_path": "tealdeer-linux-x86_64-musl",
        "link_name": "tldr"
    },
    "httpie": {
        "name": "HTTPie",
        "url": "https://packages.httpie.io/binaries/linux/http-latest",
        "type": "appimage",
        "bin_path": "http-latest",
        "link_name": "http"
    },
    "k9s": {
        "name": "K9s (Kubernetes UI)",
        "url": "https://github.com/derailed/k9s/releases/download/v0.32.7/k9s_Linux_amd64.tar.gz", 
        # Search 449 says v0.50 ? Let's use search result if reliable or recent stable.
        # "v0.50.18" seems very high jump from v0.32. 
        # Let's use a known recent version or the one from search ID 449 if I can trust it.
        # Check URL structure: k9s_Linux_amd64.tar.gz vs k9s_Linux_x86_64.tar.gz?
        # Search 449 mentions k9s_Linux_x86_64.tar.gz for v0.50.18
        "url": "https://github.com/derailed/k9s/releases/download/v0.32.5/k9s_Linux_amd64.tar.gz",
        "type": "tar.gz",
        "bin_path": "k9s",
        "link_name": "k9s"
    },
    
    # --- DevOps & Cloud ---
    "kubectl": {
        "name": "Kubectl",
        "url": "https://dl.k8s.io/release/v1.29.1/bin/linux/amd64/kubectl",
        "type": "appimage", # Treating single binary as appimage hack?
        # Installer 'appimage' logic is: move file, chmod +x. 
        # This works for raw binaries too!
        "bin_path": "kubectl",
        "link_name": "kubectl"
    },
    "terraform": {
        "name": "Terraform",
        "url": "https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip",
        "type": "zip", 
        # Need zip support.
    },
    
    # --- System ---
    "jq": {
        "name": "JQ (JSON Processor)",
        "url": "https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64",
        "type": "appimage", # Raw binary hack
        "bin_path": "jq-linux-amd64",
        "link_name": "jq"
    },
    "yq": {
        "name": "YQ (YAML Processor)",
        "url": "https://github.com/mikefarah/yq/releases/download/v4.40.5/yq_linux_amd64",
        "type": "appimage", # Raw binary hack
        "bin_path": "yq_linux_amd64",
        "link_name": "yq"
    },
    "ncdu": {
        "name": "NCDU (Disk Usage)",
        "url": "https://dev.yorhel.nl/download/ncdu-2.3-linux-x86_64.tar.gz",
        "type": "tar.gz",
        "bin_path": "ncdu",
        "link_name": "ncdu"
    },
    "bottom": {
        "name": "Bottom (Btop alternative)",
        "url": "https://github.com/ClementTsang/bottom/releases/download/0.9.6/bottom_x86_64-unknown-linux-gnu.tar.gz",
        "type": "tar.gz",
        "bin_path": "btm",
        "link_name": "btm"
    },

    # --- Browsers ---
    "firefox": {
        "name": "Firefox Developer Edition",
        "url": "https://download.mozilla.org/?product=firefox-devedition-latest-ssl&os=linux64&lang=en-US",
        "type": "tar.bz2",
        "bin_path": "firefox/firefox",
        "link_name": "firefox-dev"
    },
    # "brave": {
    #     "name": "Brave Browser",
    #     "url": "https://github.com/ivan-hc/Brave-appimage/releases/download/continuous/Brave-x86_64.AppImage",
    #     "type": "appimage",
    #     "bin_path": "Brave-x86_64.AppImage",
    #     "link_name": "brave"
    # },
    "librewolf": {
        "name": "LibreWolf",
        "url": "https://gitlab.com/api/v4/projects/24386000/packages/generic/librewolf/latest/LibreWolf.x86_64.AppImage",
        "type": "appimage",
        "bin_path": "LibreWolf.x86_64.AppImage",
        "link_name": "librewolf"
    },
}

