// Zero-secret verification of GitHub's signed OIDC identity in an ephemeral runner.
// This does NOT create an agent, grant Supabase access, or synchronize records.
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";

const audience = "pryntor-context-fabric-v1";
const issuer = "https://token.actions.githubusercontent.com";
const decode = x => JSON.parse(Buffer.from(x.replace(/-/g, "+").replace(/_/g, "/"), "base64url").toString("utf8"));
function validate(claims, repo, repoId, now = Math.floor(Date.now() / 1000)) {
  const prefix = repo + "/.github/workflows/context-identity-preflight.yml@refs/heads/main";
  assert.equal(claims.iss, issuer, "issuer");
  assert.equal(claims.aud, audience, "audience");
  assert.equal(claims.repository, repo, "repository");
  assert.equal(String(claims.repository_id), String(repoId), "repository ID");
  assert.equal(claims.repository_owner_id, "250606912", "owner ID");
  assert.equal(claims.workflow_ref, prefix, "workflow ref");
  assert.equal(claims.ref, "refs/heads/main", "branch");
  assert.equal(claims.sub, "repo:" + repo + ":ref:refs/heads/main", "subject");
  assert.ok(["push", "schedule", "workflow_dispatch"].includes(claims.event_name), "event");
  assert.ok(/^[0-9]+$/.test(String(claims.run_id)), "run ID");
  assert.ok(/^[0-9]+$/.test(String(claims.run_attempt)), "attempt");
  assert.ok(Number.isFinite(claims.iat) && Number.isFinite(claims.exp), "timestamp");
  assert.ok(claims.exp - claims.iat > 0 && claims.exp - claims.iat <= 600, "token lifetime");
  assert.ok(claims.iat <= now + 60 && claims.exp > now - 10, "fresh token");
}
async function verify(token) {
  const parts = token.split(".");
  assert.equal(parts.length, 3, "JWT");
  const header = decode(parts[0]);
  const claims = decode(parts[1]);
  assert.equal(header.alg, "RS256", "algorithm");
  assert.ok(typeof header.kid === "string" && header.kid, "key ID");
  const response = await fetch(issuer + "/.well-known/jwks", { signal: AbortSignal.timeout(10000) });
  assert.ok(response.ok, "JWKS availability");
  const json = await response.json();
  const jwk = json.keys.find(k => k.kid === header.kid && k.kty === "RSA" && k.use === "sig" && k.alg === "RS256");
  assert.ok(jwk, "verified signing key");
  const key = await webcrypto.subtle.importKey("jwk", jwk, {name:"RSASSA-PKCS1-v1_5",hash:"SHA-256"}, false, ["verify"]);
  const good = await webcrypto.subtle.verify({name:"RSASSA-PKCS1-v1_5"}, key, Buffer.from(parts[2], "base64url"), Buffer.from(parts[0] + "." + parts[1]));
  assert.ok(good, "JWT signature");
  return claims;
}
if (process.argv.includes("--selftest")) {
  const repo = "LLoliwe/Anthropic-skills", repoId = "1128131192";
  const now = Math.floor(Date.now() / 1000);
  const good = {iss:issuer,aud:audience,repository:repo,repository_id:repoId,repository_owner_id:"250606912",workflow_ref:repo+"/.github/workflows/context-identity-preflight.yml@refs/heads/main",ref:"refs/heads/main",sub:"repo:"+repo+":ref:refs/heads/main",event_name:"schedule",run_id:"1234",run_attempt:"1",iat:now-10,exp:now+120};
  validate(good,repo,repoId,now);
  for(const changed of [{aud:"wrong"},{repository:"another/repo"},{repository_id:"1148852238"},{ref:"refs/heads/evil"},{event_name:"pull_request"},{exp:now-20},{workflow_ref:"other"}]){
    assert.throws(() => validate({...good,...changed},repo,repoId,now));
  }
  console.log("8/8 static workload identity claim checks PASS; no live token tested");
} else {
  const repo = process.env.GITHUB_REPOSITORY;
  const repoId = process.env.EXPECTED_REPO_ID;
  assert.ok(repo && repoId && process.env.GITHUB_REF === "refs/heads/main", "configured repo/main");
  const tokenUrl = new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL);
  tokenUrl.searchParams.set("audience", audience);
  const response = await fetch(tokenUrl, {
    headers:{Authorization:"Bearer "+process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN},
    signal:AbortSignal.timeout(10000)
  });
  assert.ok(response.ok, "GitHub OIDC token issue");
  const token = (await response.json()).value;
  assert.ok(typeof token === "string", "received token");
  const claims = await verify(token);
  validate(claims,repo,repoId);
  console.log(JSON.stringify({signed_identity_verified:true,repository:repo,repository_id:repoId,event:claims.event_name,run_id:claims.run_id,run_attempt:claims.run_attempt,credential_lifetime_seconds:claims.exp-claims.iat}));
  // Intentionally do not print, write, transmit or persist the JWT.
}