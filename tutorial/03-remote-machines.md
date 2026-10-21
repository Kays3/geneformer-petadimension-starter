# Lesson 3. Working on a remote Linux machine

Lessons 5 to 8 run on a laptop. They run faster, and fine-tuning and in
silico perturbation only become practical, on a Linux machine with a GPU, and
such machines are usually in another room or another building. This lesson
shows how to log in to one, keep a job running after you disconnect, and
check its disk, memory and GPU before you start. If you only have a laptop,
skip to [lesson 4](04-install.md) and come back later.

Your institution or lab will tell you the machine's address, your user name,
and how to get a key or account. This tutorial does not cover that, and you
should never share a private key. Below, `yourname` is your user name and
`gpu-box` is a placeholder for the machine you were given.

## Two tools in two sentences each

**SSH** ("secure shell") lets you open a terminal on another computer from
your own. You type `ssh` and the machine's name, and from then on your
commands run on that machine until you type `exit`.

**tmux** keeps a terminal session alive on the remote machine. If your laptop
sleeps or the network drops, the session, and anything running in it, carries
on, and you can pick it up again later.

## Step 1. Describe the machine once

SSH can remember a machine under a short name. Open (or create) the file
`~/.ssh/config` on your laptop:

```bash
mkdir -p ~/.ssh
nano ~/.ssh/config
```

Add a block like this, replacing the three values with the ones you were
given, then save (`Ctrl` + `O`, `Return`, `Ctrl` + `X`):

```text
Host gpu-box
    HostName gpu-box.example.org
    User yourname
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 15
    ServerAliveCountMax 3
```

`HostName` is the machine's address; `User` is your account on it;
`IdentityFile` is the private key file on your laptop (the file that does not
end in `.pub`); the two `ServerAlive` lines keep an idle connection from
dropping. If your institution requires a VPN or a jump host, it will give you
the extra lines.

## Step 2. Log in for the first time

```bash
ssh gpu-box
```

The first time you reach a machine, SSH asks whether you trust it:

```text
The authenticity of host '...' can't be established.
ED25519 key fingerprint is SHA256:....
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

SSH wants you to confirm that you have reached the real machine. Compare the
`SHA256:...` fingerprint with the one your administrator published, and type
`yes` only if they match. Then the prompt changes:

```text
yourname@gpu-box:~$
```

Your commands now run on the remote machine. Check, then leave:

```bash
hostname
exit
```

`hostname` prints the machine's name. After `exit` you are back on your
laptop.

## Step 3. Look before you start

Log in again and check three things before any large job. A shared machine
may already be busy, and a job that runs out of memory can stop other
people's work too.

```bash
ssh gpu-box
df -h ~
free -g
nvidia-smi
```

- `df -h ~` shows free disk space in your home folder. Plan for 5 to 15 GB
  for this tutorial, and much more for real projects.
- `free -g` shows memory in gigabytes. The column `available` is what a new
  job can use. Leave at least 15 GB available on a shared machine; if a job
  would take it below that, wait or use another machine.
- `nvidia-smi` shows the GPU and the programs using it. If another person's
  job holds most of the GPU memory, ask before you start. The command is
  missing on a machine without an NVIDIA GPU, which is fine for lessons 5
  to 8.

## Step 4. Keep a job running after you disconnect

On the remote machine, start a named tmux session:

```bash
tmux new -s gf
```

Start your long command inside it. To leave it running, press `Ctrl` + `B`,
release, then press `D`. Later, reconnect and pick it up:

```bash
ssh gpu-box
tmux attach -t gf
```

`tmux ls` lists your sessions. Type `exit` inside a session to end it when the
job is finished.

## Step 5. Copy files to and from your laptop

Run these on your laptop, not on the remote machine. The first copies a
result file down to the current folder; the second sends a file up:

```bash
scp gpu-box:geneformer-tutorial/pbmc/results/umap_pbmc3k_cls.png .
scp my_script.py gpu-box:geneformer-tutorial/
```

Keep large data on the machine (or on shared storage that the machine mounts)
and copy only small results to your laptop.

## You should now see

`ssh gpu-box` gives you a prompt on the remote machine, and `df -h ~`,
`free -g` and (on a GPU machine) `nvidia-smi` print their tables.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `Connection timed out` or `Could not resolve hostname` | The address is wrong, the machine is offline, or a required VPN is off | Check the `HostName` line in `~/.ssh/config`; connect to the VPN if your institution uses one |
| `Permission denied (publickey)` | The machine does not accept your key | Ask your administrator to add your public key (the `.pub` file). Never send the private key |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` | The machine was reinstalled, or something is wrong | Confirm with your administrator before continuing. Only then remove the old entry with `ssh-keygen -R gpu-box.example.org` and connect again |

Previous: [2. Geneformer in plain words](02-geneformer-in-plain-words.md) ·
Next: [4. Install Python and Geneformer](04-install.md)
