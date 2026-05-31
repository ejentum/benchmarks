export const meta = {
  name: 'mhpp-10-ablation',
  description: 'F2-style ablation on 10 hardest MHPP tasks. 3 conditions per task (raw / dynamic-code / adaptive-code). Each solve agent calls /harness/ itself when it sees its task (agentic-tool pattern). Public repo ejentum/ablation-mhpp-10 with pre-registration committed before solve agents run.',
  phases: [
    { title: 'Setup', detail: 'Fetch MHPP, pick 10 hardest, create repo, pre-register. NO /harness/ calls.' },
    { title: 'Solve', detail: '30 parallel agents — D and A agents call /harness/ themselves when they see their task' },
    { title: 'Score', detail: 'Run hidden tests on each output, enforce protocol contract' },
    { title: 'Writeup', detail: 'Chart + table + commit results to repo' },
  ],
};

const SETUP_SCHEMA = {
  type: 'object',
  properties: {
    tasks: {
      type: 'array',
      minItems: 10,
      maxItems: 10,
      items: {
        type: 'object',
        properties: {
          task_id: { type: 'string' },
          prompt: { type: 'string', description: 'Full MHPP task prompt' },
          test_code: { type: 'string', description: 'Hidden test code, executable Python' },
          entry_point: { type: 'string', description: 'Function name the solution must define' },
        },
        required: ['task_id', 'prompt', 'test_code', 'entry_point'],
      },
    },
    repo_url: { type: 'string' },
    setup_notes: { type: 'string' },
  },
  required: ['tasks', 'repo_url', 'setup_notes'],
};

const SOLVE_SCHEMA = {
  type: 'object',
  properties: {
    task_id: { type: 'string' },
    condition: { type: 'string', enum: ['B', 'D', 'A'] },
    code: { type: 'string', description: 'Complete executable Python. No fences, no prose.' },
    harness_called: { type: 'boolean' },
    harness_mode: { type: 'string' },
  },
  required: ['task_id', 'condition', 'code', 'harness_called', 'harness_mode'],
};

const SCORE_SCHEMA = {
  type: 'object',
  properties: {
    scores: {
      type: 'array',
      minItems: 30,
      maxItems: 30,
      items: {
        type: 'object',
        properties: {
          task_id: { type: 'string' },
          condition: { type: 'string', enum: ['B', 'D', 'A'] },
          passed: { type: 'boolean' },
          error: { type: 'string' },
        },
        required: ['task_id', 'condition', 'passed', 'error'],
      },
    },
    pass_rate_B: { type: 'string' },
    pass_rate_D: { type: 'string' },
    pass_rate_A: { type: 'string' },
    quarantined: { type: 'array', items: { type: 'string' } },
  },
  required: ['scores', 'pass_rate_B', 'pass_rate_D', 'pass_rate_A', 'quarantined'],
};

phase('Setup');

const setup = await agent(
  `Task: Set up the MHPP-10 ablation. DO NOT CALL /harness/ — the solve agents call it themselves when they see their task. This is the agentic-tool pattern, not pre-generation.

Steps:

1. Fetch MHPP from HuggingFace. Try in order:
   - datasets.load_dataset('prometheus-eval/MHPP', split='test')
   - datasets.load_dataset('SparksofAGI/MHPP', split='test')
   - Web search 'MHPP More Heuristics Patient Problems HuggingFace dataset' if both fail
   Install datasets via pip if needed.

2. Pick 10 hardest tasks. If a difficulty field exists, sort and take top 10. Else use canonical_solution length as a proxy. Document the strategy in setup_notes.

3. Create public repo ejentum/ablation-mhpp-10 via gh CLI. If it exists, use it.

4. Commit PRE_REGISTRATION.md to main with this content:

# MHPP-10 Ablation — Pre-Registration

Date: 2026-05-31
Model: Claude Opus 4.7 via Claude Code subagent fleet
Reps: 1 per (task, condition) pair
Protocol: each solve agent calls /harness/ itself when it sees its task (agentic-tool pattern, not pre-generation)

## Conditions
- B (raw baseline): no harness call, solve directly
- D (dynamic code): agent calls /harness/ with mode=code, injects top-1 retrieval, then solves
- A (adaptive code): agent calls /harness/ with mode=adaptive-code, injects top-5 + adapter-rewritten scaffold, then solves

## Predicted pass rates (out of 10)
- A: 6-8 (full product)
- D: 4-6 (content matched, no adapter)
- B: 2-4 (Opus 4.7 native on hardest MHPP)

## Hypotheses
- H1: A > D > B (clean step-ladder)
- H2: A roughly equal to D, both > B (harness helps, adapter is icing)
- H3: null result, all roughly equal (publish honestly)

## Commitment
Results published whether they confirm or not.

Use gh api -X PUT repos/ejentum/ablation-mhpp-10/contents/PRE_REGISTRATION.md with base64-encoded content. Capture commit SHA in setup_notes.

5. Verify every task has all 4 fields non-empty. Return EXACTLY 10 tasks.`,
  { schema: SETUP_SCHEMA, label: 'setup' }
);

if (!setup || !setup.tasks || setup.tasks.length !== 10) {
  return { error: 'Setup did not produce 10 tasks', setup };
}

phase('Solve');

const HARNESS_KEY = 'ej_vq9EgOG0s3A-To04ciHaDx1C95Q-pa3h61bHCjVklWY';
const solveJobs = [];

for (const task of setup.tasks) {
  for (const cond of ['B', 'D', 'A']) {
    const mode = cond === 'D' ? 'code' : cond === 'A' ? 'adaptive-code' : null;

    const harnessInstruction = mode === null
      ? `Condition B (raw baseline): DO NOT call /harness/. Solve using native reasoning only. Set harness_called=false, harness_mode="".`
      : `Condition ${cond}: BEFORE you solve, call the Ejentum harness as an agentic tool. This is a real curl call you make right now after reading the task — not a pre-fetched scaffold.

Run via Bash:
  curl -s -X POST "https://api.ejentum.com/harness/" \\
    -H "Authorization: Bearer ${HARNESS_KEY}" \\
    -H "Content-Type: application/json" \\
    --data-binary @- <<'EOF'
  {"query": <task prompt as JSON string>, "mode": "${mode}"}
  EOF

The response is a JSON array. Read the injection string at response[0]["${mode}"].

Place it in your reasoning BEFORE you start writing code:
  [REASONING CONTEXT]
  {injection string}
  [END REASONING CONTEXT]

Pay special attention to Suppress: signals — they block your default failure modes.

Then solve the task.

Set harness_called=true, harness_mode="${mode}". If the curl fails after one retry, set harness_called=false, harness_mode="${mode}_failed", and the score phase will quarantine this entry.`;

    const prompt = `You are a solve agent in an MHPP ablation.

task_id: ${task.task_id}
condition: ${cond}
entry_point: ${task.entry_point}

${harnessInstruction}

--- PROBLEM ---
${task.prompt}
--- END PROBLEM ---

Return:
- task_id: "${task.task_id}"
- condition: "${cond}"
- code: complete Python defining ${task.entry_point}. No fences. No prose.
- harness_called: boolean
- harness_mode: string`;

    solveJobs.push(() => agent(prompt, {
      schema: SOLVE_SCHEMA,
      label: `solve:${task.task_id}:${cond}`,
      phase: 'Solve',
    }));
  }
}

const rawSolves = await parallel(solveJobs);
const solves = rawSolves.filter(Boolean);

phase('Score');

const score = await agent(
  `Task: Score ${solves.length} solve outputs against MHPP hidden tests AND enforce the protocol contract.

For each output:

1. Protocol check:
   - B: harness_called must be false. If true → quarantine, count fail.
   - D: harness_called must be true and harness_mode must be "code". Else → quarantine, count fail.
   - A: harness_called must be true and harness_mode must be "adaptive-code". Else → quarantine, count fail.
   - task_id must match one of the 10. Else → quarantine.

2. Strip markdown fences if any agent wrapped code in triple backticks.

3. Execute in subprocess. Write tempfile with agent code + test_code. python3, 30s timeout. Pass = exit 0 no exceptions.

4. Capture first line of traceback for failures.

5. Pass rate per condition as "<n>/10".

Tasks (id, entry_point, test_code):
${JSON.stringify(setup.tasks.map(t => ({ task_id: t.task_id, entry_point: t.entry_point, test_code: t.test_code })), null, 2)}

Solve outputs:
${JSON.stringify(solves, null, 2)}`,
  { schema: SCORE_SCHEMA, label: 'score', phase: 'Score' }
);

phase('Writeup');

const writeup = await agent(
  `Task: Final results artifact, committed to ${setup.repo_url}.

Inputs:
- Setup: ${setup.setup_notes}
- Pass rates: B=${score.pass_rate_B}, D=${score.pass_rate_D}, A=${score.pass_rate_A}
- Scores: ${JSON.stringify(score.scores, null, 2)}
- Quarantined: ${JSON.stringify(score.quarantined)}

Commit three files to the repo:

1. RESULTS.md — headline pass rates; pre-reg prediction vs actual table; 10x3 per-task P/F matrix; 200-word honest narrative; quarantined entries called out.

2. chart.svg — hand-written ~300x200 SVG bar chart with 3 bars (B/D/A) labeled.

3. raw_scores.json — the scores array.

Use gh api -X PUT repos/ejentum/ablation-mhpp-10/contents/<filename> with base64 content for each. Return commit URLs.`,
  { label: 'writeup', phase: 'Writeup' }
);

return {
  setup_notes: setup.setup_notes,
  repo_url: setup.repo_url,
  pass_rate_B: score.pass_rate_B,
  pass_rate_D: score.pass_rate_D,
  pass_rate_A: score.pass_rate_A,
  quarantined: score.quarantined,
  writeup_result: writeup,
};
