# Controls That Aren't Controls

*Part 3 of a series on running a team of coding agents. Each part stands alone.*

## Takeaways

- **A client-side guard is a belief with good ergonomics.** It inspects a proposed action
  and returns a verdict, which works only because the runtime asks permission first.
  Nothing physically prevents the action, so an unconfigured machine has no guards at all.
- **Put the enforceable control where the client cannot reach it, first.** For code that
  means the forge: protected branches, required review, no direct push. It is an afternoon
  of work and it is the only part that holds when someone else's machine is wrong.
- **Assume every client-side guard is off until something proved otherwise today.** Probe
  them; do not read the config. An untested control is worse than a missing one, because
  it consumes the attention you would have spent worrying about the gap.
- **Installation is part of the control.** The failure that prompted this was not a clever
  bypass — it was tooling running somewhere the rules had never been installed, and no
  enforcement design survives its own absence.
- **Make the definitions reconstructible.** A control defined by something that was never
  checked out is not a control anyone else can inherit.

An agent on a machine that was not mine pushed to a protected branch. It was running
the same tooling I was, nominally under the same rules, and it went straight past every
guard I had built to prevent exactly that.

The guards were not broken. They were not there. They lived in a settings file on my
machine, and that machine was not involved.

I had spent months building policy enforcement for agents and had arrived at an
architecture I was fairly pleased with. This piece is about what that incident revealed,
which is that most of what I had built was not a control at all. It was a belief with
good ergonomics.

## The thing I got wrong

My plan, before this happened, was to make the boundary physical. Filesystem scope
enforced by the operating system instead of a path check. Network egress restricted to
declared endpoints. Each agent in its own worktree so ownership was structural. Real
confinement underneath the advisory layer, with the guards demoted to good error
messages on top of a boundary that actually held.

None of that would have helped, and working out why took longer than it should have.

Every guard I had built runs inside the client. It is a hook that inspects a proposed
tool call and returns allow or deny, and it works because the runtime asks permission
before acting. Operating-system confinement is also configured in the client. So is the
worktree layout. So is the egress policy.

The thing that got bypassed *was* the client. Hardening the client against a failure of
the client is not a security measure, it is a stronger belief.

There is exactly one layer in that whole picture that a misconfigured or unwilling
client cannot route around, and it is not on the client at all. The git host can refuse
the push. Protected branches, required reviews, required checks, enforced server-side,
identically for every actor regardless of what their machine believes. That is the
control. Everything else is defence in depth on top of it.

## What the layers are actually worth

Ordered by how hard each is to bypass, which turns out to be close to the inverse of
how much effort each takes to build.

**Forge-side branch protection** is the only bypass-proof layer, and it is an API call.
Required pull request, required checks, no direct push to protected branches, no force
push. An agent on an unconfigured machine hits the same wall as everyone else, because
the wall is not on the machine. Cheapest thing in the list and the only one that would
have stopped the incident.

Alongside it, a health check that goes and asks the host whether protection is actually
enabled, and warns when it is not: *your protected branches rely only on client-side
guards, and a client that bypasses the hook can still push.* That sentence is the whole
lesson, and an adopter should be told it by their tooling instead of learning it the way
I did.

**Least-privilege tool sets** come next, and they are nearly as cheap. An agent that has
no push tool cannot push. A reviewer needs to read files and run tests; it does not need
to write them, and it certainly does not need to move branches. This is enforced by the
runtime that grants the tools, one level out from the agent's own judgement, and it
would also have stopped the incident on a different axis: the agent that pushed had no
business holding a push capability in the first place.

**Containers with curated mounts** are where real isolation starts, and where the effort
climbs. Each agent gets its own project tree and the shared coordination store it needs
to hand work to other agents, and nothing else. It cannot read another project because
another project is not mounted. Cross-project work survives because the coordination
surface is mounted deliberately instead of inherited by sitting on the same filesystem
as everything else.

**Fail-closed client guards**, which is what I had, come last. They are genuinely
useful. They are also the layer a broken client silently removes, so treating them as
the boundary is the mistake I made.

## The same failure, quieter

The incident is the loud version. There is a quiet version that had been happening on my
own machine and that I had no way of noticing.

Hooks are wired through a settings file, and mine named them by command. The hook
runtime executes under a minimal shell environment where the install directory is not on
the path, so the command was not found. That failure is non-blocking by design, so the
tool call proceeded. The guard reported as configured, appeared in the settings file,
and enforced nothing.

For an unknown period, I had a system that looked governed and was not. There is no
symptom. The settings are right, no errors appear, and the agent is not blocked, which
is what you would expect if everything were working.

Two fixes. Wire the absolute path of the binary, never a bare name resolved against
whatever path the hook runtime happens to have. And make the health check *probe* each
guard by invoking it, instead of confirming that a line exists in a configuration file.

The general form: a control you have not verified is a belief, and the more reliable it
looks the longer you will hold the belief.

## Verification as a feature

Which is why the diagnostic command ended up carrying about thirty checks, and why the
interesting ones are not about configuration.

Checking that a binary exists and a config parses is table stakes. The checks that earn
their place are the ones that ask whether the operating model is still holding: lanes
that have not moved, agents that claimed work and went away, daemons that are installed
but dead, policy keys that silently shadow each other, a queue being mutated by
something other than the tool that owns it, a milestone anchor that has drifted from
what the tasks say.

That is a tool reporting on whether its own rules are being followed, rather than on
whether it was installed correctly. The distinction matters because the second question
has a reassuring answer almost always, and the first one does not.

It is also the closest thing I have to evidence that any of this works. Not a benchmark,
but a continuously running check that the controls are live, which is a different and
more useful claim than an assertion that they exist.

## Installation is part of the control

Two smaller things sit underneath, and both come from the same realisation: a control
that cannot be installed correctly on a second machine is a control that exists once.

The first is a scar. The install and audit commands can modify real state, so they take
an `--apply` flag. A boolean flag in Go parses as true when passed with no value, which
means a stray `--apply` at the end of a command line is indistinguishable from a
deliberate one. During dogfooding, my own tool ran a live apply against my own task
store because of exactly that.

The fix was a second, independent flag. `--apply` alone now computes the plan, prints
it, and refuses with a non-zero exit. Writing anything requires `--apply --confirm`
together, typed on purpose. It is a small thing, but it is the right shape: the
protection is not a warning in the output, it is a state the command cannot reach by
accident.

The second is reconstruction. The definitions that make the operating model work, the
agent briefs, the protocol, the standard operating procedure, normally live outside the
repository in a home directory. That is precisely why they were absent on the machine
where the incident happened. So the tool versions them into the repository itself and
can rebuild them on a fresh machine from what is committed.

That is the direct answer to the incident, and it is also the least glamorous item here.
The machine that bypassed the guards did not disable them. It simply never had them,
because the thing that defines them was not a thing you could check out.

## What I would tell someone starting

Put the enforceable control at the layer the client cannot reach, and do it before
building anything clever on the client side. For code, that means the forge. It is an
afternoon of work and it is the only part of this that holds when someone's machine is
wrong.

Then assume every client-side guard is off until something has proved otherwise today.
Probe them; do not read the config. An untested control is worse than a missing one,
because it consumes the attention you would otherwise have spent worrying about the gap.

And make the definitions reconstructible. The failure that started all this was not a
clever bypass. It was an agent running somewhere the rules had never been installed, and
no amount of enforcement design survives its own absence.
