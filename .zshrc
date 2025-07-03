export PATH="/Users/cyberlives/Library/Python/3.8/bin:"$PATH
export OPENAI_API_KEY="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"
alias ll="ls -l"
eval "$(/opt/homebrew/bin/brew shellenv)"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

