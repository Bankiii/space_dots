source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

if status is-interactive
    python3 ~/.local/bin/dotbanner.py --style star --fit --thick 2
end

# prompt pure en ambar
set --universal pure_color_primary ffaf00
set --universal pure_color_current_directory ffaf00
set --universal pure_color_git_branch af8700
set --universal pure_color_prompt_on_success ffaf00
set --universal pure_color_git_dirty af8700
set --universal pure_color_git_unpushed_commits af8700
set --universal pure_color_git_unpulled_commits af8700
set --universal pure_color_command_duration af8700
set --universal pure_color_info ffaf00
