# Racket
export PATH="/Applications/Racket/bin:$PATH"

# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# pipx
export PATH="$PATH:/Users/xiaoyangliu/.local/bin"

# >>> conda initialize >>>
# This is the original conda initialization, safe to leave
# It will set up conda functions but 不自动激活 base
if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    . "/opt/anaconda3/etc/profile.d/conda.sh"
fi
# <<< conda initialize <<<

# Other PATH settings
export PATH="$PATH:$HOME/flutter/bin"
export PATH=$HOME/.gem/bin:$PATH
export PATH="/opt/homebrew/lib/ruby/gems/3.4.0/bin:$PATH"

# Aliases
alias cm='open -a "Google Chrome"'
alias os='cd ~/Desktop/academic/coop1/os'

# Optional function to manually activate conda base
conda_on() {
    conda activate base
}

