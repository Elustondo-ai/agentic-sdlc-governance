"""Local installer/project tests. Temporary HOME and Git repositories only."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / 'asdlc/00-governance/src'
sys.path.insert(0, str(SRC))
from cli_files import Conflict, apply, plan
from cli_install import MANIFEST, PATH_BLOCK, install, launcher, shell_files
from cli_model import ARTIFACTS, BINDING, CATALOG, COMMAND, PROVIDER, SHORT_COMMAND, catalogue, project_root, sha
from cli_project import BRIDGE, binding, initialize, inspect, merged_instructions


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='asdg tests ')
        self.base = Path(self.temp.name).resolve()
        self.provider = self.base / "tools with spaces/ASDLC 'repo'"
        (self.provider / CATALOG).parent.mkdir(parents=True)
        shutil.copyfile(REPO / CATALOG, self.provider / CATALOG)
        for relative in ('docs/status/lifecycle-baseline.md', 'asdlc/00-governance/types/lifecycle-rules.json'):
            destination = self.provider / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, destination)
        target_src = self.provider / 'asdlc/00-governance/src'
        target_src.mkdir()
        for source in SRC.glob('cli*.py'):
            shutil.copyfile(source, target_src / source.name)
        shutil.copyfile(REPO / 'asdg', self.provider / 'asdg')
        (self.provider / 'asdg').chmod(0o755)
        self.home = self.base / 'developer home'
        self.home.mkdir()
        self.project = self.base / 'other workspace/speaker coach'
        self.project.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        (self.project / 'app.py').write_text('print("untouched application")\n')
        self.env = dict(os.environ, HOME=str(self.home), SHELL='/bin/bash',
                        PATH=f'{Path(sys.executable).parent}:/usr/bin:/bin', PYTHONDONTWRITEBYTECODE='1')
        for variable in ('SUDO_USER', 'ZDOTDIR', 'BASH_ENV', 'ENV'):
            self.env.pop(variable, None)

    def tearDown(self):
        self.temp.cleanup()

    def setup_install(self, shell='/bin/bash'):
        return install(self.home, shell, self.env['PATH'], self.provider, Path(sys.executable))

    def run_cli(self, *args, cwd=None):
        return subprocess.run([str(self.home / '.local/bin/asdg'), *args],
                              cwd=cwd or self.project, env=self.env,
                              capture_output=True, text=True, timeout=20)


class InstallTests(Fixture):
    def test_root_asdg_install_executes_without_options(self):
        result = subprocess.run(['./asdg', 'install'], cwd=self.provider, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout,
                         'ALL GOOD! Elustondo.ai ASDLC installed successfully.\n'
                         'Next: open a new terminal, cd into your project, and run: asdg init\n')
        self.assertTrue(os.access(self.home / '.local/bin/asdg', os.X_OK))
        self.assertTrue((self.home / '.local/bin' / COMMAND).exists())

    def test_install_no_flags_required_and_extra_flags_rejected(self):
        result = subprocess.run(['./asdg', 'install', '--user'], cwd=self.provider, env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.home / '.local').exists())

    def test_non_executable_drive_copy_can_run_via_python(self):
        (self.provider / 'asdg').chmod(0o644)
        result = subprocess.run([sys.executable, 'asdg', 'install'], cwd=self.provider, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_install_is_idempotent(self):
        self.setup_install()
        self.assertEqual(self.setup_install()['files_changed'], [])
        self.assertEqual((self.home / '.bashrc').read_text().count(PATH_BLOCK), 1)

    def test_existing_shell_settings_preserved_and_backed_up(self):
        before = b'# developer settings\nexport EDITOR=vim\n'
        (self.home / '.bashrc').write_bytes(before)
        self.setup_install()
        self.assertTrue((self.home / '.bashrc').read_bytes().startswith(before))
        backups = list((self.home / '.config/elustondo-asdlc/backups').glob('*.before'))
        self.assertIn(before, [p.read_bytes() for p in backups])

    def test_new_shell_finds_cli_without_export_argument(self):
        self.setup_install()
        result = subprocess.run(['bash', '--noprofile', '--norc', '-c',
                                 '. "$HOME/.bashrc"; asdg --version'],
                                cwd=self.project, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(COMMAND, result.stdout)

    def test_zsh_startup_targets_and_syntax(self):
        self.setup_install('/bin/zsh')
        self.assertTrue((self.home / '.zprofile').exists())
        self.assertTrue((self.home / '.zshrc').exists())
        # Syntax/behavior of the POSIX PATH block, not a claim to run native zsh.
        result = subprocess.run(['bash', '-c', '. "$HOME/.zshrc"; asdg --version'],
                                cwd=self.project, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_zdotdir_inside_home(self):
        dot = self.home / 'zsh settings'
        result = install(self.home, '/bin/zsh', self.env['PATH'], self.provider,
                         Path(sys.executable), str(dot))
        self.assertTrue(result['files_changed'])
        self.assertTrue((dot / '.zshrc').exists())
        self.assertFalse((self.home / '.zshrc').exists())

    def test_existing_bash_login_file_chosen(self):
        (self.home / '.profile').write_text('# existing login\n')
        self.setup_install()
        self.assertFalse((self.home / '.bash_profile').exists())
        self.assertIn(PATH_BLOCK, (self.home / '.profile').read_text())

    def test_existing_asdg_collision_leaves_home_unchanged(self):
        binary = self.home / '.local/bin/asdg'
        binary.parent.mkdir(parents=True)
        binary.write_text('#!/bin/sh\necho other-tool\n')
        binary.chmod(0o755)
        with self.assertRaises(Conflict):
            self.setup_install()
        self.assertFalse((self.home / '.bashrc').exists())
        self.assertIn('other-tool', binary.read_text())

    def test_collision_elsewhere_on_path(self):
        external = self.base / 'foreign-bin'
        external.mkdir()
        (external / 'asdg').write_text('#!/bin/sh\nexit 0\n')
        (external / 'asdg').chmod(0o755)
        with self.assertRaises(Conflict):
            install(self.home, '/bin/bash', str(external), self.provider, Path(sys.executable))
        self.assertFalse((self.home / '.local').exists())

    def test_edited_owned_launcher_not_overwritten(self):
        self.setup_install()
        file = self.home / '.local/bin/asdg'
        file.write_text(file.read_text() + '# manual change\n')
        with self.assertRaises(Conflict):
            self.setup_install()
        self.assertIn('manual change', file.read_text())

    def test_modified_managed_path_block_rejected(self):
        self.setup_install()
        rc = self.home / '.bashrc'
        rc.write_text(rc.read_text().replace('export PATH=', 'export CUSTOM_PATH='))
        with self.assertRaises(Conflict):
            self.setup_install()

    def test_unsupported_shell_fails_before_changes(self):
        with self.assertRaises(Conflict):
            self.setup_install('/usr/bin/fish')
        self.assertFalse((self.home / '.local').exists())

    def test_symlink_shell_file_rejected(self):
        outside = self.base / 'do-not-edit'
        outside.write_text('keep\n')
        (self.home / '.bashrc').symlink_to(outside)
        with self.assertRaises(Conflict):
            self.setup_install()
        self.assertEqual(outside.read_text(), 'keep\n')

    def test_source_move_has_diagnostic_and_reinstall_recovers(self):
        self.setup_install()
        new = self.provider.with_name('moved provider')
        self.provider.rename(new)
        failure = self.run_cli('--version')
        self.assertEqual(failure.returncode, 1)
        self.assertIn('moved', failure.stderr)
        install(self.home, '/bin/bash', self.env['PATH'], new, Path(sys.executable))
        self.assertEqual(self.run_cli('--version').returncode, 0)

    def test_agent_listing_is_definition_inspection(self):
        self.setup_install()
        result = self.run_cli('agent', 'list', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(len(value['agents']), 13)
        self.assertFalse(value['live_invocation_tested'])


class ProjectTests(Fixture):
    def test_init_and_standalone_verify_have_concise_success_output(self):
        self.setup_install()
        for operation, message in (
                ('init', 'ASDLC initialized and verified.'),
                ('verify', 'ASDLC structure verified.'),
                ('init', 'ASDLC initialized and verified.')):
            result = self.run_cli(operation)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, message + '\nALL GOOD!\n')
            self.assertEqual(result.stderr, '')

    def test_init_verifies_after_writes_and_shares_verify_logic(self):
        import contextlib
        import io
        import cli
        missing = 'docs/asdlc/04-benchmarks-test-strategy-and-success-criteria'
        for operation in ('init', 'verify'):
            with self.subTest(operation=operation), \
                    patch('cli.project_root', return_value=self.project), \
                    patch('cli.initialize', return_value={'changed_files': []}) as init, \
                    patch('cli.inspect', return_value={'structure_ok': False, 'missing': [missing]}) as verify, \
                    contextlib.redirect_stdout(io.StringIO()) as output, \
                    contextlib.redirect_stderr(io.StringIO()) as errors:
                calls = []
                init.side_effect = lambda root: calls.append('init') or {'changed_files': []}
                verify.side_effect = lambda root: calls.append('verify') or {'structure_ok': False, 'missing': [missing]}
                self.assertEqual(cli.main([operation]), 1)
                self.assertEqual(calls, ['init', 'verify'] if operation == 'init' else ['verify'])
                verify.assert_called_once_with(self.project)
                self.assertEqual(output.getvalue(), '')
                self.assertIn('ERROR:', errors.getvalue())
                self.assertIn(missing, errors.getvalue())
                self.assertNotIn('ALL GOOD!', errors.getvalue())

    def test_standalone_verify_reports_removed_structure(self):
        self.setup_install()
        self.assertEqual(self.run_cli('init').returncode, 0)
        (self.project / 'AGENTS.md').unlink()
        result = self.run_cli('verify')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertIn('ASDLC verification failed.', result.stderr)
        self.assertIn('ERROR:', result.stderr)
        self.assertIn('AGENTS.md', result.stderr)

    def test_init_exception_reports_actionable_error(self):
        import contextlib
        import io
        import cli
        with patch('cli.project_root', return_value=self.project), \
                patch('cli.initialize', side_effect=Conflict('Cannot update AGENTS.md')), \
                patch('cli.inspect') as verify, \
                contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(cli.main(['init']), 1)
            verify.assert_not_called()
            self.assertIn('ASDLC initialization failed.\nERROR: Cannot update AGENTS.md', errors.getvalue())

    def test_init_generates_exact_catalogue_folders(self):
        report = initialize(self.project, self.provider)
        agents, _ = catalogue(self.provider)
        expected = sorted(Path(a['folder']).name for a in agents)
        actual = sorted(p.name for p in (self.project / ARTIFACTS).iterdir() if p.is_dir())
        self.assertEqual(actual, expected)
        self.assertEqual(report['semantic_compliance'], 'NOT_ASSESSED')
        self.assertFalse(report['sprint_started'])
        self.assertTrue((self.project / '.codex/hooks.json').is_file())
        self.assertFalse((self.project / 'asdlc').exists())

    def test_init_twice_is_no_op(self):
        initialize(self.project, self.provider)
        self.assertEqual(initialize(self.project, self.provider)['changed_files'], [])

    def test_verify_after_init_structural_pass(self):
        initialize(self.project, self.provider)
        report = inspect(self.project, self.provider)
        self.assertTrue(report['structure_ok'])
        self.assertEqual(report['semantic_compliance'], 'NOT_ASSESSED')

    def test_cli_preserves_calling_project_and_detects_nested_root(self):
        self.setup_install()
        nested = self.project / 'src/nested'
        nested.mkdir(parents=True)
        result = self.run_cli('init', '--json', cwd=nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['project_root'], str(self.project))
        self.assertTrue(json.loads(result.stdout)['structure_ok'])
        self.assertTrue((self.project / BINDING).exists())
        self.assertFalse((self.provider / BINDING).exists())
        self.assertFalse((nested / BINDING).exists())

    def test_application_and_git_control_files_unchanged(self):
        original = (self.project / 'app.py').read_bytes()
        git_before = {str(p.relative_to(self.project)): p.read_bytes()
                      for p in (self.project / '.git').rglob('*') if p.is_file()}
        initialize(self.project, self.provider)
        git_after = {str(p.relative_to(self.project)): p.read_bytes()
                     for p in (self.project / '.git').rglob('*') if p.is_file()}
        self.assertEqual(git_before, git_after)
        self.assertEqual(original, (self.project / 'app.py').read_bytes())

    def test_existing_content_and_approval_preserved(self):
        before = (b'AI-MODIFIED - 2026-01-01T00:00Z | PME-APPROVED - 2026-01-02T00:00Z\n\n'
                  b'# Project rules\nDo not alter application data.\n')
        (self.project / 'AGENTS.md').write_bytes(before)
        doc = self.project / ARTIFACTS / '02-intent/intent.md'
        doc.parent.mkdir(parents=True)
        doc.write_text('Real intent; do not replace.\n')
        initialize(self.project, self.provider)
        result = (self.project / 'AGENTS.md').read_text()
        self.assertIn('PME-APPROVED - 2026-01-02T00:00Z', result)
        self.assertIn('Do not alter application data.', result)
        self.assertIn(before, [p.read_bytes() for p in (self.project / '.asdlc/backups').glob('*.md')])
        self.assertEqual(doc.read_text(), 'Real intent; do not replace.\n')

    def test_foreign_metadata_refused_without_any_other_changes(self):
        foreign = self.project / BINDING
        foreign.parent.mkdir()
        foreign.write_text('{"provider":"other-vendor", "schema_version":1}')
        before = foreign.read_bytes()
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertEqual(foreign.read_bytes(), before)
        self.assertFalse((self.project / 'docs').exists())
        self.assertFalse((self.project / 'AGENTS.md').exists())

    def test_unknown_nonempty_metadata_directory_refused(self):
        (self.project / '.asdlc').mkdir()
        (self.project / '.asdlc/foreign.txt').write_text('other tool')
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)

    def test_symlink_in_project_path_refused(self):
        outside = self.base / 'external docs'
        outside.mkdir()
        (self.project / 'docs').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertFalse((self.project / BINDING).exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_yaml_front_matter_not_damaged(self):
        original = b'---\nname: app\n---\n# Instructions\n'
        (self.project / 'AGENTS.md').write_bytes(original)
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), original)
        self.assertFalse((self.project / BINDING).exists())

    def test_fifty_line_rule_blocks_overlong_merge(self):
        (self.project / 'AGENTS.md').write_text('# Existing rules\n' + 'Preserve me.\n' * 48)
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertFalse((self.project / BINDING).exists())

    def test_all_generated_markdown_at_most_fifty_lines(self):
        initialize(self.project, self.provider)
        for p in self.project.rglob('*.md'):
            self.assertLessEqual(len(p.read_text().splitlines()), 50, str(p))

    def test_catalogue_drift_not_silently_adopted(self):
        initialize(self.project, self.provider)
        path = self.provider / CATALOG
        path.write_text(path.read_text() + ' ')
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)

    def test_missing_stage_folder_repaired_without_overwriting_others(self):
        initialize(self.project, self.provider)
        target = self.project / ARTIFACTS / '02-intent'
        shutil.rmtree(target)
        self.assertFalse(inspect(self.project, self.provider)['structure_ok'])
        initialize(self.project, self.provider)
        self.assertTrue(inspect(self.project, self.provider)['structure_ok'])

    def test_broken_existing_bridge_not_overwritten(self):
        initialize(self.project, self.provider)
        file = self.project / 'AGENTS.md'
        file.write_text(file.read_text().replace('NoSuch', 'NoSuch').replace('stop and report', 'ignore'))
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)

    def test_binding_has_no_machine_specific_checkout_path(self):
        initialize(self.project, self.provider)
        text = (self.project / BINDING).read_text()
        self.assertNotIn(str(self.provider), text)
        self.assertNotIn(str(self.home), text)
        self.assertEqual(json.loads(text)['provider'], PROVIDER)

    def test_provider_cannot_be_initialized_as_application(self):
        subprocess.run(['git', 'init', '-q', str(self.provider)], check=True)
        with self.assertRaises(Conflict):
            project_root(self.provider, self.provider)

    def test_non_git_directory_not_implicitly_initialized(self):
        with self.assertRaises(Conflict):
            project_root(self.home, self.provider)
        self.assertFalse((self.home / '.git').exists())

    def test_verify_is_read_only(self):
        before = sorted(str(p) for p in self.project.rglob('*'))
        report = inspect(self.project, self.provider)
        self.assertFalse(report['initialized'])
        self.assertEqual(before, sorted(str(p) for p in self.project.rglob('*')))

    def test_preflight_conflicting_stage_file_leaves_no_scaffold(self):
        file = self.project / ARTIFACTS / '02-intent'
        file.parent.mkdir(parents=True)
        file.write_text('Existing file, not a directory.')
        with self.assertRaises(Conflict):
            initialize(self.project, self.provider)
        self.assertFalse((self.project / BINDING).exists())
        self.assertFalse((file.parent / '01-context-and-domain-analysis').exists())

    def test_apply_refuses_changed_snapshot(self):
        file = self.project / 'unchanged.txt'
        file.write_text('old')
        change = plan(self.project, file.name, b'new', replace=True)
        file.write_text('concurrent change')
        with self.assertRaises(Conflict):
            apply([change])
        self.assertEqual(file.read_text(), 'concurrent change')

    def test_write_failure_rolls_back_new_files(self):
        first = plan(self.project, 'new/one.txt', b'one')
        second = plan(self.project, 'new/two.txt', b'two')
        actual = os.open
        def fail_second(path, *args, **kwargs):
            if str(path).endswith('two.txt'):
                raise OSError('simulated write error')
            return actual(path, *args, **kwargs)
        with patch('cli_files.os.open', side_effect=fail_second):
            with self.assertRaises(OSError):
                apply([first, second])
        self.assertFalse((self.project / 'new').exists())


class RenameTests(Fixture):
    """The short CLI name changes; existing projects and foreign commands do not."""

    def test_new_short_name_and_qualified_name(self):
        self.assertEqual(SHORT_COMMAND, 'asdg')
        self.assertEqual(COMMAND, 'elustondo-asdlc')
        self.setup_install()
        record = json.loads((self.home / MANIFEST).read_text())
        self.assertEqual(record['commands'], ['elustondo-asdlc', 'asdg'])
        self.assertFalse((self.home / '.local/bin/asd').exists())

    def test_root_and_installed_help_use_new_name(self):
        self.setup_install()
        for command in ([str(self.provider / 'asdg'), '--help'],
                        [str(self.home / '.local/bin/asdg'), '--help']):
            result = subprocess.run(command, cwd=self.project, env=self.env,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('usage: asdg ', result.stdout)
            self.assertNotIn('usage: asd ', result.stdout)

    def test_foreign_old_asd_on_path_is_not_touched_or_blocked(self):
        foreign = self.base / 'foreign-bin'
        foreign.mkdir()
        file = foreign / 'asd'
        file.write_bytes(b'#!/bin/sh\nprintf "foreign tool\\n"\n')
        file.chmod(0o755)
        before = file.read_bytes()
        install(self.home, '/bin/bash', str(foreign) + ':' + self.env['PATH'],
                self.provider, Path(sys.executable))
        self.assertEqual(file.read_bytes(), before)
        self.assertEqual(self.run_cli('--version').returncode, 0)

    def test_upgrade_from_asd_keeps_old_command_and_uses_asdg(self):
        # Recreate the previous managed launcher and its exact hash contract.
        directory = self.home / '.local/bin'
        directory.mkdir(parents=True)
        old = launcher(self.provider, Path(sys.executable)).replace(
            b'rerun ./asdg install from its new location.', b'rerun its install script.')
        for name in (COMMAND, 'asd'):
            file = directory / name
            file.write_bytes(old)
            file.chmod(0o755)
        metadata = self.home / MANIFEST
        metadata.parent.mkdir(parents=True)
        metadata.write_text(json.dumps({'provider': PROVIDER, 'cli_version': '0.1.0',
            'commands': [COMMAND, 'asd'], 'launcher_sha256': sha(old)}))
        install(self.home, '/bin/bash', str(directory) + ':' + self.env['PATH'],
                self.provider, Path(sys.executable))
        self.assertEqual((directory / 'asd').read_bytes(), old)
        self.assertTrue(os.access(directory / 'asdg', os.X_OK))
        self.assertEqual(self.run_cli('--version').returncode, 0)
        self.assertEqual(json.loads(metadata.read_text())['commands'], [COMMAND, 'asdg'])
        self.assertEqual(self.setup_install()['files_changed'], [])

    def test_repository_launcher_preserves_external_working_directory(self):
        result = subprocess.run([str(self.provider / 'asdg'), 'init', '--json'],
                                cwd=self.project, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['project_root'], str(self.project))
        self.assertFalse((self.provider / BINDING).exists())

    def test_both_commands_share_one_implementation_and_binding(self):
        self.setup_install()
        result = self.run_cli('init', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        before = (self.project / BINDING).read_bytes()
        for name in ('asdg', COMMAND):
            result = subprocess.run([str(self.home / '.local/bin' / name), 'verify', '--json'],
                                    cwd=self.project, env=self.env,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['structure_ok'])
        self.assertEqual((self.project / BINDING).read_bytes(), before)
        self.assertIn(COMMAND, (self.project / 'AGENTS.md').read_text())

    def test_unknown_agent_error_names_asdg(self):
        self.setup_install()
        result = self.run_cli('agent', 'describe', 'not-a-role')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('run asdg agent list', result.stderr)
        self.assertNotIn('run asd ', result.stderr)

    def test_python_install_entry_point_still_works(self):
        result = subprocess.run([sys.executable, 'asdlc/00-governance/src/cli_install.py'], cwd=self.provider, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / '.local/bin/asdg').is_file())



class PythonCompatibilityTests(Fixture):
    """Version-policy mocks are not evidence of running an older interpreter."""

    def test_installer_version_gate_accepts_39_and_up(self):
        import contextlib
        import io
        import cli_install
        for version in ((3, 9, 0), (3, 9, 6), (3, 10, 0), (3, 13, 5)):
            with self.subTest(version=version):
                report = {'files_changed': [], 'checkout': str(self.provider)}
                with patch.object(sys, 'argv', ['cli_install.py']), \
                     patch.object(sys, 'version_info', version), \
                     patch.dict(os.environ, self.env, clear=True), \
                     patch('cli_install.install', return_value=report) as operation, \
                     contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(cli_install.main(), 0)
                    operation.assert_called_once()

    def test_installer_version_gate_rejects_38_before_writes(self):
        import contextlib
        import io
        import cli_install
        error = io.StringIO()
        with patch.object(sys, 'argv', ['cli_install.py']), \
             patch.object(sys, 'version_info', (3, 8, 20)), \
             patch('cli_install.install') as operation, \
             contextlib.redirect_stderr(error):
            self.assertEqual(cli_install.main(), 1)
            operation.assert_not_called()
        self.assertIn('Python 3.9 or newer', error.getvalue())
        self.assertFalse((self.home / '.local').exists())

    def test_python_entry_and_installed_launcher(self):
        text = (self.provider / 'asdg').read_text()
        self.assertTrue(text.startswith('#!/usr/bin/env python3\n'))
        self.assertIn('from cli import main', text)
        self.setup_install()
        installed = (self.home / '.local/bin/asdg').read_text()
        self.assertTrue(installed.startswith('#!/usr/bin/env python3\n'))
        self.assertNotIn('exec sh', installed)

    def test_cli_modules_parse_as_python39(self):
        import ast
        for source in SRC.glob('cli*.py'):
            ast.parse(source.read_text(), filename=str(source), feature_version=9)

    def test_cli_gate_applies_before_dispatch(self):
        import cli
        with patch.object(sys, 'version_info', (3, 8, 20)), patch('cli.initialize') as operation:
            self.assertEqual(cli.main(['init']), 1)
            operation.assert_not_called()

    def test_installer_refuses_sudo_before_writes(self):
        import cli_install
        with patch.dict(os.environ, {'SUDO_USER': 'someone'}), patch('cli_install.install') as operation:
            self.assertEqual(cli_install.main([]), 1)
            operation.assert_not_called()

if __name__ == '__main__':
    unittest.main()
