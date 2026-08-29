---
layout: post
title: Managing Screen Timeout and Power Mode Settings on Linux
summary: >
  Bash script to configure screen blank timeout and power management profiles
  on Linux laptops, with interactive prompts for quick switching.
lang: en
date: 2026-06-04 19:35:00
categories:
- DevOps & Infrastructure
tags:
- OS
- Script
---

背景：需要控制笔记本屏幕时间和电源模式

<!--more-->
---
## `./power_settings.sh`
使用AI生成脚本`./power_settings.sh`，功能如下：

```shell

Interactive menu (run ./power_settings.sh with no args):

  ┌─────┬────────────────────────────────────────────────────┐
  │ Key │                       Action                       │
  ├─────┼────────────────────────────────────────────────────┤
  │ 1   │ Set screen off time (minutes)                      │
  ├─────┼────────────────────────────────────────────────────┤
  │ 2   │ Set lock delay after screen off                    │
  ├─────┼────────────────────────────────────────────────────┤
  │ 3   │ Choose power profile                               │
  ├─────┼────────────────────────────────────────────────────┤
  │ 4   │ Set brightness (0-100%)                            │
  ├─────┼────────────────────────────────────────────────────┤
  │ 5   │ Disable screen timeout entirely                    │
  ├─────┼────────────────────────────────────────────────────┤
  │ 6-8 │ Quick switch: power-saver / balanced / performance │
  └─────┴────────────────────────────────────────────────────┘

  CLI mode (non-interactive):
  ./power_settings.sh --screen-off 10      # screen off after 10 min
  ./power_settings.sh --screen-off 0       # never turn off
  ./power_settings.sh --power power-saver  # power saver mode
  ./power_settings.sh --power performance  # performance mode
  ./power_settings.sh --brightness 50      # 50% brightness
  ./power_settings.sh --status             # show all settings

  Dependencies:
  - gsettings (GNOME) — screen timeout & lock delay
  - powerprofilesctl or tuned-adm — power profiles
  - brightnessctl — brightness control (install with sudo apt install 
  brightnessctl)
  
  It auto-detects which tools are available on your system.

```

### code

```shell
#!/bin/bash
# Power & Screen Settings Manager
# Usage: ./power_settings.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Screen Timeout (GNOME / gsettings) ───

get_screen_timeout() {
    local idle=$(gsettings get org.gnome.desktop.session idle-delay 2>/dev/null)
    if [[ "$idle" == "uint32 0" || -z "$idle" ]]; then
        echo "Disabled (never)"
    else
        local seconds=$(echo "$idle" | grep -oP '\d+$')
        echo "$((seconds / 60)) min ($seconds s)"
    fi
}

set_screen_timeout() {
    local minutes=$1
    if [[ "$minutes" == "0" ]]; then
        gsettings set org.gnome.desktop.session idle-delay 0
        echo -e "${GREEN}Screen timeout: disabled (never turn off)${NC}"
    else
        local seconds=$((minutes * 60))
        gsettings set org.gnome.desktop.session idle-delay "uint32 $seconds"
        echo -e "${GREEN}Screen timeout: $minutes min${NC}"
    fi
}

# ─── Lock Screen Timeout ───

get_lock_timeout() {
    local lock=$(gsettings get org.gnome.desktop.screensaver lock-delay 2>/dev/null)
    if [[ "$lock" == "uint32 0" || -z "$lock" ]]; then
        echo "Immediate"
    else
        local seconds=$(echo "$lock" | grep -oP '\d+$')
        echo "$((seconds / 60)) min ($seconds s)"
    fi
}

set_lock_timeout() {
    local minutes=$1
    local seconds=$((minutes * 60))
    gsettings set org.gnome.desktop.screensaver lock-delay "uint32 $seconds"
    echo -e "${GREEN}Lock delay: $minutes min after screen off${NC}"
}

# ─── Power Profile (powerprofilesctl) ───

get_power_profile() {
    if command -v powerprofilesctl &>/dev/null; then
        powerprofilesctl get 2>/dev/null || echo "unknown"
    elif command -v tuned-adm &>/dev/null; then
        tuned-adm active 2>/dev/null | sed 's/.*: //' || echo "unknown"
    else
        echo "no power manager found"
    fi
}

list_power_profiles() {
    if command -v powerprofilesctl &>/dev/null; then
        echo -e "${CYAN}Available profiles:${NC}"
        powerprofilesctl list 2>/dev/null
    elif command -v tuned-adm &>/dev/null; then
        echo -e "${CYAN}Available profiles:${NC}"
        tuned-adm list 2>/dev/null
    else
        echo -e "${RED}No supported power manager found.${NC}"
        echo "Install power-profiles-daemon or tuned."
    fi
}

set_power_profile() {
    local profile=$1
    if command -v powerprofilesctl &>/dev/null; then
        powerprofilesctl set "$profile" 2>/dev/null
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}Power profile set to: $profile${NC}"
        else
            echo -e "${RED}Failed. Valid: balanced, power-saver, performance${NC}"
        fi
    elif command -v tuned-adm &>/dev/null; then
        tuned-adm profile "$profile" 2>/dev/null
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}Power profile set to: $profile${NC}"
        else
            echo -e "${RED}Failed. Run 'tuned-adm list' for valid profiles.${NC}"
        fi
    else
        echo -e "${RED}No power manager available.${NC}"
    fi
}

# ─── Brightness ───

get_brightness() {
    if command -v brightnessctl &>/dev/null; then
        brightnessctl -m | awk -F, '{print $4}'
    elif [[ -f /sys/class/backlight/*/brightness ]]; then
        local max=$(cat /sys/class/backlight/*/max_brightness 2>/dev/null)
        local cur=$(cat /sys/class/backlight/*/brightness 2>/dev/null)
        echo "$((cur * 100 / max))%"
    else
        echo "N/A"
    fi
}

set_brightness() {
    local pct=$1
    if command -v brightnessctl &>/dev/null; then
        brightnessctl set "${pct}%" 2>/dev/null
        echo -e "${GREEN}Brightness: ${pct}%${NC}"
    else
        echo -e "${RED}brightnessctl not found. Install it: sudo apt install brightnessctl${NC}"
    fi
}

# ─── Auto Suspend (systemd) ───

get_auto_suspend() {
    local on_battery=$(gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 2>/dev/null)
    local on_ac=$(gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 2>/dev/null)
    echo "  Battery: ${on_battery:-unknown}"
    echo "  AC:      ${on_ac:-unknown}"
}

# ─── Menu ───

show_status() {
    echo -e "\n${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Current Settings${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "  Screen timeout : $(get_screen_timeout)"
    echo -e "  Lock delay     : $(get_lock_timeout)"
    echo -e "  Power profile  : $(get_power_profile)"
    echo -e "  Brightness     : $(get_brightness)"
    echo -e "  Auto-suspend   :"
    get_auto_suspend
    echo -e "${CYAN}════════════════════════════════════════${NC}\n"
}

main_menu() {
    while true; do
        show_status
        echo -e "${YELLOW}Actions:${NC}"
        echo "  1) Set screen timeout"
        echo "  2) Set lock delay"
        echo "  3) Set power profile"
        echo "  4) Set brightness"
        echo "  5) Disable screen timeout (never off)"
        echo "  6) Quick: power-saver mode"
        echo "  7) Quick: balanced mode"
        echo "  8) Quick: performance mode"
        echo "  q) Quit"
        echo ""
        read -p "Choose [1-8, q]: " choice

        case $choice in
            1)
                read -p "Screen off after (minutes, 0=never): " mins
                set_screen_timeout "$mins"
                ;;
            2)
                read -p "Lock delay (minutes after screen off): " mins
                set_lock_timeout "$mins"
                ;;
            3)
                list_power_profiles
                read -p "Profile name: " profile
                set_power_profile "$profile"
                ;;
            4)
                read -p "Brightness (0-100): " pct
                set_brightness "$pct"
                ;;
            5)
                set_screen_timeout 0
                ;;
            6)
                set_power_profile "power-saver"
                ;;
            7)
                set_power_profile "balanced"
                ;;
            8)
                set_power_profile "performance"
                ;;
            q|Q) exit 0 ;;
            *) echo -e "${RED}Invalid option${NC}" ;;
        esac
        echo ""
    done
}

# ─── CLI mode (non-interactive) ───

if [[ "$1" == "--screen-off" && -n "$2" ]]; then
    set_screen_timeout "$2"
elif [[ "$1" == "--power" && -n "$2" ]]; then
    set_power_profile "$2"
elif [[ "$1" == "--brightness" && -n "$2" ]]; then
    set_brightness "$2"
elif [[ "$1" == "--status" ]]; then
    show_status
elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage:"
    echo "  $0                          Interactive menu"
    echo "  $0 --screen-off <minutes>   Set screen timeout (0=never)"
    echo "  $0 --power <profile>        Set power profile"
    echo "  $0 --brightness <0-100>     Set brightness"
    echo "  $0 --status                 Show current settings"
else
    main_menu
fi
```