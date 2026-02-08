# Post-Install Scripts - Quick Reference

## Basic Syntax

```json
{
    "app-name": {
        "name": "App Name",
        "url": "https://...",
        "type": "tar.gz",
        "bin_path": "...",
        "link_name": "app",
        "post_install": [
            "command1",
            "command2"
        ]
    }
}
```

## Placeholders

| Placeholder | Expands To | Example |
|-------------|------------|---------|
| `{bin}` | Full path to installed binary | `/goinfre/user/void/apps/vscode/VSCode-linux-x64/bin/code` |
| `{link}` | Full path to symlink in ~/bin | `/home/user/bin/code` |

## Common Patterns

### 1. Install Extensions/Plugins
```json
"post_install": [
    "{link} --install-extension python",
    "{link} --install-extension eslint"
]
```

### 2. Create Configuration
```json
"post_install": [
    "mkdir -p ~/.config/myapp",
    "echo '{\"theme\":\"dark\"}' > ~/.config/myapp/config.json"
]
```

### 3. Download Resources
```json
"post_install": [
    "curl -sL https://example.com/data.zip -o /tmp/data.zip",
    "unzip -q /tmp/data.zip -d ~/.local/share/myapp",
    "rm /tmp/data.zip"
]
```

### 4. Verify Installation
```json
"post_install": [
    "{link} --version",
    "echo 'Installation verified!'"
]
```

### 5. Multi-line Scripts (heredoc)
```json
"post_install": [
    "cat > ~/.config/app/config << 'EOF'\nline1\nline2\nEOF"
]
```

### 6. Conditional Commands
```json
"post_install": [
    "[ -f ~/.config/app/config ] || {link} --init-config"
]
```

## Best Practices

✅ **DO:**
- Use `{link}` for running the installed app
- Use non-interactive flags (`-y`, `--yes`, `--quiet`)
- Add confirmation messages with `echo`
- Keep scripts simple and focused
- Test commands manually first

❌ **DON'T:**
- Use commands requiring user input (will hang)
- Assume specific system packages are installed
- Use absolute paths (use `{bin}` or `{link}`)
- Make scripts too long (split into multiple if needed)
- Fail silently (scripts should output something)

## Timeout & Error Handling

- Each script has a **5-minute timeout**
- Script failures **don't stop installation**
- stdout/stderr are captured and displayed
- Exit codes are checked and reported

## Debugging

If a script fails:

1. **Check the output** - Error messages are displayed
2. **Test manually** - Run the command in your terminal
3. **Verify placeholders** - Ensure `{bin}` and `{link}` are correct
4. **Check permissions** - Some commands may need specific permissions
5. **Add verbose flags** - Use `-v` or `--verbose` in commands

## Examples by Use Case

### VSCode with Extensions
```json
"post_install": [
    "{link} --install-extension ms-python.python",
    "{link} --install-extension dbaeumer.vscode-eslint",
    "{link} --install-extension esbenp.prettier-vscode"
]
```

### Node.js Tool with Global Packages
```json
"post_install": [
    "{link} install -g typescript",
    "{link} install -g eslint",
    "echo 'Global packages installed'"
]
```

### App with Theme Setup
```json
"post_install": [
    "mkdir -p ~/.config/myapp/themes",
    "curl -sL https://example.com/dark-theme.json -o ~/.config/myapp/themes/dark.json",
    "{link} --set-theme dark"
]
```

### Database Tool with Sample Data
```json
"post_install": [
    "mkdir -p ~/.local/share/mydb",
    "{link} --init-db ~/.local/share/mydb/sample.db",
    "{link} --import-sample-data"
]
```
