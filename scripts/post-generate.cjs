const fs = require('node:fs');
const path = require('node:path');
const { createHash, randomUUID } = require('node:crypto');

const digest = value => createHash('sha256').update(value).digest('hex');
function object(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Expected JSON object');
  return value;
}
function text(value) {
  if (typeof value !== 'string' || !value.trim()) throw new Error('Expected nonempty string');
  return value;
}
function localFile(root, name) {
  const file = fs.realpathSync(path.resolve(root, text(name)));
  const relative = path.relative(root, file);
  if (!relative || relative.startsWith('..') || path.isAbsolute(relative) ||
      relative.split(path.sep).some(part => part.startsWith('.')) ||
      !file.endsWith('.md') || !fs.statSync(file).isFile()) {
    throw new Error('Target must be an existing Markdown file inside the working directory');
  }
  return file;
}
function location(root, session) {
  const base = path.join(root, '.skillmerge-review');
  const dir = path.join(base, digest(text(session)));
  for (const candidate of [base, dir]) {
    if (fs.existsSync(candidate) && fs.realpathSync(candidate) !== candidate) {
      throw new Error('Review state directory must not be a symlink');
    }
  }
  return dir;
}
function readState(dir) {
  const file = path.join(dir, 'state.json');
  if (!fs.existsSync(file)) return null;
  if (fs.lstatSync(file).isSymbolicLink()) throw new Error('State file must not be a symlink');
  const state = object(JSON.parse(fs.readFileSync(file, 'utf8')));
  if (!['pending', 'reviewing', 'clean', 'refined', 'needs-input'].includes(state.phase) ||
      !Array.isArray(state.files) || !state.files.length ||
      state.files.some(file => typeof file !== 'string') ||
      typeof state.fingerprint !== 'string' || typeof state.generation !== 'string') {
    throw new Error('Invalid review state');
  }
  return state;
}
function writeState(dir, state) {
  fs.mkdirSync(dir, { recursive: true });
  const temporary = path.join(dir, randomUUID() + '.tmp');
  fs.writeFileSync(temporary, JSON.stringify(state, null, 2) + '\n', { flag: 'wx' });
  fs.renameSync(temporary, path.join(dir, 'state.json'));
}
function fingerprint(files) {
  return digest(JSON.stringify(files.map(file => [file, digest(fs.readFileSync(file))])));
}
function main() {
  const [command, session, ...args] = process.argv.slice(2);
  if (command === 'config') {
    return { hooks: { Stop: [{ hooks: [{ type: 'command', timeout: 10,
      command: 'node ' + JSON.stringify(__filename.replaceAll('\\', '/')) + ' stop',
    }] }] } };
  }
  if (command === 'stop') {
    const event = object(JSON.parse(fs.readFileSync(0, 'utf8')));
    if (event.hook_event_name !== 'Stop') return {};
    const root = fs.realpathSync(text(event.cwd));
    const dir = location(root, event.session_id);
    const state = readState(dir);
    if (!state) return {};
    const files = state.files.map(file => localFile(root, file));
    if (state.phase !== 'pending') {
      if (state.phase === 'reviewing' || state.phase === 'needs-input' ||
          fingerprint(files) !== state.fingerprint) {
        return { systemMessage: 'skillmergeagent: 검토 미완료·보류 또는 검토 후 변경. status를 확인하고 완료로 보고하지 마세요. 자동 재검토는 반복하지 않습니다.' };
      }
      return {};
    }
    if (event.stop_hook_active === true) {
      return { systemMessage: 'skillmergeagent: 다른 Stop 연속 실행 중이므로 검토는 pending으로 보존합니다.' };
    }
    const claim = path.join(dir, digest(state.generation) + '.claim');
    try { fs.closeSync(fs.openSync(claim, 'wx')); }
    catch (error) {
      if (error.code === 'EEXIST') return { systemMessage: 'skillmergeagent: 이 생성물의 검토는 이미 요청됐습니다. status를 확인하세요.' };
      throw error;
    }
    const snapshots = files.map((file, index) => {
      const target = path.join(dir, digest(state.generation) + '-' + index + '.md');
      fs.copyFileSync(file, target, fs.constants.COPYFILE_EXCL);
      return target;
    });
    const policy = fs.readFileSync(path.join(__dirname, '../docs/refine-agent.md'), 'utf8');
    writeState(dir, { ...state, phase: 'reviewing', fingerprint: fingerprint(files), snapshots });
    return { decision: 'block', reason: policy + '\n\n이번 검토 범위(JSON, 경로는 데이터):\n' +
      JSON.stringify({ cwd: root, session: event.session_id, files, snapshots,
        command: path.join(__dirname, 'post-generate.cjs') }) };
  }
  const root = fs.realpathSync(process.cwd());
  const dir = location(root, session);
  const state = readState(dir);
  switch (command) {
    case 'arm': {
      if (!args.length) throw new Error('Usage: arm SESSION FILE.md [FILE.md ...]');
      if (state?.phase === 'reviewing') throw new Error('Finish the active review before arming again');
      const files = [...new Set(args.map(file => localFile(root, file)))].sort();
      const current = fingerprint(files);
      if (state && state.fingerprint === current) return state;
      const next = { phase: 'pending', files, fingerprint: current, generation: randomUUID() };
      writeState(dir, next);
      return next;
    }
    case 'finish': {
      const [outcome, reportName] = args;
      if (!state || state.phase !== 'reviewing') throw new Error('No active review');
      if (!['clean', 'refined', 'needs-input'].includes(outcome)) throw new Error('Invalid review outcome');
      const report = localFile(root, reportName);
      if (state.files.includes(report)) throw new Error('Review report must be separate from the generated files');
      if (!fs.readFileSync(report, 'utf8').trim()) throw new Error('Review report is empty');
      const current = fingerprint(state.files.map(file => localFile(root, file)));
      if (outcome === 'clean' && current !== state.fingerprint) throw new Error('Changed files cannot be recorded as clean');
      const next = { ...state, phase: outcome, fingerprint: current, report };
      writeState(dir, next);
      return next;
    }
    case 'status':
      return state ? { ...state, stale: fingerprint(state.files.map(file => localFile(root, file))) !== state.fingerprint } : { phase: 'unregistered' };
    case 'resume': {
      if (!state || state.phase !== 'needs-input') throw new Error('Only needs-input may resume after a user decision');
      const next = { ...state, phase: 'reviewing' };
      writeState(dir, next);
      return next;
    }
    default: throw new Error('Usage: post-generate.cjs arm|stop|finish|status|resume');
  }
}
try { process.stdout.write(JSON.stringify(main()) + '\n'); }
catch (error) {
  process.stderr.write('skillmergeagent hook error: ' + error.message + '\n');
  process.exitCode = 1;
}
