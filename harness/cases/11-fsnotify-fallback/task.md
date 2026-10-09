An idle agent currently polls the queue every 5 seconds. Make the wait event-driven so an idle agent costs nothing, without breaking on filesystems where watches are unavailable.
