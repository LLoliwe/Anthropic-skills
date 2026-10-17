/** Pryntor-original offline policy gate. Does NOT install, execute or audit RESET. */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

export const forbiddenInReview = [
  'externalNetwork', 'createWallet', 'fundWallet', 'miningMoves',
  'transfers', 'backgroundAgent', 'paidApi'
];

export function validatePolicy(p) {
  const errors = [];
  if (!p || typeof p !== 'object' || Array.isArray(p)) return ['policy must be a JSON object'];
  if (p.schemaVersion !== 1) errors.push('unsupported schemaVersion');
  if (p.upstream?.repository !== 'Trac-Systems/reset') errors.push('upstream identity mismatch');
  if (!/^[a-f0-9]{40}$/.test(p.upstream?.commit ?? '')) errors.push('full upstream commit SHA required');
  if (p.upstream?.licenseConfirmed !== false) errors.push('license must remain unconfirmed until reviewed');
  if (p.mode !== 'review-only') errors.push('only review-only mode authorized in this version');
  if (p.runtime?.minimumNodeMajorForSigner !== 24) errors.push('Node 24 signer requirement changed');
  for (const field of ['hostSignerInstalled', 'mcpLiveVerified', 'independentDevnetTestVerified']) {
    if (p.runtime?.[field] !== false) errors.push(`${field} is not independently verified`);
  }
  for (const field of forbiddenInReview) {
    if (p.permissions?.[field] !== false) errors.push(`${field} must be explicitly disabled`);
  }
  if (p.permissions?.chatMode !== 'off') errors.push('chat must be off');
  for (const field of ['licenseReview','securityReview','independentValidation','separateHumanLiveGoAhead']) {
    if (p.approvals?.[field] !== false) errors.push(`${field} must not be represented as approved`);
  }
  return errors;
}

export function assessSignerHost({nodeMajor, isolatedHost, reviewedSource, interactiveSecretEntry}) {
  const problems = [];
  if (!Number.isSafeInteger(nodeMajor) || nodeMajor < 24) problems.push('Node.js 24 LTS+ required for documented public signer setup');
  if (isolatedHost !== true) problems.push('isolated host required');
  if (reviewedSource !== true) problems.push('source and dependencies need independent review');
  if (interactiveSecretEntry !== true) problems.push('secure local wallet-password entry required');
  return {readyForSeparateSignerSetup: problems.length === 0, problems};
}

const script = process.argv[1];
if (script && fileURLToPath(import.meta.url) === script) {
  const file = process.argv[2] || new URL('./policy.json', import.meta.url);
  try {
    const policy = JSON.parse(readFileSync(file, 'utf8'));
    const errors = validatePolicy(policy);
    process.stdout.write(JSON.stringify({policyValid:errors.length===0,mode:policy.mode,upstream:policy.upstream?.commit, signerInstalled:false, realMcpTested:false, errors},null,2)+'\n');
    if (errors.length) process.exitCode = 1;
  } catch (e) {
    process.stderr.write('Policy file unavailable or invalid JSON\n');
    process.exitCode=1;
  }
}
