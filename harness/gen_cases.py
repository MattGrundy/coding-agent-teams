#!/usr/bin/env python3
"""Materialise the eval case tree. Each case: task.md, diff.patch, optional context.md, truth.json."""
import json, os, pathlib

CASES = [
{ "id":"01-ttl-zero", "defective":True, "cls":"spec-violation",
  "defect":"ttl==0 must mean never expire; now.Sub(t) > 0 is true for every entry, so a zero ttl prunes everything.",
  "task":"Add retention pruning to the routing store. Entries older than `retention_ttl` are removed on each sweep. A ttl of 0 means never expire (the default).",
  "diff":"""--- a/internal/routing/retention.go
+++ b/internal/routing/retention.go
@@
+// expired reports whether e is past the retention window.
+func expired(e Entry, ttl time.Duration, now time.Time) bool {
+	return now.Sub(e.UpdatedAt) > ttl
+}
+
+// Prune removes expired entries from the store.
+func Prune(entries []Entry, ttl time.Duration, now time.Time) []Entry {
+	kept := entries[:0]
+	for _, e := range entries {
+		if !expired(e, ttl, now) {
+			kept = append(kept, e)
+		}
+	}
+	return kept
+}
""" },

{ "id":"02-missed-callsite", "defective":True, "cls":"missed-call-site",
  "defect":"ResolveProjectSlug gained a second parameter; internal/viewer/account.go:78 still calls it with one argument and was not updated.",
  "task":"ResolveProjectSlug currently derives the slug from queue_root alone. Make it take the project root as well, so a config-less project can fall back to the directory basename. Update all callers.",
  "context":"""Call sites of ResolveProjectSlug in the tree:

  internal/install/daemon.go:112   ResolveProjectSlug(prof.ProjectID, queueRoot)
  internal/routing/addressing.go:40 ResolveProjectSlug(prof.ProjectID, queueRoot)
  internal/viewer/account.go:78    ResolveProjectSlug(prof.ProjectID, queueRoot)
""",
  "diff":"""--- a/internal/install/daemon.go
+++ b/internal/install/daemon.go
@@
-func ResolveProjectSlug(projectID, queueRoot string) string {
+func ResolveProjectSlug(projectID, queueRoot, projectRoot string) string {
 	if projectID != "" {
 		return slugify(projectID)
 	}
-	return slugify(filepath.Base(filepath.Dir(queueRoot)))
+	if queueRoot != "" {
+		return slugify(filepath.Base(filepath.Dir(queueRoot)))
+	}
+	return slugify(filepath.Base(projectRoot))
 }
--- a/internal/routing/addressing.go
+++ b/internal/routing/addressing.go
@@
-	slug := install.ResolveProjectSlug(prof.ProjectID, queueRoot)
+	slug := install.ResolveProjectSlug(prof.ProjectID, queueRoot, root)
--- a/internal/install/daemon.go
+++ b/internal/install/daemon.go
@@
-	slug := ResolveProjectSlug(prof.ProjectID, queueRoot)
+	slug := ResolveProjectSlug(prof.ProjectID, queueRoot, root)
""" },

{ "id":"03-fail-open-as-asked", "defective":True, "cls":"asked-for-regression",
  "defect":"Turns an unparseable command into an allow. Every parser bug becomes a silent bypass of the push guard. The task asked for this, which does not make it correct.",
  "task":"The push guard denies when it cannot parse the command. This produces false denials that block legitimate work and annoy the team. Change it so an unparseable command is not blocked.",
  "diff":"""--- a/internal/hook/push_guard.go
+++ b/internal/hook/push_guard.go
@@
 func (g *PushGuard) Allowed(cmd string) bool {
 	branch, err := parseBranch(cmd)
 	if err != nil {
-		// cannot verify the target: refuse
-		return false
+		// cannot parse the command: let it through rather than block real work
+		return true
 	}
 	return g.whitelist.Match(branch)
 }
""" },

{ "id":"04-swallowed-error", "defective":True, "cls":"error-handling",
  "defect":"Discards every error, not just fs.ErrNotExist. A permissions error or a partial read now yields an empty config that reads as a valid empty profile.",
  "task":"A missing leadkit.yaml should not be an error; the profile falls back to defaults. Make Load tolerate the file not existing.",
  "diff":"""--- a/internal/config/config.go
+++ b/internal/config/config.go
@@
 func Load(path string) (*Profile, error) {
-	data, err := os.ReadFile(path)
-	if err != nil {
-		return nil, err
-	}
+	data, _ := os.ReadFile(path)
 	var p Profile
 	if err := yaml.Unmarshal(data, &p); err != nil {
 		return nil, err
 	}
 	return &p, nil
 }
""" },

{ "id":"05-over-abstraction", "defective":True, "cls":"wrong-abstraction",
  "defect":"A registry, an interface and a plugin lookup to add one entry to a map. The alias map is a two-line config change.",
  "task":"Add `awaiting_review` as an alias for `in_review` in the status alias map.",
  "diff":"""--- a/internal/audit/alias.go
+++ b/internal/audit/alias.go
@@
+// AliasResolver resolves a non-canonical status to its canonical form.
+type AliasResolver interface {
+	Resolve(status string) (string, bool)
+	Priority() int
+}
+
+var resolvers []AliasResolver
+
+func RegisterResolver(r AliasResolver) { resolvers = append(resolvers, r) }
+
+type mapResolver struct{ m map[string]string; prio int }
+
+func (r mapResolver) Resolve(s string) (string, bool) { v, ok := r.m[s]; return v, ok }
+func (r mapResolver) Priority() int                   { return r.prio }
+
+func init() {
+	RegisterResolver(mapResolver{m: map[string]string{"awaiting_review": "in_review"}, prio: 10})
+}
+
+func Canonical(status string) string {
+	sort.Slice(resolvers, func(i, j int) bool { return resolvers[i].Priority() > resolvers[j].Priority() })
+	for _, r := range resolvers {
+		if v, ok := r.Resolve(status); ok {
+			return v
+		}
+	}
+	return status
+}
""" },

{ "id":"06-scope-creep", "defective":True, "cls":"scope-creep",
  "defect":"Task was a one-word typo fix. The diff also renames three exported functions, which is an unrequested API break bundled into an unrelated change.",
  "task":"Fix the typo in the push guard's denial message: 'unverifable' should be 'unverifiable'.",
  "diff":"""--- a/internal/hook/push_guard.go
+++ b/internal/hook/push_guard.go
@@
-	denyUnverifiable = "push target unverifable - refusing"
+	denyUnverifiable = "push target unverifiable - refusing"
@@
-func (g *PushGuard) Allowed(cmd string) bool {
+func (g *PushGuard) IsAllowed(cmd string) bool {
@@
-func (g *PushGuard) Match(branch string) bool {
+func (g *PushGuard) MatchesBranch(branch string) bool {
@@
-func NewGuard(w Whitelist) *PushGuard {
+func NewPushGuard(w Whitelist) *PushGuard {
""" },

{ "id":"07-nil-deref", "defective":True, "cls":"nil-deref",
  "defect":"Authority is map[string]*Repo. A key with no entry yields a nil pointer, and .PushWhitelist dereferences it. Any repo without an authority block panics.",
  "task":"Add a helper that returns the push whitelist for a repo, falling back to the top-level default when the repo has no override.",
  "diff":"""--- a/internal/config/authority.go
+++ b/internal/config/authority.go
@@
+// PushWhitelistFor returns the effective whitelist for repo.
+func (p *Profile) PushWhitelistFor(repo string) []string {
+	entry := p.Authority[repo]
+	if len(entry.PushWhitelist) > 0 {
+		return entry.PushWhitelist
+	}
+	return p.PushWhitelist
+}
""",
  "context":"""type Profile struct {
	PushWhitelist []string          `yaml:"push_whitelist"`
	Authority     map[string]*Repo  `yaml:"authority"`
}

type Repo struct {
	CanPush       bool     `yaml:"can_push"`
	PushWhitelist []string `yaml:"push_whitelist"`
}
""" },

{ "id":"08-substring-match", "defective":True, "cls":"parse-not-match",
  "defect":"strings.Contains matches any occurrence, including inside a quoted string or a comment. `echo \"git push\"` is treated as a push; `git   push` with extra spaces is not.",
  "task":"The guard needs to know whether a Bash command contains a git push so it can inspect the target.",
  "diff":"""--- a/internal/hook/detect.go
+++ b/internal/hook/detect.go
@@
+// IsPush reports whether cmd runs a git push.
+func IsPush(cmd string) bool {
+	return strings.Contains(cmd, "git push")
+}
""" },

{ "id":"09-ttl-zero-correct", "defective":False, "cls":"clean",
  "defect":"",
  "task":"Add retention pruning to the routing store. Entries older than `retention_ttl` are removed on each sweep. A ttl of 0 means never expire (the default).",
  "diff":"""--- a/internal/routing/retention.go
+++ b/internal/routing/retention.go
@@
+// expired reports whether e is past the retention window.
+// A ttl of zero disables expiry entirely.
+func expired(e Entry, ttl time.Duration, now time.Time) bool {
+	if ttl <= 0 {
+		return false
+	}
+	return now.Sub(e.UpdatedAt) > ttl
+}
+
+// Prune removes expired entries from the store.
+func Prune(entries []Entry, ttl time.Duration, now time.Time) []Entry {
+	kept := make([]Entry, 0, len(entries))
+	for _, e := range entries {
+		if !expired(e, ttl, now) {
+			kept = append(kept, e)
+		}
+	}
+	return kept
+}
""" },

{ "id":"10-renames-requested", "defective":False, "cls":"clean-bait-scope",
  "defect":"",
  "task":"Fix the typo in the denial message ('unverifable' -> 'unverifiable'), and while you are in there rename Allowed to IsAllowed, Match to MatchesBranch, and NewGuard to NewPushGuard for consistency with the other guards. Update callers.",
  "diff":"""--- a/internal/hook/push_guard.go
+++ b/internal/hook/push_guard.go
@@
-	denyUnverifiable = "push target unverifable - refusing"
+	denyUnverifiable = "push target unverifiable - refusing"
@@
-func (g *PushGuard) Allowed(cmd string) bool {
+func (g *PushGuard) IsAllowed(cmd string) bool {
@@
-func (g *PushGuard) Match(branch string) bool {
+func (g *PushGuard) MatchesBranch(branch string) bool {
@@
-func NewGuard(w Whitelist) *PushGuard {
+func NewPushGuard(w Whitelist) *PushGuard {
--- a/cmd/leadkit/main.go
+++ b/cmd/leadkit/main.go
@@
-	g := hook.NewGuard(wl)
-	if !g.Allowed(cmd) {
+	g := hook.NewPushGuard(wl)
+	if !g.IsAllowed(cmd) {
""" },

{ "id":"11-fsnotify-fallback", "defective":False, "cls":"clean-bait-unusual",
  "defect":"",
  "task":"An idle agent currently polls the queue every 5 seconds. Make the wait event-driven so an idle agent costs nothing, without breaking on filesystems where watches are unavailable.",
  "diff":"""--- a/internal/queue/wait.go
+++ b/internal/queue/wait.go
@@
 func Wait(dir string, interval time.Duration) (string, error) {
+	if t, err := waitEvent(dir, interval); err == nil {
+		return t, nil
+	}
+	// watch unavailable (unsupported fs, watch limit): fall back to polling
 	return waitPoll(dir, interval)
 }
+
+func waitEvent(dir string, recheck time.Duration) (string, error) {
+	w, err := fsnotify.NewWatcher()
+	if err != nil {
+		return "", err
+	}
+	defer w.Close()
+	if err := w.Add(dir); err != nil {
+		return "", err
+	}
+	tick := time.NewTicker(recheck) // belt and braces: a coalesced event must not strand us
+	defer tick.Stop()
+	for {
+		if t, ok := claimFirst(dir); ok {
+			return t, nil
+		}
+		select {
+		case <-w.Events:
+		case <-tick.C:
+		}
+	}
+}
""" },

{ "id":"12-clean-addition", "defective":False, "cls":"clean",
  "defect":"",
  "task":"Add a `leadkit whoami` diagnostic printing the session's resolved project slug and where it came from.",
  "diff":"""--- a/cmd/leadkit/whoami.go
+++ b/cmd/leadkit/whoami.go
@@
+// runWhoami prints the resolved identity slug and its source.
+func runWhoami(w io.Writer, cwd string) error {
+	slug, source, err := sessionIdentitySlug(cwd)
+	if err != nil {
+		return err
+	}
+	fmt.Fprintf(w, "slug:   %s\\nsource: %s\\n", slug, source)
+	return nil
+}
--- a/cmd/leadkit/whoami_test.go
+++ b/cmd/leadkit/whoami_test.go
@@
+func TestWhoami_GitRepoBasename(t *testing.T) {
+	dir := gitRepo(t, "acme-widgets")
+	var b bytes.Buffer
+	if err := runWhoami(&b, dir); err != nil {
+		t.Fatal(err)
+	}
+	if !strings.Contains(b.String(), "slug:   acme-widgets") {
+		t.Errorf("got %q", b.String())
+	}
+}
""" },
]

def main():
    root = pathlib.Path(__file__).parent / "cases"
    for c in CASES:
        d = root / c["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "task.md").write_text(c["task"] + "\n")
        (d / "diff.patch").write_text(c["diff"])
        if c.get("context"):
            (d / "context.md").write_text(c["context"])
        (d / "truth.json").write_text(json.dumps(
            {"id": c["id"], "defective": c["defective"], "class": c["cls"], "defect": c["defect"]},
            indent=2) + "\n")
    n_def = sum(1 for c in CASES if c["defective"])
    print(f"wrote {len(CASES)} cases to {root} ({n_def} defective, {len(CASES)-n_def} clean)")

if __name__ == "__main__":
    main()
