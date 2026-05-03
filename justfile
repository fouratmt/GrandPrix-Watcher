set shell := ["zsh", "-cu"]

config := "config.toml"

default:
    @just --list

# Validate Python syntax.
lint:
    python3 -B -m py_compile crawler.py tests.py

# Run lightweight local tests.
test:
    python3 -B tests.py

# Run one normal check using config.toml.
check config=config:
    python3 -B crawler.py --config {{config}}

# Keep polling using config.toml.
watch config=config:
    python3 -B crawler.py --config {{config}} --watch

# Run one check and notify/open matches even if they were already seen.
force config=config:
    python3 -B crawler.py --config {{config}} --include-seen

# Run one check for an event and Grand Prix location.
for event place config=config:
    python3 -B crawler.py --config {{quote(config)}} --grand-prix {{quote(place)}} --event {{quote(event)}}

# Keep polling for an event and Grand Prix location.
watch-for event place config=config:
    python3 -B crawler.py --config {{quote(config)}} --grand-prix {{quote(place)}} --event {{quote(event)}} --watch

# Run one event/location check and notify/open even if the match was already seen.
force-for event place config=config:
    python3 -B crawler.py --config {{quote(config)}} --grand-prix {{quote(place)}} --event {{quote(event)}} --include-seen

# Send a local Apple Notification Center test notification.
notify-test:
    osascript -e 'display notification "Crawler notification test" with title "New video match" subtitle "Apple Notification Center"'
