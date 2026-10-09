ResolveProjectSlug currently derives the slug from queue_root alone. Make it take the project root as well, so a config-less project can fall back to the directory basename. Update all callers.
