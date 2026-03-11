# openclaw-cultivated-skills Roadmap

## Phase 1: Foundation (Current)

**Goal:** Establish the evaluation pipeline and validate it end-to-end with a small set of seed skills.

- [x] Set up repository structure with 10 skill category directories
- [x] Create candidate tracking file (`candidates.json`) with 54 candidate skills across 4 tiers
- [x] Build pipeline scripts for automated skill evaluation
- [x] Define evaluation methodology and Quality Passport template
- [ ] Validate pipeline with 5 seed skills:
  - Anthropic `docx` (document-processing)
  - Anthropic `pdf` (document-processing)
  - obra `test-driven-development` (development-workflow)
  - Vercel `react-best-practices` (frontend)
  - Trail of Bits `static-analysis` (security)
- [ ] Produce first 5 Quality Passports from seed skill evaluation
- [ ] Refine evaluation criteria based on seed skill results

## Phase 2: First Wave (10-15 skills)

**Goal:** Evaluate all Tier 1 official vendor skills and launch the public catalog.

- [ ] Evaluate remaining Tier 1 official vendor skills (~30 candidates):
  - Anthropic: `pptx`, `xlsx`, `webapp-testing`
  - obra/superpowers: `using-git-worktrees`, `subagent-driven-development`, `systematic-debugging`, `verification-before-completion`, `writing-plans`
  - Vercel: `web-design-guidelines`, `deploy-to-vercel`
  - HashiCorp: `terraform-code-generation`, `terraform-module-generation`
  - Cloudflare: `wrangler`, `agents-sdk`
  - Trail of Bits: `insecure-defaults`, `semgrep-rule-creator`, `property-based-testing`, `modern-python`
  - Google Workspace: `gws-gmail`, `gws-drive`, `gws-calendar`, `gws-sheets`, `gws-docs`
  - Kepano: `obsidian-skills`
  - Stripe: `stripe-best-practices`
  - Hugging Face: `hugging-face-cli`, `hugging-face-model-trainer`
  - Expo: `expo-app-design`
  - Supabase: `postgres`
  - Netlify: core deployment skills
- [ ] Publish Quality Passports for all accepted Tier 1 skills
- [ ] Launch README catalog with skill summaries, ratings, and install instructions
- [ ] Establish acceptance/rejection criteria based on Tier 1 evaluation data

## Phase 3: Expansion (30-50 skills)

**Goal:** Broaden coverage to high-quality community skills and the China ecosystem.

- [ ] Evaluate Tier 2 community skills:
  - `planning-with-files` (OthmanAdi, 15.7K stars)
  - `context-engineering` (muratcankoylan, 13.7K stars)
  - `dev-browser` (SawyerHood, 3.8K stars)
  - `visual-explainer` (nicobailon, 6.3K stars)
  - `antfu-skills` Vue/Nuxt/Vite ecosystem (antfu, 4K stars)
  - `playwright-skill` (lackeyjb, 1.9K stars)
  - `last30days` (mvanhorn, 4K stars)
  - K-Dense-AI scientific skills: `scientific-writing`, `literature-review`, `statistical-analysis` (14.3K stars)
- [ ] Evaluate Tier 3 China Ecosystem skills:
  - `humanizer-zh` (op7418, 4.1K stars)
  - `anything-to-notebooklm` (joeseesun, 508 stars)
  - `videocut-skills` (Ceeon, 1.1K stars)
  - `xray-paper` (lijigang, 487 stars)
- [ ] Cross-reference with awesome-openclaw-usecases-zh for additional Chinese ecosystem candidates
- [ ] Publish Quality Passports for all accepted Tier 2 and Tier 3 skills
- [ ] Update README catalog with expanded listings

## Phase 4: Automation & Community

**Goal:** Automate the evaluation pipeline and open the process to community contributions.

- [ ] Build GitHub Actions CI workflow for automated evaluation on PR submission
- [ ] Create community submission workflow:
  - Issue template for nominating new skill candidates
  - PR template for submitting evaluated skills
  - Contributor guidelines document
- [ ] Integrate with awesome-openclaw-usecases-zh for cross-promotion
- [ ] Monitor Tier 4 specialty skills for maturity:
  - `remotion` (remotion-dev)
  - `typefully` (typefully)
  - `dotnet-skills` (Aaronontheweb)
  - `raptor-security` (gadievron)
- [ ] Establish regular re-evaluation cadence for accepted skills (quarterly)
- [ ] Build dashboard or summary page for skill health metrics

## Metrics

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| Skills evaluated | 5 | 35 | 50+ | Ongoing |
| Quality Passports published | 5 | 15+ | 40+ | Ongoing |
| Categories covered | 3-4 | 8+ | 10 | 10 |
| Pipeline automation | Manual | Semi-auto | Semi-auto | Full CI |
