"""No-model macOS Codex sandbox probe; uses only disposable synthetic fixtures."""
from pathlib import Path
import argparse, hashlib, json, os, signal, subprocess, sys, tempfile
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--codex', required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo / 'asdlc/00-governance/src'))
    from cli_baseline import resolve_codex, sandbox_settings, subprocess_environment
    if sys.platform != 'darwin':
        raise SystemExit('This native probe requires macOS Seatbelt.')
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    executable = resolve_codex(args.codex)
    results = {'started': datetime.now(timezone.utc).isoformat(), 'selected': args.codex,
               'resolved': executable, 'executable_sha256': hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
               'no_model': True, 'cases': []}
    with tempfile.TemporaryDirectory(prefix='asdg-native-probe-') as temporary, tempfile.TemporaryDirectory(
            prefix='.asdg-runtime-canary-', dir=args.repo.parent) as home_temporary:
        base = Path(temporary).resolve()
        work = base / 'workspace'
        for folder in ('output', 'source', 'context'):
            (work / folder).mkdir(parents=True)
        source = work / 'source/evidence.txt'
        source.write_text('synthetic source\n'); source.chmod(0o600)
        context = work / 'context/evidence.txt'
        context.write_text('synthetic context\n'); context.chmod(0o600)
        canary = Path(home_temporary) / 'unrelated-canary.txt'
        canary.write_text('synthetic unrelated canary\n'); canary.chmod(0o600)
        state = base / 'synthetic-codex-home'; state.mkdir()
        credential = state / 'auth.json'
        credential.write_text('{"synthetic":true}\n'); credential.chmod(0o600)
        env = subprocess_environment(); env['CODEX_HOME'] = str(state)
        settings = sandbox_settings(work, executable)
        results['filesystem_settings'] = settings
        results['fixtures'] = {'source_mode': oct(source.stat().st_mode & 0o777), 'canary': str(canary),
                               'synthetic_auth': str(credential), 'real_credentials_accessed': False}
        def run(name, command, allowed, profile=None, launcher=None):
            argv = [launcher or executable, 'sandbox', *(profile if profile is not None else settings),
                    '-P', 'asdg_baseline', '-C', str(work / 'output'), '--', *command]
            process = subprocess.Popen(argv, cwd=work / 'output', env=env, text=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            try:
                stdout, stderr = process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                stdout, stderr = process.communicate()
                stderr += '\nProbe timed out (not a successful denial).'
            passed = process.returncode == 0 if allowed else process.returncode != 0 and 'Operation not permitted' in stderr
            item = {'name': name, 'argv': argv, 'exit_code': process.returncode,
                    'expected': 'allowed' if allowed else 'sandbox denial', 'passed': passed,
                    'stdout': stdout, 'stderr': stderr}
            results['cases'].append(item)
            print(name, 'PASS' if passed else 'FAIL', 'exit', process.returncode, flush=True)
            (args.evidence_dir / 'native-probe.json').write_text(json.dumps(results, indent=2) + '\n')
        omitted = [value.replace(',' + json.dumps(executable) + '="read"', '') for value in settings]
        run('control-original-symlink-without-grant', [args.codex, '--version'], False, omitted, args.codex)
        run('resolved-runtime-version', [executable, '--version'], True)
        run('source-readable', ['/bin/cat', str(source)], True)
        run('source-overwrite-blocked', ['/bin/sh', '-c', 'printf changed > "$1"', 'probe', str(source)], False)
        run('source-create-blocked', ['/bin/sh', '-c', 'printf changed > "$1"', 'probe', str(source.parent / 'new.txt')], False)
        run('source-delete-blocked', ['/bin/rm', str(source)], False)
        run('context-overwrite-blocked', ['/bin/sh', '-c', 'printf changed > "$1"', 'probe', str(context)], False)
        output = work / 'output/result.txt'
        run('output-write-read', ['/bin/sh', '-c', 'printf produced > "$1" && /bin/cat "$1"', 'probe', str(output)], True)
        run('unrelated-home-canary-unreadable', ['/bin/sh', '-c', '/bin/cat "$1" >/dev/null', 'probe', str(canary)], False)
        run('synthetic-credential-unreadable', ['/bin/sh', '-c', '/bin/cat "$1" >/dev/null', 'probe', str(credential)], False)
        run('network-bind-blocked', ['/usr/bin/nc', '-l', '127.0.0.1', '0'], False)
        results['postconditions'] = {
            'source_unchanged': source.read_text() == 'synthetic source\n',
            'source_create_absent': not (source.parent / 'new.txt').exists(),
            'context_unchanged': context.read_text() == 'synthetic context\n',
            'output_written': output.read_text() == 'produced' if output.exists() else False,
            'canary_unchanged': canary.read_text() == 'synthetic unrelated canary\n',
            'synthetic_credential_unchanged': credential.read_text() == '{"synthetic":true}\n'}
        results['passed'] = all(c['passed'] for c in results['cases']) and all(results['postconditions'].values())
    results['finished'] = datetime.now(timezone.utc).isoformat()
    results['fixtures_cleaned'] = True
    (args.evidence_dir / 'native-probe.json').write_text(json.dumps(results, indent=2) + '\n')
    return 0 if results['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
