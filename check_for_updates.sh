
if [[ "$(tr -d '\0' < $@)" != *"Already up to date."* ]]; then 
    echo update needed 
fi