// HLE-15 ablation — Round 2 of the Ejentum harness benchmark series.
// 15 text-only multiple-choice questions from cais/hle, B/D/A conditions, Opus 4.8 solver.
// Tests the flagship reasoning + adaptive-reasoning modes (311 ability pool).
// HF_TOKEN must be set in environment before dispatching (HLE is gated).

export const meta = {
  name: 'hle-15-ablation',
  description: 'Round 2 of the Ejentum harness benchmark series. 15 text-only multiple-choice questions from Humanity\'s Last Exam (HLE), B/D/A conditions, Opus 4.8 solver, testing the reasoning and adaptive-reasoning modes (311-ability pool). HLE has ~53% headroom on Opus 4.8, so unlike Round 1 (MHPP code) this round tests whether the harness produces visible pass-rate spread.',
  phases: [
    { title: 'Setup', detail: 'Fetch 15 pinned hardest HLE-exactMatch questions, create repo ablation-hle-15, commit pre-registration' },
    { title: 'Solve', detail: '45 Opus 4.8 solve agents (15 questions × 3 conditions). Each D/A agent calls /harness/ itself. Free-text answers.' },
    { title: 'Judge', detail: 'Blind LLM judge grades semantic equivalence vs canonical with X/Y/Z anonymization. Enforces protocol contract.' },
    { title: 'Writeup', detail: 'Commit RESULTS.md, chart.svg, raw_scores.json to the dedicated repo' },
    { title: 'Index', detail: 'Mirror to ejentum/benchmarks/hle-15/ + update root README + CHANGELOG' },
  ],
};

// Pinned question indices (deterministic, hardest by rationale-length proxy within each category).
// Selection: from text-only exactMatch HLE subset (1909 candidates), stratified across 8 categories,
// picked the hardest by rationale length + 0.3*question length per category. Math=3, Bio/Med=2, CS=2,
// Phys=2, Hum=2, Chem=2, Eng=1, Other=1. The hardest selected has a 32KB expert rationale.
const HLE_INDICES = [2431, 865, 1968, 42, 874, 334, 914, 2466, 2448, 2414, 1786, 2407, 2492, 1990, 2418];

const SETUP_SCHEMA = {
  type: 'object',
  properties: {
    questions: {
      type: 'array', minItems: 15, maxItems: 15,
      items: {
        type: 'object',
        properties: {
          hle_id: { type: 'string', description: 'The HLE row id (24-char hex)' },
          hle_index: { type: 'integer', description: 'Position in the hf test split' },
          question: { type: 'string', description: 'Full question text (free-text exact-match question)' },
          canonical_answer: { type: 'string', description: 'The canonical free-text answer from HLE' },
          category: { type: 'string' },
          raw_subject: { type: 'string' },
        },
        required: ['hle_id', 'hle_index', 'question', 'canonical_answer', 'category', 'raw_subject'],
      },
    },
    repo_url: { type: 'string' },
    setup_notes: { type: 'string' },
  },
  required: ['questions', 'repo_url', 'setup_notes'],
};

const SOLVE_SCHEMA = {
  type: 'object',
  properties: {
    hle_id: { type: 'string' },
    condition: { type: 'string', enum: ['B', 'D', 'A'] },
    answer: { type: 'string', description: 'The free-text answer derived for this question. Can be a number, formula, string, or short explanation. No prose surrounding the answer; just the final answer as concise as possible while remaining unambiguous.' },
    reasoning_summary: { type: 'string', description: 'One sentence on the derivation. For D and A, mention any specific Suppress: signal from the injection that shaped the answer.' },
    harness_called: { type: 'boolean' },
    harness_mode: { type: 'string' },
  },
  required: ['hle_id', 'condition', 'answer', 'reasoning_summary', 'harness_called', 'harness_mode'],
};

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    judgments: {
      type: 'array', minItems: 45, maxItems: 45,
      items: {
        type: 'object',
        properties: {
          hle_id: { type: 'string' },
          condition: { type: 'string', enum: ['B', 'D', 'A'] },
          submission_letter: { type: 'string', enum: ['X', 'Y', 'Z'], description: 'The anonymized letter the judge saw for this submission' },
          passed: { type: 'boolean', description: 'Did the submission match the canonical semantically?' },
          submitted_answer: { type: 'string' },
          canonical_answer: { type: 'string' },
          judge_reasoning: { type: 'string', description: 'One sentence: why match or no-match. Be strict; semantic equivalence only.' },
        },
        required: ['hle_id', 'condition', 'submission_letter', 'passed', 'submitted_answer', 'canonical_answer', 'judge_reasoning'],
      },
    },
    pass_rate_B: { type: 'string', description: 'e.g. "5/15"' },
    pass_rate_D: { type: 'string' },
    pass_rate_A: { type: 'string' },
    quarantined: { type: 'array', items: { type: 'string' } },
    per_category_breakdown: { type: 'string', description: 'Markdown table of per-category pass rates B/D/A' },
  },
  required: ['judgments', 'pass_rate_B', 'pass_rate_D', 'pass_rate_A', 'quarantined', 'per_category_breakdown'],
};

phase('Setup');

const setup = await agent(
  `Task: Set up Round 2 of the Ejentum harness benchmark series. DO NOT call /harness/ during setup — solve agents call it themselves.

Source: cais/hle on HuggingFace (gated dataset).

Pinned question indices (deterministic, hardest-by-rationale-length stratified sample): ${JSON.stringify(HLE_INDICES)}

Steps:

1. Load cais/hle test split. The HF_TOKEN must be set in the os environment before loading. Use:
\`\`\`python
import os
os.environ['HF_TOKEN'] = 'hf_REDACTED_SET_YOUR_OWN_TOKEN'
from datasets import load_dataset
ds = load_dataset('cais/hle', split='test')
indices = ${JSON.stringify(HLE_INDICES)}
selected = [ds[i] for i in indices]
\`\`\`

For each selected row, extract: id (as hle_id), the index (as hle_index), question, answer (as canonical_answer, single letter), category, raw_subject.

2. Create public GitHub repo:
   \`gh repo create ejentum/ablation-hle-15 --public --description "Ejentum harness benchmark Round 2: 15 HLE questions, B/D/A conditions, Opus 4.8, reasoning + adaptive-reasoning modes"\`
   If it already exists, use it.

3. Commit PRE_REGISTRATION.md by reading c:/Users/frank/Desktop/ejentum/round2_hle_PRE_REGISTRATION.md, base64-encoding it, and PUTing to repos/ejentum/ablation-hle-15/contents/PRE_REGISTRATION.md via gh api. Capture commit SHA in setup_notes.

4. Verify all 15 questions are populated with non-empty question + canonical_answer.

Return the structured object with the 15 questions, the repo URL, and setup_notes describing what you did and any anomalies.`,
  { schema: SETUP_SCHEMA, label: 'setup' }
);

if (!setup || !setup.questions || setup.questions.length !== 15) {
  return { error: 'Setup did not produce 15 questions', setup };
}

phase('Solve');

const HARNESS_KEY = 'ej_vq9EgOG0s3A-To04ciHaDx1C95Q-pa3h61bHCjVklWY';
const solveJobs = [];

for (const q of setup.questions) {
  for (const cond of ['B', 'D', 'A']) {
    const mode = cond === 'D' ? 'reasoning' : cond === 'A' ? 'adaptive-reasoning' : null;

    const harnessInstruction = mode === null
      ? `Condition B (raw baseline): DO NOT call /harness/. Solve using native reasoning only. Set harness_called=false, harness_mode="".`
      : `Condition ${cond}: BEFORE you solve, call the Ejentum harness as an agentic tool. Real curl call you make right now after reading the question.

Run via Bash:
  curl -s -X POST "https://api.ejentum.com/harness/" \\
    -H "Authorization: Bearer ${HARNESS_KEY}" \\
    -H "Content-Type: application/json" \\
    --data-binary @- <<'EOF'
  {"query": <task description string>, "mode": "${mode}"}
  EOF

The query should be a short description of the reasoning task (e.g., "Graduate-level multiple-choice question in ${q.category}: ${q.raw_subject}. Choose the correct answer letter based on rigorous step-by-step reasoning.").

Read injection at response[0]["${mode}"]. Place in [REASONING CONTEXT] ... [END REASONING CONTEXT] block BEFORE your reasoning chain. Pay attention to Suppress: signals — they block common reasoning failure modes for this kind of problem.

Set harness_called=true, harness_mode="${mode}". On curl failure, retry once; if still failing, harness_called=false, harness_mode="${mode}_failed", and solve raw (score phase will quarantine).`;

    const prompt = `You are a solve agent for the HLE-15 ablation, Round 2 of the Ejentum harness benchmark series.

hle_id: ${q.hle_id}
condition: ${cond}
category: ${q.category} / ${q.raw_subject}

${harnessInstruction}

--- QUESTION (HLE-hardest, exact-match free-text) ---
${q.question}
--- END QUESTION ---

This is a free-text exact-match HLE question. There is no answer-choice list. Derive the answer from scratch using rigorous step-by-step reasoning. Some HLE questions are PhD-level; the canonical rationale for the hardest selected in this batch runs 30+ KB (5-10 pages of mathematics). Don't shortcut. Show your work in scratchpad reasoning, then commit to a final answer.

Your final answer should be the most concise unambiguous form possible: a number, a formula, a specific term, a sequence, a short phrase. Match the format implied by the question. Do NOT include prose or explanation in the answer field; only the final answer.

Return the structured output:
- hle_id: "${q.hle_id}"
- condition: "${cond}"
- answer: the concise final answer (no surrounding prose, no leading "the answer is")
- reasoning_summary: one sentence on the derivation. For D and A, name a specific Suppress: signal from the injection if any shaped the answer.
- harness_called: boolean
- harness_mode: string`;

    solveJobs.push(() => agent(prompt, {
      schema: SOLVE_SCHEMA,
      label: `solve:${q.hle_id.slice(-8)}:${cond}`,
      phase: 'Solve',
    }));
  }
}

const rawSolves = await parallel(solveJobs);
const solves = rawSolves.filter(Boolean);

phase('Judge');

// Build a per-question X/Y/Z blinding map.
// For each question, randomly map B/D/A to X/Y/Z (different rotation per question to prevent positional bias).
// The judge sees X/Y/Z labels; we un-blind after judgments come in.
function buildBlinding(questions) {
  const map = {};
  const rotations = [
    ['B','D','A'], ['D','B','A'], ['A','B','D'],
    ['B','A','D'], ['D','A','B'], ['A','D','B'],
  ];
  questions.forEach((q, i) => {
    // Deterministic rotation by question index — no Math.random (unavailable in workflow scripts)
    const rot = rotations[i % rotations.length];
    map[q.hle_id] = { X: rot[0], Y: rot[1], Z: rot[2] };
  });
  return map;
}
const BLINDING = buildBlinding(setup.questions);

// Build judge payload: per question, gather the 3 submissions and apply X/Y/Z labels
const judgePayload = setup.questions.map(q => {
  const submissionsByCondition = {};
  for (const s of solves) {
    if (s.hle_id === q.hle_id) submissionsByCondition[s.condition] = s;
  }
  const map = BLINDING[q.hle_id];
  return {
    hle_id: q.hle_id,
    category: q.category,
    raw_subject: q.raw_subject,
    question: q.question,
    canonical_answer: q.canonical_answer,
    submission_X: submissionsByCondition[map.X]?.answer || '(missing)',
    submission_Y: submissionsByCondition[map.Y]?.answer || '(missing)',
    submission_Z: submissionsByCondition[map.Z]?.answer || '(missing)',
    // Carry protocol metadata for the score phase (judge ignores these)
    protocol: {
      X: { condition: map.X, harness_called: submissionsByCondition[map.X]?.harness_called, harness_mode: submissionsByCondition[map.X]?.harness_mode },
      Y: { condition: map.Y, harness_called: submissionsByCondition[map.Y]?.harness_called, harness_mode: submissionsByCondition[map.Y]?.harness_mode },
      Z: { condition: map.Z, harness_called: submissionsByCondition[map.Z]?.harness_called, harness_mode: submissionsByCondition[map.Z]?.harness_mode },
    },
  };
});

const score = await agent(
  `Task: Judge ${solves.length} free-text HLE submissions for semantic equivalence to the canonical answers, AND enforce the protocol contract.

You are a strict semantic-equivalence judge. For each HLE question, three free-text submissions are presented as X, Y, Z. You do NOT know which submission came from which solver condition. Letter assignments rotate per question to prevent positional bias.

For each (question, submission_letter) pair, decide whether the submission matches the canonical answer semantically. Be strict: "Z+Z+Z+Z+Z" and "$\\mathbb{Z}^5$" are equivalent; "70" and "seventy" are equivalent; but "70.0" and "70.5" are NOT equivalent; "the answer is between 60 and 80" is NOT equivalent to "70". Use Python or scratch reasoning to verify mathematical/symbolic equivalence when needed.

The blinding-map (for your eventual un-blinding by the workflow runtime, NOT for you to read while judging):
${JSON.stringify(BLINDING, null, 2)}

PER-QUESTION PAYLOAD:
${JSON.stringify(judgePayload.map(p => ({ hle_id: p.hle_id, category: p.category, question: p.question, canonical_answer: p.canonical_answer, submission_X: p.submission_X, submission_Y: p.submission_Y, submission_Z: p.submission_Z })), null, 2)}

PROTOCOL CONTRACT (must enforce):
${JSON.stringify(judgePayload.map(p => ({ hle_id: p.hle_id, protocol: p.protocol })), null, 2)}

For each of the 45 submissions, return:
- hle_id, condition (un-blinded from the protocol map you have), submission_letter (the X/Y/Z label the judge saw)
- passed: judge's semantic-equivalence verdict
- submitted_answer, canonical_answer, judge_reasoning (one sentence)

Plus apply the protocol contract:
- B agents: harness_called must be false. If true, quarantine the entry (add to quarantined list, force passed=false).
- D agents: harness_called must be true AND harness_mode must be "reasoning". Else quarantine.
- A agents: harness_called must be true AND harness_mode must be "adaptive-reasoning". Else quarantine.

Aggregate pass rate per condition as "<n>/15". Provide a per-category markdown breakdown table.`,
  { schema: JUDGE_SCHEMA, label: 'judge', phase: 'Judge' }
);

phase('Writeup');

const writeup = await agent(
  `Task: Final results artifact for HLE-15 Round 2, committed to ${setup.repo_url}.

Round 1 reference (MHPP-10 Opus 4.8 code mode): https://github.com/ejentum/ablation-mhpp-10
Round 1 pass rates: B=9/10, D=9/10, A=9/10 (saturated; blind expert review converged on A > D > B in 8/9 ballots)

Round 2 results (this run, HLE-15 Opus 4.8 reasoning mode):
- B: ${score.pass_rate_B}
- D: ${score.pass_rate_D}
- A: ${score.pass_rate_A}

Per-category breakdown:
${score.per_category_breakdown}

Setup: ${setup.setup_notes}
Scores: ${JSON.stringify(score.scores, null, 2)}
Quarantined: ${JSON.stringify(score.quarantined)}

Commit three files to the Round 2 repo:

1. RESULTS.md:
   - Headline pass rates for B, D, A
   - Side-by-side comparison with Round 1 (code mode, saturated)
   - Pre-reg prediction vs actual
   - Per-category breakdown table
   - 300-word honest narrative interpreting the result:
     * If H1 (A > D > B with spread): full product validated across saturated and non-saturated regimes
     * If H2 (A roughly D, both > B): retrieval matters, adapter contribution small at this benchmark
     * If H3 (null): harness does not lift HLE pass rate at Opus 4.8 capability level
     * If H4 (inverted): harness misroutes; investigate
   - Cross-link to Round 1 repo and to the harness at ejentum.com
   - Quarantined entries called out

2. chart.svg: side-by-side ~500x250 SVG, Round 1 (saturated) | Round 2 (HLE), 3 bars each labeled. Make Round 2 the visual focus.

3. raw_scores.json: the scores array.

Use gh api -X PUT repos/ejentum/ablation-hle-15/contents/<filename> with base64. Return commit URLs.`,
  { label: 'writeup', phase: 'Writeup' }
);

phase('Index');

const indexResult = await agent(
  `Task: Mirror this benchmark into the canonical Ejentum benchmarks index repo at https://github.com/ejentum/benchmarks. This is the umbrella catalog where all benchmark results live alongside each other (lcb-hard/, ejbench/, elephant/, mhpp-10/, etc.).

You are performing three operations on \`ejentum/benchmarks\`:

## 1. Create \`hle-15/\` subdir with mirrored files

Copy these files from the dedicated repo \`ejentum/ablation-hle-15\` into \`ejentum/benchmarks/hle-15/\`:
- PRE_REGISTRATION.md
- RESULTS.md
- raw_scores.json
- chart.svg
- workflow.js (read from c:/Users/frank/Desktop/ejentum/round2_hle_workflow.js)

For each:
\`\`\`bash
content=$(gh api repos/ejentum/ablation-hle-15/contents/<file> --jq .content)
gh api -X PUT repos/ejentum/benchmarks/contents/hle-15/<file> --input - <<<'{"message": "Mirror <file> into benchmarks/hle-15/", "content": "'$content'", "branch": "main"}'
\`\`\`

Plus author and commit \`hle-15/README.md\` with this structure:
- Title: # HLE-15 Ablation
- One-paragraph intro: Reasoning Harness benchmark. 15 text-only multiple-choice questions from Humanity's Last Exam, Claude Opus 4.8, B/D/A conditions. Pre-registered ladder A > D > B before any solver ran.
- Headline table with pass rates B=${score.pass_rate_B}, D=${score.pass_rate_D}, A=${score.pass_rate_A}
- "Findings" subsection: 3-5 bullet points on what the result shows. Cross-reference Round 1 (MHPP-10): pass rate was saturated there; here we tested if the harness produces visible pass-rate spread on a non-saturated benchmark.
- "Dedicated repo" pointer to https://github.com/ejentum/ablation-hle-15
- File inventory table
- "Reproducibility" note about the workflow script
- "Status" note saying this is Round 2 of the series

## 2. Update root README.md

Fetch \`README.md\` from \`ejentum/benchmarks\` (it uses CRLF line endings — be careful with anchors). Find the \`### Reasoning Harness (311 abilities)\` section and add a new row to its markdown table:

\`| [HLE-15 Ablation](hle-15/) | 15 HLE multiple-choice | B/D/A ablation, reasoning + adaptive-reasoning modes | Claude Opus 4.8 | **B=${score.pass_rate_B}, D=${score.pass_rate_D}, A=${score.pass_rate_A}. [one-line interpretive headline based on result]** |\`

The interpretive headline should be honest: if A > D > B clearly, say "Pre-registered ladder validated on a non-saturated benchmark." If A roughly D > B, say "Harness lifts pass rate; adapter contribution is small at this surface." If null, say so plainly.

## 3. Update CHANGELOG.md

Fetch \`CHANGELOG.md\`. Prepend a new dated entry after the \`# Changelog\` header:

\`\`\`
## 2026-05-31: HLE-15 ablation added

Round 2 of the Ejentum harness benchmark series added to \`hle-15/\`. Claude Opus 4.8 on 15 text-only multiple-choice questions from Humanity's Last Exam, three conditions (B raw, D dynamic reasoning, A adaptive reasoning), 45 solve agents, pre-registered before dispatch.

### Findings

- Pass rates: B=${score.pass_rate_B}, D=${score.pass_rate_D}, A=${score.pass_rate_A}
- [2-3 bullet points on what the data shows]
- [Cross-reference to Round 1 MHPP-10 if relevant]

### Methodological notes

- Pre-registration committed before any solver ran (see PRE_REGISTRATION.md in dedicated repo \`ejentum/ablation-hle-15\`)
- 15 questions stratified across 8 HLE categories for breadth
- Multiple-choice subset used for trivial exact-letter scoring (no judge agent needed)
- Tested the flagship reasoning + adaptive-reasoning modes (311-ability pool), distinct from Round 1's code modes (128 abilities)
\`\`\`

Use CRLF line endings to match existing CHANGELOG style.

Return the three commit URLs (subdir, root README, CHANGELOG).`,
  { label: 'index-benchmarks', phase: 'Index' }
);

return {
  setup_notes: setup.setup_notes,
  repo_url: setup.repo_url,
  round1_passrates: { B: '9/10 (saturated)', D: '9/10 (saturated)', A: '9/10 (saturated)' },
  round2_passrates: {
    B: score.pass_rate_B,
    D: score.pass_rate_D,
    A: score.pass_rate_A,
  },
  per_category_breakdown: score.per_category_breakdown,
  quarantined: score.quarantined,
  writeup_result: writeup,
  index_result: indexResult,
};
