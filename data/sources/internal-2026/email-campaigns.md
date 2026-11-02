<!-- Internal source copy (INT-10 in internal-sources-2026.md): communications/email/README.md; D7-screened 2026-11-02.; redactions: 1 -->

# Plone Conference 2026 — email campaigns

## Layout

```
email/
├── 1_announcement/
│   ├── input/                  # raw source copy (optional)
│   ├── announcement.mjml       # source of truth
│   ├── announcement.html       # compiled output (what gets sent)
│   └── announcement.txt        # plain-text fallback
├── 2_tickets_cfp/
│   └── ...
└── send_via_mailtrap.py        # sender script
```

The sender script expects **exactly one `.html` and one `.txt` file** per campaign folder and uses the HTML `<title>` as the subject.

## Create a new email

1. Make a folder under `email/`, e.g. `email/3_sprints/`.
2. Write the MJML source and a matching `.txt` fallback. Use `email/1_announcement/announcement.mjml` as the template and follow the brand rules in `AGENTS.md`.
3. Compile:

```bash
npx --yes mjml my-email.mjml -o my-email.html
```

Never hand-edit the generated `.html`.

## Send an email

```bash
python3 email/send_via_mailtrap.py <campaign-folder> <target>
```

- `target = list` sends to `plone-conference@lists.plone.org`
- `target = you@example.com` sends a personal copy

Always test first:

```bash
python3 email/send_via_mailtrap.py 2_tickets_cfp you@example.com --dry-run
```

## SMTP credentials

The sender script reads credentials from the environment. Nothing secret is stored in the repository.

```bash
export SMTP_USER='[redacted: D7 email]'
export SMTP_PASS='...'
```

A real send fails immediately, naming the missing variable, if either is unset. `--dry-run` still works without them so campaign copy can be previewed, and it reports whether credentials are present.

`SMTP_HOST` and `SMTP_PORT` are not secret and default to the production mail server (`sslout.de:465`). Override them for Mailtrap sandbox testing:

```bash
export SMTP_HOST='sandbox.smtp.mailtrap.io'
export SMTP_PORT='2525'
export SMTP_USER='...'
export SMTP_PASS='...'
```

Inspect captured messages at https://mailtrap.io/inboxes.
