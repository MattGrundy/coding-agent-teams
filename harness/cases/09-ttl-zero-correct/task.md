Add retention pruning to the routing store. Entries older than `retention_ttl` are removed on each sweep. A ttl of 0 means never expire (the default).
