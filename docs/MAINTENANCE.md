# Maintenance

## Repository layout

```
komarkun/                         # repo name must equal the username: komarkun/komarkun
├── README.md                     # the profile — rendered on github.com/komarkun
├── .gitignore
├── .github/
│   └── workflows/
│       └── profile-status.yml    # daily refresh of the STATUS + ACTIVITY panels
├── scripts/
│   ├── render_readme.py          # stdlib-only renderer for the auto blocks
│   └── status.config.json        # edit this to change the STATUS panel
└── docs/
    ├── assets/                   # every image the README references lives here
    │   └── banner.png            # hero banner (source: gituhubmd.png)
    ├── DESIGN-SYSTEM.md          # design rules, components, pinning strategy
    ├── AUTOMATION.md             # how the workflow and renderer work
    └── MAINTENANCE.md            # this file
```

Rules of thumb:

- **Images** → `docs/assets/`. Reference them with a **relative** path
  (`docs/assets/banner.png`), never an absolute `https://github.com/...` blob
  URL — relative paths survive a rename and render on the profile page.
- **One image = one purpose.** Name by role (`banner.png`, `stack.svg`,
  `homelab-topology.svg`), not by tool (`img1.png`).
- Prefer **SVG** for anything you draw yourself (diagrams, the stack chart) — it
  stays crisp on HiDPI and is diffable. Keep PNG/JPG for photos and AI art.
- Keep the original of any generated asset out of the repo (see `.gitignore`);
  commit only the version the README uses.
- If a repo grows its own docs, mirror this: `docs/` for prose,
  `docs/assets/` for its images.

## Update by hand

These are not automated — change them when reality changes.

- [ ] **Flip project links to live** when `bucket-explorer` and `cert-watch`
      become public: replace `*private, opening gradually*` / `*in design*`
      with `— [repo](https://github.com/komarkun/<name>)`.
- [ ] **Confirm the project names.** `cert-watch` is a working title — rename in
      `README.md` and `status.config.json` if you pick something else.
- [ ] **`status.config.json`** — update `focus` / `building` / `operating` /
      `learning` whenever your direction shifts. The timestamp updates itself.
- [ ] **Roadmap** — move items between `[ ]`, `[~]`, `[x]` as they progress.
      Only mark `[x]` what you've actually done.
- [ ] **Pinned repositories** — set in the GitHub UI (Customize your pins). Can't
      be scripted. Follow the order in `docs/DESIGN-SYSTEM.md`.
- [ ] **Repo social preview** — Settings → Social preview → upload
      `docs/assets/banner.png` (or a 1280×640 crop) so shared links look right.
- [ ] **Homelab card** — if you publish a write-up or IaC repo, add the link.
- [ ] **Contact** — no email is published. Add one under "Elsewhere" if you want
      inbound from recruiters/clients; `devops@meteor.id` is a work address, so
      consider a personal one.
- [ ] **Banner accuracy** — `banner.png` shows tools you don't use (Azure,
      Ansible, Jenkins, Datadog, Splunk, Istio, Snyk, SonarQube, PagerDuty,
      Vault, Trello). It's decorative and nothing in the text claims them, but a
      sharp reviewer may notice. Consider regenerating it against your real
      stack, or swap in a hand-drawn SVG hero later.

## Do not expose

The profile is public and permanent. Keep all of the following **out** of the
README, commit history, asset metadata, and any future "live" panel:

- IP addresses, MACs, VLAN/subnet details, internal DNS or hostnames
- Real cluster names, `kubeconfig` context names, node names or counts that map
  to physical hardware
- Cloudflare account / zone / tunnel IDs; any API token, kubeconfig, or `.env`
- The actual domain list `cert-watch` monitors
- Employer or client names, project codenames, private repo names that reveal
  client work
- Grafana/Prometheus screenshots, dashboard URLs, or real metric values
- Anything that describes production topology in enough detail to attack it

The current README follows this: the homelab card says "multi-node" with no
numbers, prompts use the generic host `infra`, and the status panel is driven by
a config file you control — it never probes live systems. Keep it that way. If a
future idea needs any of the above to work, don't build it — render a
generalised version instead.

## Validation checklist

Verified in this pass:

- [x] Valid GitHub-Flavored Markdown; no raw HTML beyond `<p align>` and `<sub>`
- [x] `scripts/render_readme.py` runs clean on Python 3.12, stdlib only
- [x] Both marker pairs present and correctly replaced by the renderer
- [x] Panels are 56 columns — no mobile wrap in a code block
- [x] Only link in the file that could 404 is intentionally omitted (WIP repos
      are plain text, not links)
- [x] `tui-todo-listapp` link and stack match its real README
- [x] No secrets, IPs, hostnames, client names, or real metrics
- [x] No fabricated experience, certifications, scale, or stars
- [x] English: concise, no "passionate", no "leveraging", no "fast-paced world"
- [x] Banner uses a relative path and meaningful alt text

Check after first push:

- [ ] Repo is named exactly `komarkun` and is **public**
- [ ] Profile page renders the banner (relative path resolves once pushed)
- [ ] `profile-status` workflow has run once (Actions tab) and committed cleanly
- [ ] Pins set per the strategy
- [ ] Social preview uploaded
- [ ] Viewed on a phone — hero, panels, and project cards read without
      horizontal scrolling of the page body
