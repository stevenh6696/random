# From https://github.com/chubin/wttr.in

# Auto refresh the data-rich format
alias getWeather="watch -c -n 10 \"curl --silent https://v2.wttr.in/Atlanta\?m\""

# Get the weather in my format
alias getWeather2="curl \"https://wttr.in/Atlanta?format=\"%l:%20%t%20%c%20%C%20%m\"&m\""
