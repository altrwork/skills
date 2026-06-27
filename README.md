<p>
  <img src="assets/altr_key_logo_cream_taupe_transparent.png" alt="altr" width="180">
</p>

# altr Skills

[![skills.sh](https://skills.sh/b/altrwork/skills)](https://skills.sh/altrwork/skills)

Skills we use at altr to help businesses run on AI — not just play with it.

altr is an AI automation consultancy. Every skill in this repo has been used in production across real client workflows: outbound sales, content operations, onboarding automation, and Cloudflare-based infrastructure. They are designed to be small, composable, and easy to adapt to your stack. Take them, fork them, make them your own.

## Quickstart (30-second setup)

1. Run the skills.sh installer:

```bash
npx skills@latest add altrwork/skills
```

2. Pick the skills you want and select the coding agents to install them on.

3. Start using them — each skill is invoked by typing `/skill-name` in Claude Code or your preferred agent.

## Or, clone and link directly

```bash
git clone https://github.com/altrwork/skills
cd skills
bash scripts/link-skills.sh
```

This symlinks all skills into `~/.claude/skills` and `~/.agents/skills`. A `git pull` is all you need to stay up to date.

## Why These Skills Exist

Most AI adoption looks like this: a company gives employees access to ChatGPT, a few people use it to write emails, and everyone else waits to be told what to do with it.

Skills fix that. They are reusable instruction files that encode your specific workflows, knowledge, and preferences into commands the AI follows every time. No more rewriting the same prompt. No more hoping the AI figures out your context.

### The three moments where they matter most

**You are repeating yourself.** If you write the same prompt more than twice, you are leaving time on the table. Skills turn one-off prompts into repeatable workflows — one command, every time, exactly how you want it.

**Your workflows span multiple tools.** Most business processes cross systems: a form submission triggers a DocuSign, updates a CRM, and sends an email. A skill can orchestrate all of that. No custom code. No agent engineering. Just a markdown file.

**Your team is not technical.** Skills meet people in sales, marketing, operations, and legal where they already work. You do not need to understand what a context window is to use one.

## Reference

### Marketing & Content

| Skill | What it does |
|---|---|
| **[ab-testing](./skills/marketing/ab-testing/SKILL.md)** | Plan, design, and run A/B experiments with hypothesis writing, statistical significance, and ICE scoring |
| **[amplify](./skills/productivity/amplify/SKILL.md)** | Build before/after compilation videos from raw footage — for tradespeople, creators, or anyone documenting a transformation |
| **[cold-email](./skills/marketing/cold-email/SKILL.md)** | Write B2B cold emails and follow-up sequences that get replies |
| **[content-strategy](./skills/marketing/content-strategy/SKILL.md)** | Plan what content to create: topic clusters, editorial calendars, content pillars |
| **[copywriting](./skills/marketing/copywriting/SKILL.md)** | Write and improve marketing copy for landing pages, homepages, and pricing pages |
| **[edit-article](./skills/marketing/edit-article/SKILL.md)** | Edit articles by restructuring sections, improving clarity, and tightening prose |
| **[emails](./skills/marketing/emails/SKILL.md)** | Build email sequences, drip campaigns, welcome series, and lifecycle flows |
| **[free-tools](./skills/marketing/free-tools/SKILL.md)** | Plan and build free tools for lead generation: calculators, generators, graders |
| **[image](./skills/marketing/image/SKILL.md)** | Generate and optimize marketing images for blogs, social, and product mockups |
| **[lead-magnets](./skills/marketing/lead-magnets/SKILL.md)** | Plan and create lead magnets for email capture: ebooks, checklists, templates |
| **[marketing-ideas](./skills/marketing/marketing-ideas/SKILL.md)** | Brainstorm marketing strategies and tactics for SaaS and service businesses |
| **[marketing-plan](./skills/marketing/marketing-plan/SKILL.md)** | Build a comprehensive marketing plan structured by AARRR, mapped to budget and stage |
| **[marketing-psychology](./skills/marketing/marketing-psychology/SKILL.md)** | Apply behavioral science and cognitive bias to marketing decisions |
| **[offers](./skills/marketing/offers/SKILL.md)** | Design and improve offers: value framing, guarantees, bonuses, payment structure |
| **[social](./skills/marketing/social/SKILL.md)** | Create and optimize social media content for LinkedIn, X, Instagram, and TikTok |

### Engineering

| Skill | What it does |
|---|---|
| **[agents-sdk](./skills/engineering/agents-sdk/SKILL.md)** | Build AI agents on Cloudflare Workers using the Agents SDK |
| **[cloudflare](./skills/engineering/cloudflare/SKILL.md)** | Comprehensive Cloudflare platform skill: Workers, Pages, KV, D1, R2, AI, and security |
| **[cloudflare-email-service](./skills/engineering/cloudflare-email-service/SKILL.md)** | Send and receive transactional emails with Cloudflare Email Service |
| **[durable-objects](./skills/engineering/durable-objects/SKILL.md)** | Create and review Cloudflare Durable Objects for stateful coordination |
| **[mcp-builder](./skills/engineering/mcp-builder/SKILL.md)** | Create high-quality MCP servers for integrating external APIs and services |
| **[sandbox-sdk](./skills/engineering/sandbox-sdk/SKILL.md)** | Build sandboxed applications for secure code execution on Cloudflare |
| **[turnstile-spin](./skills/engineering/turnstile-spin/SKILL.md)** | Set up Cloudflare Turnstile end-to-end: widget, siteverify Worker, and frontend snippets |
| **[web-perf](./skills/engineering/web-perf/SKILL.md)** | Audit and optimize web performance: Core Web Vitals, LCP, INP, CLS |
| **[workers-best-practices](./skills/engineering/workers-best-practices/SKILL.md)** | Review and author Cloudflare Workers code against production best practices |
| **[wrangler](./skills/engineering/wrangler/SKILL.md)** | Cloudflare Workers CLI for deploying and managing Workers, KV, R2, D1, and more |

### Workflow & Productivity

| Skill | What it does |
|---|---|
| **[clipify](./skills/productivity/clipify/SKILL.md)** | Find the best moments in a video, cut them as clips, and reformat for vertical social |
| **[expense-report](./skills/productivity/expense-report/SKILL.md)** | Scan OneDrive for receipts, categorize transactions, and append to a master expense report |
| **[find-skills](./skills/productivity/find-skills/SKILL.md)** | Discover and install agent skills for any task |
| **[grill-me](./skills/productivity/grill-me/SKILL.md)** | Get relentlessly interviewed about a plan until every branch of the decision tree is resolved |
| **[grill-with-docs](./skills/productivity/grill-with-docs/SKILL.md)** | Grilling session that challenges your plan against existing domain docs and updates them inline |
| **[grilling](./skills/productivity/grilling/SKILL.md)** | The reusable interview loop behind grill-me and grill-with-docs |
| **[implement](./skills/productivity/implement/SKILL.md)** | Implement a piece of work based on a PRD or set of issues |
| **[loop-me](./skills/productivity/loop-me/SKILL.md)** | Grill you about specs for workflows you want to build, within the current workspace |
| **[signal-brief](./skills/productivity/signal-brief/SKILL.md)** | Research AI trends on X and Substack, synthesize into a ranked brief, and write a dated file |
| **[teach](./skills/productivity/teach/SKILL.md)** | Teach yourself a new skill or concept across multiple sessions, with stateful progress tracking |

---

Built by [altr](https://altrwork.com) — AI automation for real businesses.

If you want to implement skills like these across your organization, [let's talk](mailto:jarred@altrwork.com).
