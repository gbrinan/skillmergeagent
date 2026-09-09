const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const script = path.resolve(__dirname, '../scripts/post-generate.cjs');

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'skillmerge hook '));
  t.after(() => fs.rmSync(root, { recursive: true }));
  fs.writeFileSync(path.join(root, 'agent-plan.md'), '# 목적\n업무 요약.\n');
  return root;
}
function run(root, args, input = '') {
  const result = spawnSync(process.execPath, [script, ...args], {
    cwd: root, input, encoding: 'utf8', timeout: 5000, windowsHide: true,
  });
  return { code: result.status, output: result.stdout, error: result.stderr };
}
function stop(root, active = false) {
  return run(root, ['stop'], JSON.stringify({
    hook_event_name: 'Stop', session_id: 'test-session', cwd: root,
    stop_hook_active: active,
  }));
}
test('Given no registered files, when Stop runs, then no continuation', t => {
  const root = fixture(t);
  const result = stop(root);
  assert.equal(result.code, 0);
  assert.deepEqual(JSON.parse(result.output), {});
});
test('Given generated files, when Stop runs, then one review and snapshot', t => {
  const root = fixture(t);
  assert.equal(run(root, ['arm', 'test-session', 'agent-plan.md']).code, 0);
  const result = stop(root);
  assert.equal(result.code, 0);
  assert.equal(JSON.parse(result.output).decision, 'block');
  const status = JSON.parse(run(root, ['status', 'test-session']).output);
  assert.equal(status.phase, 'reviewing');
  assert.equal(fs.readFileSync(status.snapshots[0], 'utf8'), '# 목적\n업무 요약.\n');
});
test('Given review already requested, when Stop repeats, then no loop or false pass', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  stop(root);
  const result = JSON.parse(stop(root, true).output);
  assert.equal(result.decision, undefined);
  assert.equal(typeof result.systemMessage, 'string');
  assert.equal(JSON.parse(run(root, ['status', 'test-session']).output).phase, 'reviewing');
});
test('Given another session, when Stop runs, then registered work remains untouched', t => {
  const root = fixture(t);
  run(root, ['arm', 'other-session', 'agent-plan.md']);
  assert.deepEqual(JSON.parse(stop(root).output), {});
});
test('Given outside or directory target, when arming, then registration fails', t => {
  const root = fixture(t);
  assert.equal(run(root, ['arm', 'test-session', '../outside.md']).code, 1);
  assert.equal(run(root, ['arm', 'test-session', '.']).code, 1);
});
test('Given malformed hook input, when invoked, then visible error without continuation', t => {
  const root = fixture(t);
  const result = run(root, ['stop'], '{');
  assert.equal(result.code, 1);
  assert.ok(result.error.length > 0);
});
test('Given review and empty report, when finishing, then completion is rejected', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  stop(root);
  fs.writeFileSync(path.join(root, 'review.md'), '');
  assert.equal(run(root, ['finish', 'test-session', 'clean', 'review.md']).code, 1);
});
test('Given unchanged completed review, when arming again, then no extra pass', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  stop(root);
  fs.writeFileSync(path.join(root, 'review.md'), '# 검토\n변경 없음, 실행 미검증.\n');
  assert.equal(run(root, ['finish', 'test-session', 'clean', 'review.md']).code, 0);
  assert.equal(JSON.parse(run(root, ['arm', 'test-session', 'agent-plan.md']).output).phase, 'clean');
  assert.deepEqual(JSON.parse(stop(root).output), {});
});
test('Given files changed after registration, when review begins, then baseline is current', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  fs.appendFileSync(path.join(root, 'agent-plan.md'), '정지: 승인 대기.\n');
  stop(root);
  fs.writeFileSync(path.join(root, 'review.md'), '# 검토\n변경 없음.\n');
  assert.equal(run(root, ['finish', 'test-session', 'clean', 'review.md']).code, 0);
});
test('Given cleaned files, when recorded clean, then outcome mismatch fails', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  stop(root);
  fs.appendFileSync(path.join(root, 'agent-plan.md'), '완료 조건: 검토.\n');
  fs.writeFileSync(path.join(root, 'review.md'), '# 검토\n정리함.\n');
  assert.equal(run(root, ['finish', 'test-session', 'clean', 'review.md']).code, 1);
  assert.equal(run(root, ['finish', 'test-session', 'refined', 'review.md']).code, 0);
  fs.appendFileSync(path.join(root, 'agent-plan.md'), '추가 변경\n');
  assert.equal(JSON.parse(run(root, ['status', 'test-session']).output).stale, true);
  assert.equal(typeof JSON.parse(stop(root).output).systemMessage, 'string');
  assert.equal(JSON.parse(run(root, ['arm', 'test-session', 'agent-plan.md']).output).phase, 'pending');
});
test('Given pending approval, when resumed, then same review continues without extra Stop', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  stop(root);
  fs.writeFileSync(path.join(root, 'review.md'), '# 감사안\n승인이 필요한 정리안.\n');
  assert.equal(run(root, ['finish', 'test-session', 'needs-input', 'review.md']).code, 0);
  assert.equal(JSON.parse(run(root, ['resume', 'test-session']).output).phase, 'reviewing');
  assert.equal(JSON.parse(stop(root).output).decision, undefined);
});
test('Given a native config, when generated, then it addresses this executable', t => {
  const root = fixture(t);
  const result = run(root, ['config']);
  assert.equal(result.code, 0);
  const hook = JSON.parse(result.output).hooks.Stop[0].hooks[0];
  assert.equal(hook.type, 'command');
  assert.ok(hook.command.includes(script.replaceAll('\\', '/')));
});
test('Given a symlink escaping scope, when registering, then it is rejected', t => {
  const root = fixture(t);
  const outside = fixture(t);
  fs.symlinkSync(outside, path.join(root, 'linked'), 'junction');
  assert.equal(run(root, ['arm', 'test-session', 'linked/agent-plan.md']).code, 1);
});
test('Given snapshot I/O failure, when explicitly retried, then review can start once', t => {
  const root = fixture(t);
  run(root, ['arm', 'test-session', 'agent-plan.md']);
  const bootstrap = "const fs=require('node:fs');fs.copyFileSync=()=>{throw new Error('injected snapshot I/O failure')};process.argv=[process.execPath,process.argv[1],'stop'];require(process.argv[1]);";
  const failure = spawnSync(process.execPath, ['-e', bootstrap, script], {
    cwd: root, input: JSON.stringify({ hook_event_name: 'Stop', session_id: 'test-session', cwd: root }),
    encoding: 'utf8', windowsHide: true, timeout: 5000,
  });
  assert.equal(failure.status, 1);
  assert.equal(JSON.parse(run(root, ['status', 'test-session']).output).phase, 'failed');
  assert.equal(JSON.parse(stop(root).output).decision, undefined);
  assert.equal(run(root, ['retry', 'test-session']).code, 0);
  assert.equal(JSON.parse(stop(root).output).decision, 'block');
  assert.equal(run(root, ['retry', 'test-session']).code, 1);
  assert.equal(JSON.parse(stop(root, true).output).decision, undefined);
});
