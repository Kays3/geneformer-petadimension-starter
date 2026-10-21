# Lesson 1. The terminal

A **terminal** is a window where you type commands instead of clicking. Every
later lesson uses it. This lesson teaches the five commands you need.

> **Plan ahead: ask for access now.** If you will use the lab's GPU machines,
> ask your computer administrator today for a user account and a Tailscale
> invitation. It takes a person to grant them and may take days. The checklist
> and a message to copy are in
> [lesson 3, step 0](03-remote-machines.md#step-0-ask-your-labs-computer-administrator-for-access).

## Open a terminal

- **macOS:** press `Command` + `Space`, type `Terminal`, press `Return`.
- **Linux:** press `Ctrl` + `Alt` + `T`.
- **Windows:** install the Windows Subsystem for Linux (WSL) by following
  [Microsoft's guide](https://learn.microsoft.com/windows/wsl/install) (it
  needs a restart), then open the **Ubuntu** app. Everything after that works
  as on Linux.

A window opens with a line ending in `%` or `$`. That line is the **prompt**:
the terminal is waiting for you.

## Five commands

`pwd` ("print working directory") shows which folder you are in:

```bash
pwd
```

You should see your home folder, for example:

```text
/Users/yourname
```

`mkdir` ("make directory") creates a folder. `cd` ("change directory") moves
into it. Create the folder used for the rest of the tutorial:

```bash
mkdir -p ~/geneformer-tutorial
cd ~/geneformer-tutorial
pwd
```

You should see:

```text
/Users/yourname/geneformer-tutorial
```

`~` is shorthand for your home folder. `-p` tells `mkdir` not to complain if
the folder already exists.

`ls` ("list") shows what is in the current folder. The folder is new, so it
prints nothing yet:

```bash
ls
```

`cat` prints a file. Create a small file and read it back:

```bash
echo "my first file" > hello.txt
cat hello.txt
```

You should see:

```text
my first file
```

## Editing a file

Later lessons ask you to save a short Python script. The simplest editor
inside the terminal is `nano`. To create or open a file called `hello.py`:

```bash
nano hello.py
```

Paste the text, then press `Ctrl` + `O` and `Return` to save, and `Ctrl` + `X`
to leave. If you prefer a normal window, use a code editor such as Visual
Studio Code. Avoid TextEdit and word processors: they turn straight quotes
into curly ones, which breaks Python. Save the file inside
`~/geneformer-tutorial`.

## Two habits that save time

- Press `Tab` to complete a file or folder name.
- Press the up arrow to bring back the previous command.

## You should now see

A terminal open in `~/geneformer-tutorial`, containing `hello.txt`. Each
later lesson starts with `cd ~/geneformer-tutorial`.

## Troubleshooting

| You see | What it means | What to do |
| --- | --- | --- |
| `command not found` | A typo, or the program is not installed | Check the spelling; install steps come in lesson 4 |
| `No such file or directory` | You are in a different folder from the one you think | Run `pwd`, then `cd ~/geneformer-tutorial` |
| A `>`, `quote>` or `dquote>` prompt that will not go away | A quote mark was left open | Press `Ctrl` + `C` and paste the command again |

Previous: [0. Start here](00-start-here.md) ·
Next: [2. Geneformer in plain words](02-geneformer-in-plain-words.md)
