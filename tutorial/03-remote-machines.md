# Lesson 3. A small lab network of GPU machines: Tailscale and SSH

Lessons 5 to 8 run on a laptop. Fine-tuning and in silico perturbation only
become practical on a Linux machine with a GPU, and such machines sit in
another room or another building. A common lab setup, and the one this
tutorial is built around, is a handful of GPU machines on a private network
that you reach from your laptop with **Tailscale** and **SSH**. You log in,
start a job inside a persistent terminal, close your laptop, and collect the
results later. If you only have a laptop, skip to [lesson 4](04-install.md)
and come back later.

This lesson describes your **own** network. Names below are placeholders:
`laptop` is your computer, `gpu-box-1` is a GPU machine you can administer or
have been given, and `yourname` is your user name on it. Substitute your own.
Your administrator will tell you how to get an account; never share a private
key.

## Three tools in two sentences each

**Tailscale** puts your machines on one private network (a "tailnet"), however
different their physical networks are. Each machine gets a stable name and a
private address, so `gpu-box-1` works from a cafe as well as from the lab.

**SSH** ("secure shell") opens a terminal on another computer from your own.
Your commands run on that machine until you type `exit`.

**tmux** keeps a terminal session alive on the remote machine. If your laptop
sleeps or the network drops, the session and anything running in it carry on.

## Step 1. Put both machines on your tailnet

Do this once per machine. Create a free Tailscale account at
[tailscale.com](https://tailscale.com/), then install the client following
the instructions for your system at
[tailscale.com/download](https://tailscale.com/download). On a Linux GPU box
that is a short script and needs administrator rights, so ask whoever manages
the machine. On a laptop it is an app. Then log in:

```bash
sudo tailscale up      # on the Linux GPU box (the laptop app has a Log in button)
```

A link appears; open it in a browser and sign in with the same account (or the
same organisation) on every machine. Check who is on the network:

```bash
tailscale status
```

```text
100.x.y.z   laptop        yourname@   macOS   -
100.x.y.z   gpu-box-1     yourname@   linux   -
```

The first column is the machine's private address (it starts with `100.`),
the second its name. With **MagicDNS** switched on (the default on new
tailnets) you can use the name instead of the address, and the full form is
`gpu-box-1.tailnet-name.ts.net`. Test the connection from the laptop:

```bash
tailscale ping gpu-box-1
```

## Step 2. Log in with SSH over the tailnet

```bash
ssh yourname@gpu-box-1
```

The first time you reach a machine, SSH asks whether you trust it:

```text
The authenticity of host '...' can't be established.
ED25519 key fingerprint is SHA256:....
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Compare the `SHA256:...` fingerprint with the one the machine's
administrator gives you, and type `yes` only if they match. Then the prompt
changes to `yourname@gpu-box-1:~$`. Run `hostname`, then `exit` to come back.

If you do not have a key yet, create one on the laptop with
`ssh-keygen -t ed25519`, and give the administrator the **public** file
(`~/.ssh/id_ed25519.pub`, the one ending in `.pub`). The private file stays on
your laptop.

To type less, describe the machine once in `~/.ssh/config` on the laptop:

```text
Host gpu-box-1
    HostName gpu-box-1
    User yourname
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 15
    ServerAliveCountMax 3
```

After that, `ssh gpu-box-1` is enough. The two `ServerAlive` lines keep an
idle connection from dropping.

## Step 3. Look before you start

A shared machine may already be busy, and a job that runs out of memory can
stop other people's work too. Check three things first. The helper in
`quickstart/remote_run.sh` does it in one command:

```bash
cd quickstart
./remote_run.sh gpu-box-1 check
```

It prints the free disk space, the memory, the GPU and whether `git`, `curl`,
`tmux` and `uv` are installed. Read it as follows:

- Disk: plan for 10 GB for the quickstart and much more for real projects.
- Memory: `available` is what a new job can use. Leave at least 15 GB
  available on a shared machine; if a job would take it below that, wait or
  use another machine.
- GPU: if another person's job holds most of the GPU memory, ask before you
  start. A machine without an NVIDIA GPU is fine for the quickstart, which
  falls back to the CPU.

## Step 4. Run the quickstart on the GPU machine

This is the main route. The job runs on `gpu-box-1` inside tmux, so closing
your laptop does not stop it:

```bash
./remote_run.sh gpu-box-1 start            # clones the repository there, runs setup and the quickstart
./remote_run.sh gpu-box-1 status           # RUNNING, plus the last lines of the log
./remote_run.sh gpu-box-1 fetch            # when it is done: copies results/ to ./results-gpu-box-1/
```

Arguments after `start` go to the script, for example
`./remote_run.sh gpu-box-1 start --cells 0` for all cells. The remote machine
needs `git`, `curl`, `tmux` and [`uv`](https://docs.astral.sh/uv/) and access
to GitHub and Hugging Face; `check` tells you what is missing.

The same steps by hand, if you prefer to see them:

```bash
ssh gpu-box-1
git clone https://github.com/Kays3/geneformer-petadimension-starter.git
tmux new -s gf                              # a named session
cd geneformer-petadimension-starter/quickstart
./setup.sh && uv run python run_quickstart.py
```

Press `Ctrl` + `B`, release, then `D` to leave the session running. Later:
`ssh gpu-box-1`, then `tmux attach -t gf`. `tmux ls` lists sessions; type
`exit` inside one to end it.

**Fallback.** No GPU machine yet? Run the same two commands on the laptop,
as in the main README. The result is the same; only the time differs.

## Step 5. Copy files to and from the laptop

`fetch` does this for the quickstart. For other files, run these on the
laptop, not on the remote machine:

```bash
scp gpu-box-1:geneformer-starter/quickstart/results/umap_pbmc3k.png .
scp my_script.py gpu-box-1:
```

Keep large data on the GPU machine and copy only small results to the laptop.
Tailscale also has `tailscale file cp` for sending a file between your own
machines.

## You should now see

`tailscale status` lists your machines, `ssh gpu-box-1` gives you a prompt on
the GPU machine, and `./remote_run.sh gpu-box-1 check` prints a table with a
GPU line.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `Could not resolve hostname gpu-box-1` | MagicDNS is off, the name is wrong, or the laptop is not logged in to Tailscale | Run `tailscale status`; log in on the laptop; use the address from the first column, or turn MagicDNS on in the Tailscale admin console |
| `Connection timed out` | The machine is off or asleep, or its Tailscale client is stopped | Check `tailscale status` for the machine; ask whoever runs it to start it |
| `Permission denied (publickey)` | The machine does not accept your key | Ask the administrator to add your public key (the `.pub` file). Never send the private key |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` | The machine was reinstalled, or something is wrong | Confirm with the administrator first. Only then run `ssh-keygen -R gpu-box-1` and connect again |
| `tmux is not installed` or `MISSING` in `check` | A tool is absent on the GPU machine | Ask the administrator to install it, or use the user-space installers: `uv` has a one-line installer that needs no administrator rights |
| `tailscale ping` works but `ssh` hangs | The machine's SSH server is not running, or a firewall blocks port 22 | Ask the administrator; as a workaround Tailscale can serve SSH itself (`sudo tailscale up --ssh` on the GPU box) |

Previous: [2. Geneformer in plain words](02-geneformer-in-plain-words.md) ·
Next: [4. Install Python and Geneformer](04-install.md)
