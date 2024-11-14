export PATH=${PATH}:/usr/local/mysql/bin/ 
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/Users/seanroades/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/Users/seanroades/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/Users/seanroades/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/Users/seanroades/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

export PATH="/opt/homebrew/opt/icu4c/bin:$PATH"

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/seanroades/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/seanroades/Downloads/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/seanroades/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/seanroades/Downloads/google-cloud-sdk/completion.zsh.inc'; fi

# Created by `pipx` on 2022-04-26 23:47:46
export PATH="$PATH:/Users/seanroades/.local/bin"

export HOMEBREW_PREFIX="/usr/local"
export HOMEBREW_CELLAR="/usr/local/Cellar"

# opam configuration
[[ ! -r /Users/seanroades/.opam/opam-init/init.zsh ]] || source /Users/seanroades/.opam/opam-init/init.zsh  > /dev/null 2> /dev/nulleval "$(rbenv init - zsh)"
eval "$(~/.rbenv/bin/rbenv init - zsh)"
export PATH="PATH:$HOME/development/flutter/bin"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
