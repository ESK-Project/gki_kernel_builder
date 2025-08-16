# Kernel Builder Configuration Guide

This short guide explains **how configuration files are structured** in the Kernel Builder.

---

## 1. Simplified Git Link

> **Used by:** `manifest.py`, `config.py`

### 1.1 Format

```plaintext
<host>:<user>/<repo>
```

| Part | Description                   | Example              |
| ---- | ----------------------------- | -------------------- |
| host | Git hosting domain            | `github.com`         |
| user | Organisation or username      | `bachnxuan`          |
| repo | Repository **without** `.git` | `gki_kernel_builder` |

**Example**

```plaintext
github.com:bachnxuan/gki_kernel_builder
```

### 1.2 Rules

* *Do **not** append* `.git`.
* Use **HTTPS** format only, SSH URLs are **not** accepted (`git@…` will break the parser).

---

## 2 · Manifest

Each source is represented by a dict below:

```python
source: Source = {
    "url":    "<git link>",     # simplified link (see §1)
    "branch": "<branch/tag>",
    "to":     str(<Path object>), # absolute or relative path
}
```

### 2.1 Example

```python
KERNEL: Source = {
    "url":    "github.com:bachnxuan/android12-5.10-lts",
    "branch": "esk/main",
    "to":     str(WORKSPACE),
}
```

### 2.2 After adding a source

- Append the variable to the `SOURCES` list in `manifest.py` so it is checked‑out automatically.

---

## 3 · Variants Configuration (`variants.json`)

> [!NOTE]
> `variants.json` tells the builder which Kconfig tweaks to apply for a given environment.\
Flow: CLI → env vars → scan variants.json → pick first entry whose env keys all match → feed that entry's config dict to `config` to enable/disable items in .config.

```json
{
  "variant": "<string>",          // Human‑readable variant name
  "env": {
    "KEY": "value"                // Environment variables expected for variant
  },
  "config": {
    "CONFIG_FOO": true             // Kernel .config overrides (bool)
  }
}
```

### 3.1 Complete example

```json
{
  "variant": "NEXT-SUSFS",
  "env": {
    "KSU": "NEXT",
    "SUSFS": true
  },
  "config": {
    "CONFIG_KSU": true,
    "CONFIG_KSU_MANUAL_HOOK": true,
    "CONFIG_KSU_KPROBES_HOOK": false,
    "CONFIG_KSU_SUSFS": true,
    "CONFIG_KSU_SUSFS_SUS_SU": false
  }
}
```
