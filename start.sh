#!/bin/bash

# Spinner fun
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

cat << 'EOF'


               __  __                  ____
               \ \/ /___  __  __      / __ \___  _________ _____ 
                \  / __ \/ / / /_____/ /_/ / _ \/ ___/ __ `/ __ \
                / / /_/ / /_/ /_____/ _, _/  __/ /__/ /_/ / /_/ /
               /_/\____/\__,_/     /_/ |_|\___/\___/\__,_/ .___/ 
                                                        /_/      
        _   ___       _    _           ___
       /_\ |_ _| __ _(_)__| |___ ___  / __|_  _ _ __  _ __  __ _ _ _ _  _ 
      / _ \ | |  \ V / / _` / -_) _ \ \__ \ || | '  \| '  \/ _` | '_| || |
     /_/ \_\___|  \_/|_\__,_\___\___/ |___/\_,_|_|_|_|_|_|_\__,_|_|  \_, |
                                                                     |__/ 


EOF


# Nome dello script Python
SCRIPT_PYTHON="idcanale.py"

# Esegui lo script Python
python3 $SCRIPT_PYTHON &
pid=$!
spinner $pid

# Attendi che lo script Python finisca
wait $pid

# Trova tutte le cartelle create dallo script Python
# Supponiamo che le cartelle siano create nella directory corrente
for dir in */; do
    # Controlla se il file esegui.sh esiste nella cartella
    if [ -f "$dir/esegui.sh" ]; then
        # Entra nella cartella
        cd "$dir"
        
        # Esegui il file esegui.sh
        ./esegui.sh &
        pid=$!
        spinner $pid
        
        # Torna alla directory precedente
        cd ..
    fi
done

# Pausa di 60 secondi con barra che gira
sleep_with_spinner() {
    local duration=$1
    local end=$((SECONDS+duration))
    while [ $SECONDS -lt $end ]; do
        printf " [ ]  "
        sleep 0.1
        printf "\b\b\b\b\b\b"
        printf " [|]  "
        sleep 0.1
        printf "\b\b\b\b\b\b"
        printf " [/]  "
        sleep 0.1
        printf "\b\b\b\b\b\b"
        printf " [-]  "
        sleep 0.1
        printf "\b\b\b\b\b\b"
        printf " [\\]  "
        sleep 0.1
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Pausa di 15 secondi con barra che gira
sleep_with_spinner 15

python3 send_email.py
