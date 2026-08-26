# Dev Container Usage

## 1) Open In Container

1. Open this folder in VS Code.
2. Run command: `Dev Containers: Reopen in Container`.
3. Wait for build to finish.

## 2) Run The App In The Container

From the VS Code terminal inside the container:

```bash
python3 sec_flashcards.py
```

## 3) Linux GUI Forwarding (Tkinter)

This app opens a Tkinter window, so container GUI access is required.

On Linux hosts, start VS Code with X11 access enabled for local containers:

```bash
xhost +local:docker
```

If needed, allow your local user instead:

```bash
xhost +SI:localuser:$USER
```

After you are done, you can revoke broad docker access:

```bash
xhost -local:docker
```