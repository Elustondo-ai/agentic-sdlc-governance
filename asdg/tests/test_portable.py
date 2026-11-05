"""End-to-end portable installation/guard regressions in disposable repositories."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

CORE = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(CORE / 'scripts/lib'))
from cli_files import apply, plan
from cli_runtime_env import subprocess_environment
from cli_advice import build_prompt
from cli_advice_report import save_advice
from distribution_files import package_files


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.area = tempfile.TemporaryDirectory(prefix='asdg-portable-')
        self.addCleanup(self.area.cleanup)
        self.root = Path(self.area.name) / 'client project'
        self.root.mkdir()
        for source in package_files(CORE):
            target = self.root / 'asdg' / source.relative_to(CORE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        self.seal_package()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / 'app.js').write_text('console.log("existing application");\n')
        (self.root / 'index.html').write_text('<script src="app.js"></script>\n')
        self.app = (self.root / 'app.js').read_bytes()

    def run_cli(self, *args, entry='cli.py', expect=0, cwd=None):
        result = subprocess.run([sys.executable, '-B', str(self.root / 'asdg/scripts' / entry), *args],
                                cwd=cwd or self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return result

    def seal_package(self):
        core = self.root / 'asdg'
        manifest = core / 'metadata/MANIFEST.json'
        value = json.loads(manifest.read_text())
        value['files'] = {p.relative_to(core).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in package_files(core) if p != manifest}
        manifest.write_text(json.dumps(value) + '\n')

    def init(self, *args, **kw):
        if '--dry-run' in args or kw.get('expect', 0):
            return self.run_cli(*args, entry='init.py', **kw)
        preview = self.run_cli(*args, '--dry-run', '--json', entry='init.py', **kw)
        token = json.loads(preview.stdout)['plan']
        return self.run_cli(*args, '--apply', '--plan', token, entry='init.py', **kw)

    def active(self):
        self.run_cli('sprint', 'start', '--id', 'S1', '--objective', 'One bounded behavior',
                     '--scope', 'app.js', '--acceptance', 'Existing behavior is retained')

    def hook(self, payload, event='PreToolUse', cwd=None, role='ASDG-09', context=None):
        config = json.loads((self.root / '.codex/hooks.json').read_text())
        command = config['hooks'][event][0]['hooks'][0]['command']
        if event == 'PreToolUse':
            payload = dict(payload, session_id='fixture-session')
        declared = context or {'role_id': role}
        env = dict(os.environ, ASDG_WRITE_CONTEXT=json.dumps(dict(declared, session_id='fixture-session')))
        result = subprocess.run(command, shell=True, input=json.dumps(payload), text=True, env=env,
                                cwd=cwd or self.root, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def payload(self, paths):
        command = '*** Begin Patch\n' + '\n'.join('*** Update File: ' + p + '\n@@\n-old\n+new' for p in paths) + '\n*** End Patch'
        return {'tool_name': 'apply_patch', 'cwd': str(self.root), 'tool_input': {'command': command}}

    def denied(self, payload):
        self.assertEqual(self.hook(payload)['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_dry_run_then_init_repeat_is_byte_identical(self):
        before = snapshot(self.root)
        self.init('--project-status', 'defining', '--dry-run')
        self.assertEqual(snapshot(self.root), before)
        self.init('--project-status', 'defining')
        after = snapshot(self.root)
        report = json.loads(self.init('--json').stdout)
        self.assertEqual(report['changed_files'], [])
        self.assertEqual(snapshot(self.root), after)
        self.assertEqual((self.root / 'app.js').read_bytes(), self.app)
        status = json.loads(self.run_cli('status', '--json').stdout)
        self.assertEqual((status['project_status'], status['release_status'], status['sprint_status']), ('defining', 'none', 'inactive'))
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.assertEqual(status['guard']['runtime_trust'], 'UNKNOWN')
        self.assertEqual(len(status['lifecycle_stages']), 12)
        self.assertEqual(status['current_stage']['number'], 1)
        from cli_status import context_is_empty
        for folder in (self.root / 'docs/asdg').glob('[0-1][0-9]-*'):
            document = (folder / 'README.md').read_text()
            self.assertIn('```mermaid', document)
            self.assertNotIn('SpeakerCoach', document)
            self.assertNotIn('Speaker Coach', document)
        self.assertTrue(context_is_empty(self.root, {'slug': '01-context-and-domain-analysis'}))
        context = self.root / 'docs/asdg/01-context-and-domain-analysis/README.md'
        context.write_text(context.read_text() + '\nExisting payroll integration requires review.\n')
        self.assertFalse(context_is_empty(self.root, {'slug': context.parent.name}))
        preserved = snapshot(self.root)
        self.init()
        self.assertEqual(snapshot(self.root), preserved)
        for stage in status['lifecycle_stages']:
            folder = self.root / 'docs/asdg' / stage['slug']
            for name in ('current', 'planned-release', 'planned-sprint'):
                self.assertFalse((folder / name).exists())
            self.assertFalse((folder / 'intended').exists())
            self.assertFalse((folder / 'planned').exists())

    def test_default_initial_state_new_and_no_later_redeclaration(self):
        self.init()
        before = snapshot(self.root)
        self.init('--project-status', 'defined', expect=1)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(json.loads(self.run_cli('status', '--json').stdout)['project_status'], 'new')

    def test_init_guidance_resolves_to_installed_status_without_changing_state_on_repeat(self):
        result = self.init()
        self.assertIn('Next, use /asdg-status in your project chat.', result.stdout)
        self.assertNotIn('/asdg-create-team', result.stdout.split('ASDG installation complete;', 1)[1])
        self.assertNotIn('Create my ASDG team', result.stdout)
        self.assertIn('This installation did not run Status, create team chats or start Context analysis', result.stdout)
        self.assertNotIn('Context survey', result.stdout)
        self.assertNotIn('$asdg-focus-', result.stdout)
        adapter = self.root / '.agents/skills/asdg-status/SKILL.md'
        self.assertTrue(adapter.is_file())
        self.assertEqual(adapter.read_bytes(),
                         (self.root / 'asdg/templates/.agents/skills/asdg-status/SKILL.md').read_bytes())
        before = snapshot(self.root)
        self.assertIn('Next, use /asdg-status in your project chat.', self.init().stdout)
        self.assertEqual(snapshot(self.root), before)
        status = json.loads(self.run_cli('status', '--json').stdout)
        self.assertEqual(status['project_status'], 'new')
        self.assertEqual(status['sprint_status'], 'inactive')
        self.assertEqual(status['implementation_permission'], 'BLOCKED')

    def test_init_guidance_is_only_emitted_after_successful_console_initialization(self):
        before = snapshot(self.root)
        self.assertNotIn('Next, use /asdg-status in your project chat.', self.init('--dry-run').stdout)
        self.assertEqual(snapshot(self.root), before)
        report = json.loads(self.init('--json').stdout)
        self.assertIsNone(report['human_approval'])
        self.assertFalse(report['sprint_started'])
        self.assertFalse(report['context_survey']['offered'])
        self.assertFalse(report['context_survey']['executed'])
        self.assertNotIn('$asdg-status', self.run_cli('verify').stdout)
        adapter = self.root / '.agents/skills/asdg-focus/SKILL.md'
        adapter.write_text(adapter.read_text() + '\nClient customization.\n')
        before = snapshot(self.root)
        self.assertNotIn('$asdg-status', self.init(expect=1).stdout)
        self.assertEqual(snapshot(self.root), before)

    def test_factual_entry_points_never_import_advice_or_mutate_initialized_project(self):
        self.init()
        before = snapshot(self.root)
        # An import trap proves these entry points never reach the SDK advice path.
        program = '''import importlib.abc, runpy, sys
class RejectAdvice(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('cli_advice', 'codex_sdk'):
            raise AssertionError('Unexpected model advice import: ' + fullname)
sys.meta_path.insert(0, RejectAdvice())
entry, *arguments = sys.argv[1:]
sys.argv = [entry, *arguments]
runpy.run_path(entry, run_name='__main__')
'''
        for entry, args in (('init.py', []), ('cli.py', ['status', '--facts-only']),
                            ('cli.py', ['status', '--json'])):
            result = subprocess.run([sys.executable, '-B', '-c', program,
                                     str(self.root / 'asdg/scripts' / entry), *args],
                                    cwd=self.root, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(snapshot(self.root), before)

    def test_shared_focus_preserves_unregistered_purpose_work(self):
        self.init()
        doc = self.root / 'docs/asdg/02-purpose/unregistered.md'
        doc.write_text('# Purpose\n\nHelp new staff complete their first shift independently.\n')
        before = snapshot(self.root)
        self.init()
        self.assertEqual(snapshot(self.root), before)
        relative = Path('.agents/skills/asdg-focus/SKILL.md')
        self.assertEqual((self.root / relative).read_bytes(),
                         (self.root / 'asdg/templates' / relative).read_bytes())
        self.assertTrue((self.root / 'asdg/02-purpose/skills/elicit-purpose/opening.md').is_file())
        self.assertTrue((self.root / 'asdg/00-governance/docs/continuation.md').is_file())
        status = json.loads(self.run_cli('status', '--json').stdout)
        purpose = next(s for s in status['lifecycle_stages'] if s['number'] == 2)
        self.assertEqual(purpose['artifacts'], [])
        self.assertEqual(doc.read_text().splitlines()[-1],
                         'Help new staff complete their first shift independently.')

    def test_single_focus_installs_without_changing_roles_or_authority(self):
        self.init()
        relative = Path('.agents/skills/asdg-focus')
        for name in ('SKILL.md', 'agents/openai.yaml'):
            self.assertEqual((self.root / relative / name).read_bytes(),
                             (self.root / 'asdg/templates' / relative / name).read_bytes())
        self.assertEqual([p.parent.name for p in (self.root / '.agents/skills').glob('asdg-focus*/SKILL.md')], ['asdg-focus'])
        self.assertEqual(len(list((self.root / '.codex/agents').glob('asdg*.toml'))), 13)
        status = json.loads(self.run_cli('status', '--json').stdout)
        self.assertEqual([s['number'] for s in status['lifecycle_stages']], list(range(1, 13)))
        self.assertEqual(status['sprint_status'], 'inactive')
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.run_cli('verify')
        before = snapshot(self.root)
        self.init()
        self.assertEqual(snapshot(self.root), before)

    def test_attitude_adapter_relocates_and_preserves_state(self):
        self.init()
        protected = {p: (self.root / p).read_bytes()
                     for p in ('.asdg/project.json', '.asdg/lifecycle.json', '.asdg/sprint.json', 'app.js')}
        before_move = snapshot(self.root)
        self.root = self.root.rename(self.root.parent / 'relocated attitude client')
        self.assertEqual(snapshot(self.root), before_move)
        relative = Path('.agents/skills/asdg-attitude')
        for name in ('SKILL.md', 'agents/openai.yaml'):
            self.assertEqual((self.root / relative / name).read_bytes(),
                             (self.root / 'asdg/templates' / relative / name).read_bytes())
        canonical = (self.root / relative / '../../../asdg/skills/asdg-attitude/SKILL.md').resolve()
        self.assertEqual(canonical, (self.root / 'asdg/skills/asdg-attitude/SKILL.md').resolve())
        self.assertTrue(canonical.is_file())
        for name in ('attitudes.md', 'TRY-IT.md'):
            self.assertTrue((canonical.parent / name).is_file())
        for name in ('session-state.md', 'subject-focus.md', 'rename-chat.md'):
            self.assertTrue((canonical.parent.parent / 'asdg-focus' / name).is_file())
        self.run_cli('verify', cwd=self.root / 'docs')
        before_repeat = snapshot(self.root)
        self.init(cwd=self.root / 'docs')
        self.assertEqual(snapshot(self.root), before_repeat)
        for path, data in protected.items():
            self.assertEqual((self.root / path).read_bytes(), data)
        self.assertEqual(len(list((self.root / '.codex/agents').glob('asdg*.toml'))), 13)

    def test_openspec_wrapper_preserves_upstream_and_relocates(self):
        native = self.root / '.agents/skills/openspec-propose/SKILL.md'
        native.parent.mkdir(parents=True)
        native.write_text('---\nname: openspec-propose\ndescription: Independent upstream fixture.\n---\n')
        config = self.root / 'openspec/config.yaml'
        config.parent.mkdir()
        config.write_text('schema: spec-driven\n')
        self.init()
        protected = {p: (self.root / p).read_bytes() for p in (
            '.agents/skills/openspec-propose/SKILL.md', 'openspec/config.yaml',
            '.asdg/project.json', '.asdg/lifecycle.json', '.asdg/sprint.json',
            '.codex/hooks.json', 'app.js')}
        self.root = self.root.rename(self.root.parent / 'relocated proposal client')
        relative = Path('.agents/skills/asdg-openspec-propose')
        for name in ('SKILL.md', 'agents/openai.yaml'):
            self.assertEqual((self.root / relative / name).read_bytes(),
                             (self.root / 'asdg/templates' / relative / name).read_bytes())
        canonical = (self.root / relative / '../../../asdg/skills/asdg-openspec-propose/SKILL.md').resolve()
        self.assertEqual(canonical, (self.root / 'asdg/skills/asdg-openspec-propose/SKILL.md').resolve())
        self.assertTrue(canonical.is_file())
        self.run_cli('verify', cwd=self.root / 'docs')
        before = snapshot(self.root)
        self.init(cwd=self.root / 'docs')
        self.assertEqual(snapshot(self.root), before)
        for path, data in protected.items():
            self.assertEqual((self.root / path).read_bytes(), data)
        self.assertFalse((self.root / 'openspec/changes').exists())

    def test_gui_visual_rule_is_shared_by_all_role_entry_points(self):
        self.init()
        self.root = self.root.rename(self.root.parent / 'relocated gui client')
        docs = self.root / 'asdg/00-governance/docs'
        rule = (docs / 'gui-visuals.md').read_text()
        self.assertIn('every adopting project, governance, all twelve specialists', rule)
        self.assertTrue((docs / 'images/gui-visuals.svg').is_file())
        referrers = ('asdg/AGENTS.md', 'asdg/00-governance/docs/documentation-standard.md',
                     'asdg/00-governance/docs/documentation-review.md',
                     'asdg/00-governance/docs/runtime-contract.md',
                     'asdg/skills/asdg-documentation/SKILL.md')
        for path in referrers:
            source = self.root / path
            links = re.findall(r'\]\(([^)]*gui-visuals\.md)\)', source.read_text())
            self.assertTrue(links, path)
            for link in links:
                self.assertEqual((source.parent / link).resolve(), (docs / 'gui-visuals.md').resolve())
        self.assertIn('asdg/AGENTS.md', (self.root / 'AGENTS.md').read_text())

    def test_new_session_bootstrap_reports_governance_default_ready(self):
        self.init()
        session = json.loads(self.run_cli('status', '--json').stdout)['session_governance']
        self.assertEqual((session['default_role'], session['native_name'], session['status']),
                         ('ASDG-COORDINATOR', 'asdg_coordinator', 'READY'))
        self.assertFalse(session['role_none_permitted'])
        self.assertEqual(session['enforcement'], 'INSTRUCTIONAL_ONLY')
        self.assertTrue((self.root / 'AGENTS.md').read_text().startswith('<!-- ASDG:BEGIN bootstrap-v2 -->\n## ASDG bootstrap\n'))
        self.assertIn('00 Governance by default', (self.root / 'asdg/AGENTS.md').read_text())
        self.assertIn('Session role: 00 Governance by default (READY)', self.run_cli('status', '--facts-only').stdout)

    def test_missing_governance_source_blocks_bootstrap_and_implementation(self):
        self.init()
        self.active()
        self.run_cli('sprint', 'check-implementation', '--path', 'app.js')
        (self.root / 'asdg/00-governance/types/contract.md').unlink()
        status = json.loads(self.run_cli('status', '--json', expect=1).stdout)
        session = status['session_governance']
        self.assertEqual((session['status'], session['blocked_code']), ('BLOCKED', 'GOVERNANCE_BOOTSTRAP'))
        self.assertEqual(session['missing'], ['asdg/00-governance/types/contract.md: required governance source missing'])
        self.assertIn('Governance bootstrap: ' + session['missing'][0], status['errors'])
        self.assertEqual(status['implementation_permission'], 'BLOCKED')
        self.run_cli('sprint', 'check-implementation', '--path', 'app.js', expect=1)
        payload = {'tool_name': 'apply_patch', 'tool_input': {'command':
                   '*** Begin Patch\n*** Update File: app.js\n@@\n-console.log("existing application");\n+x\n*** End Patch\n'}}
        self.assertEqual(self.hook(payload)['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_entry_point_without_distribution_link_blocks_bootstrap(self):
        self.init()
        agents = self.root / 'AGENTS.md'
        managed = agents.read_text()
        # An edited block without the link, or a removed block whose project text mentions the file, both fail.
        for text in (managed.replace('`asdg/AGENTS.md`', 'the methodology'), 'Project notes: read asdg/AGENTS.md first.\n'):
            agents.write_text(text)
            session = json.loads(self.run_cli('status', '--json', expect=1).stdout)['session_governance']
            self.assertEqual(session['status'], 'BLOCKED')
            self.assertIn('AGENTS.md: client entry point does not load asdg/AGENTS.md', session['missing'])

    def bootstrap_module(self):
        sys.path.insert(0, str(self.root / 'asdg/scripts/lib'))
        self.addCleanup(sys.path.remove, str(self.root / 'asdg/scripts/lib'))
        import cli_project
        return cli_project

    def test_known_legacy_blocks_move_first_and_keep_project_text(self):
        cli = self.bootstrap_module()
        self.init()
        agents = self.root / 'AGENTS.md'
        project = '# Team rules\n\nKeep the build green.\n'
        self.assertEqual(len(cli.LEGACY_BRIDGES), 3)
        for legacy in cli.LEGACY_BRIDGES:
            cases = ((project + '\n' + legacy, cli.BRIDGE + '\n' + project),  # appended by an older setup
                     (legacy, cli.BRIDGE),  # an older fresh install
                     (project + '\n' + legacy + '\nLater note.\n', cli.BRIDGE + '\n' + project + '\nLater note.\n'))
            for old, expected in cases:
                agents.write_text(old)
                self.run_cli('verify', expect=1)
                self.init()
                self.assertEqual(agents.read_text(), expected)
                self.assertIn(old, [b.read_text() for b in (self.root / '.asdg/backups').glob('AGENTS-before-*.md')])
                before = snapshot(self.root)
                self.init()
                self.assertEqual(snapshot(self.root), before)
                self.run_cli('verify')

    def test_project_text_after_bootstrap_is_preserved_byte_for_byte(self):
        cli = self.bootstrap_module()
        project = b'# Client notes\r\n\r\nTabs\tand trailing spaces stay.  \n\xc3\xa9t\xc3\xa9\n'
        (self.root / 'AGENTS.md').write_bytes(project)
        self.init()
        body = (self.root / 'AGENTS.md').read_bytes()
        self.assertEqual(body, cli.BRIDGE.encode() + b'\n' + project)
        extended = body + b'\n## More project guidance\nStill project-owned.\n'
        (self.root / 'AGENTS.md').write_bytes(extended)
        self.run_cli('verify')
        before = snapshot(self.root)
        self.init()
        self.init()
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual((self.root / 'AGENTS.md').read_bytes(), extended)

    def test_edited_moved_or_duplicated_bootstrap_conflicts_without_writes(self):
        cli = self.bootstrap_module()
        (self.root / 'AGENTS.md').write_text('# Project\n')
        self.init()
        agents = self.root / 'AGENTS.md'
        good = agents.read_text()
        self.assertEqual(good, cli.BRIDGE + '\n# Project\n')
        for text in (good.replace('stop dependent work', 'continue anyway'),
                     '# Project\n\n' + cli.BRIDGE,
                     good + '\n' + cli.BRIDGE,
                     '# Project\n\n' + cli.LEGACY_BRIDGES[0].replace('Preserve', 'Keep')):
            agents.write_text(text)
            before = snapshot(self.root)
            result = self.init(expect=1)
            self.assertIn('Edited, moved or incomplete ASDG bootstrap', result.stdout + result.stderr)
            self.assertEqual(snapshot(self.root), before)
            self.run_cli('verify', expect=1)
        agents.write_text(good)
        self.run_cli('verify')

    def test_bootstrap_template_is_generic_and_removed_rules_have_homes(self):
        cli = self.bootstrap_module()
        self.assertLessEqual(sum(1 for line in cli.BRIDGE.splitlines() if line.strip()), 8)
        for phrase in ('read and follow `asdg/AGENTS.md`', 'every startup source', 'read-only diagnosis stays allowed'):
            self.assertIn(phrase, cli.BRIDGE)
        self.assertNotRegex(cli.BRIDGE.lower(), 'speakercoach|speaker coach|pablo')
        entry = (CORE / 'AGENTS.md').read_text()
        for link in ('skills/asdg-focus/session-policy.md', 'skills/asdg-focus/session-state.md',
                     '00-governance/docs/runtime-contract.md', '00-governance/AGENTS.md',
                     '00-governance/docs/sprint-gate.md', '00-governance/docs/documentation-authority.md', 'admin/AGENTS.md'):
            self.assertIn(f']({link})', entry)
            self.assertTrue((CORE / link).is_file(), link)
        homes = {
            CORE / 'AGENTS.md': [
                'session-policy.md), again on every turn', '00 Governance by default', 'BLOCKED: GOVERNANCE_BOOTSTRAP',
                'read-only diagnosis stays allowed', 'In initialized clients, run `python3 asdg/scripts/cli.py status --json` before substantial work',
                'In the canonical provider, follow its root maintenance and package checks instead', '`python3 asdg/scripts/cli.py verify` checks structure only',
                'sprint check-implementation --path <target>', "a sprint never widens a role's authority",
                'hook definitions or ASDG policies', 'Codex hooks enforce nothing until a human reviews and trusts them',
                'grant no approval, publication, commit, push, deletion, deployment or hook trust',
                'run only under explicitly selected [ASDG Admin]', 'preserving both'],
            CORE / '00-governance/docs/sprint-gate.md': [
                'Scope is an exact repository-relative file or directory ending in `/`', 'meet its acceptance criteria',
                'a coding task alone implies neither', 'Use scoped apply_patch', 'It blocks arbitrary',
                'Protected agent-policy/state paths cannot be scope', 'Project hooks run ONLY after'],
            CORE / '00-governance/docs/runtime-contract.md': [
                'only its bounded documentation-review recording workflow', 'python3 asdg/scripts/cli.py sprint check-implementation'],
            CORE / '00-governance/docs/documentation-authority.md': ['default way agents communicate'],
            CORE / 'skills/asdg-focus/session-policy.md': ['NEVER selects or clears these fields', 'Never use a shared ACTIVE_ROLE file'],
            CORE / '00-governance/AGENTS.md': ['[runtime rules](docs/runtime-contract.md)'],
        }
        for path, phrases in homes.items():
            text = path.read_text()
            for phrase in phrases:
                self.assertIn(phrase, text, f'{path}: {phrase}')

    def test_admin_role_is_registered_outside_the_lifecycle(self):
        registration = json.loads((CORE / 'admin/types/admin-role.json').read_text())
        self.assertEqual((registration['role_id'], registration['title'], registration['lifecycle_stage'],
                          registration['default'], registration['native_adapter']),
                         ('ASDG-ADMIN', 'ASDG Admin', None, False, None))
        self.assertEqual(registration['activation'], 'explicit-human-selection-only')
        for key in ('entry', 'contract', 'skill'):
            self.assertTrue((CORE.parent / registration[key]).is_file(), key)
        catalogue = json.loads((CORE / '00-governance/types/agent-catalog.json').read_text())
        self.assertEqual(len(catalogue['agents']), 13)
        self.assertNotIn('ASDG-ADMIN', json.dumps(catalogue))
        self.init()
        self.assertFalse(list((self.root / '.codex/agents').glob('*admin*')))
        self.assertIn('admin/types/admin-role.json', (CORE / 'skills/asdg-focus/focus-choices.md').read_text())

    def test_admin_skill_installs_relocates_and_is_explicit_only(self):
        self.init()
        self.root = self.root.rename(self.root.parent / 'relocated admin skill client')
        relative = Path('.agents/skills/asdg-admin')
        for name in ('SKILL.md', 'agents/openai.yaml'):
            self.assertEqual((self.root / relative / name).read_bytes(),
                             (self.root / 'asdg/templates' / relative / name).read_bytes())
        self.assertIn('allow_implicit_invocation: false', (self.root / relative / 'agents/openai.yaml').read_text())
        canonical = (self.root / relative / '../../../asdg/skills/asdg-admin/SKILL.md').resolve()
        self.assertEqual(canonical, (self.root / 'asdg/skills/asdg-admin/SKILL.md').resolve())
        text = canonical.read_text()
        for phrase in ('only when the human explicitly invokes `$asdg-admin`', 'Never invoke it on your own initiative',
                       'Selection authorizes no change', 'returns to 00 Governance', 'that list is authoritative'):
            self.assertIn(phrase, text)
        for link in re.findall(r'\]\(([^)#]+)\)', text):
            self.assertTrue((canonical.parent / link).resolve().is_file(), link)
        self.assertIn('$asdg-admin', json.loads((self.root / 'asdg/admin/types/admin-role.json').read_text())['selectors'])
        self.assertIn('[Admin](asdg-admin/SKILL.md)', (self.root / 'asdg/skills/README.md').read_text())
        self.run_cli('verify', cwd=self.root / 'docs')
        before = snapshot(self.root)
        self.init(cwd=self.root / 'docs')
        self.assertEqual(snapshot(self.root), before)

    def fresh_client(self, name):
        self.root = Path(self.area.name) / name
        self.root.mkdir()
        shutil.copytree(CORE, self.root / 'asdg', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.seal_package()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / 'app.js').write_text('console.log("existing application");\n')

    def integrations(self):
        return json.loads((self.root / '.asdg/integrations.json').read_text())['clients']

    def statuses(self, expect=0):
        report = json.loads(self.run_cli('verify', '--json', expect=expect).stdout)
        return {name: item['status'] for name, item in report['integrations'].items()}

    def test_fresh_setup_installs_only_the_selected_clients(self):
        for choice, expected in (('codex', {'codex'}), ('claude', {'claude'}), ('both', {'codex', 'claude'})):
            self.fresh_client(f'fresh {choice}')
            self.init('--client', choice)
            self.assertEqual(set(self.integrations()), expected)
            self.assertEqual((self.root / '.codex').exists(), 'codex' in expected)
            self.assertEqual((self.root / '.agents').exists(), 'codex' in expected)
            self.assertEqual((self.root / '.claude/skills').is_dir(), 'claude' in expected)
            self.assertFalse((self.root / 'CLAUDE.md').exists())
            self.assertEqual(self.statuses(), {n: 'COMPLETE' if n in expected else 'NOT_SELECTED' for n in ('codex', 'claude')})
            guard = json.loads(self.run_cli('status', '--json').stdout)['guard']['configuration']
            self.assertEqual(guard, 'PRESENT' if 'codex' in expected else 'NOT_INSTALLED')

    def test_clients_add_in_either_order_without_touching_the_other(self):
        prefixes = {'codex': ('.codex/', '.agents/'), 'claude': ('.claude/',)}
        for first, second in (('codex', 'claude'), ('claude', 'codex')):
            self.fresh_client(f'{first} then {second}')
            self.init('--client', first)
            kept = {k: v for k, v in snapshot(self.root).items() if k.startswith(prefixes[first])}
            self.assertTrue(kept)
            self.init('--client', second)
            after = snapshot(self.root)
            self.assertEqual({k: after[k] for k in kept}, kept)
            self.assertEqual(self.integrations()[first], {'recorded_from': f'--client {first}'})
            self.assertEqual(set(self.integrations()), {'codex', 'claude'})
            self.assertEqual(self.statuses(), {'codex': 'COMPLETE', 'claude': 'COMPLETE'})

    def test_repeat_setup_and_dry_run_create_nothing_new(self):
        for choice, expected in (('codex', {'codex'}), ('claude', {'claude'}), ('both', {'codex', 'claude'})):
            self.fresh_client(f'repeat {choice}')
            before = snapshot(self.root)
            self.init('--client', choice, '--dry-run')
            self.assertEqual(snapshot(self.root), before)
            self.init('--client', choice)
            first = snapshot(self.root)
            for args in (('--client', choice), (), ('--client', choice, '--dry-run')):
                self.init(*args)
                self.assertEqual(snapshot(self.root), first, args)
            self.assertEqual(set(self.integrations()), expected)
            events = json.loads((self.root / '.asdg/document-reviews.json').read_text())['events']
            self.assertEqual(len(events), len({(e['path'], e['sha256']) for e in events}))

    def test_invalid_client_is_rejected_before_any_write(self):
        before = snapshot(self.root)
        result = self.init('--client', 'cursor', expect=2)
        self.assertIn('invalid choice', result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_edited_client_files_conflict_and_verify_names_the_damaged_client(self):
        self.init('--client', 'both')
        claude = self.root / '.claude/skills/asdg-admin/SKILL.md'
        original = claude.read_bytes()
        claude.write_text(claude.read_text().replace('disable-model-invocation: true\n', ''))
        before = snapshot(self.root)
        result = self.init('--client', 'claude', expect=1)
        self.assertIn('Refusing to overwrite existing file', result.stdout + result.stderr)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(self.statuses(expect=1), {'codex': 'COMPLETE', 'claude': 'DAMAGED'})
        claude.write_bytes(original)
        codex = self.root / '.agents/skills/asdg-focus/SKILL.md'
        codex.write_text(codex.read_text() + 'Local change.\n')
        self.assertEqual(self.statuses(expect=1), {'codex': 'DAMAGED', 'claude': 'COMPLETE'})

    def test_codex_and_claude_adapters_resolve_the_same_canonical_skills_after_relocation(self):
        self.init('--client', 'both')
        self.root = self.root.rename(self.root.parent / 'relocated two-client project')
        names = sorted(p.parent.name for p in (self.root / 'asdg/templates/.agents/skills').glob('*/SKILL.md'))
        self.assertGreaterEqual(len(names), 16)
        for name in names:
            targets = set()
            for folder in ('.agents/skills', '.claude/skills'):
                adapter = self.root / folder / name / 'SKILL.md'
                link = re.search(r'\]\(([^)]*asdg/skills/[^)]+)\)', adapter.read_text()).group(1)
                targets.add((adapter.parent / link).resolve())
            self.assertEqual(targets, {(self.root / 'asdg/skills' / name / 'SKILL.md').resolve()}, name)
        self.run_cli('verify', cwd=self.root / 'docs')

    def test_claude_invocation_controls_mirror_the_codex_policy(self):
        self.init('--client', 'both')
        explicit = set()
        for adapter in (self.root / '.claude/skills').glob('*/SKILL.md'):
            name = adapter.parent.name
            policy = self.root / '.agents/skills' / name / 'agents/openai.yaml'
            codex_explicit = policy.is_file() and 'allow_implicit_invocation: false' in policy.read_text()
            front = adapter.read_text().split('---\n')[1]
            self.assertTrue(front.startswith(f'name: {name}\ndescription: '), name)
            self.assertEqual('disable-model-invocation: true' in front, codex_explicit, name)
            self.assertNotIn('user-invocable', front)
            if codex_explicit:
                explicit.add(name)
        self.assertTrue({'asdg-admin', 'asdg-focus', 'asdg-init', 'asdg-status'} <= explicit)

    def test_legacy_codex_installation_is_recorded_explicitly(self):
        self.init()
        (self.root / '.asdg/integrations.json').unlink()  # an installation made before client tracking
        report = json.loads(self.run_cli('verify', '--json').stdout)['integrations']
        self.assertEqual((report['codex']['selection'], report['codex']['status']), ('legacy-unrecorded', 'COMPLETE'))
        self.assertEqual(report['claude']['status'], 'NOT_SELECTED')
        codex = {k: v for k, v in snapshot(self.root).items() if k.startswith(('.codex/', '.agents/'))}
        result = self.init('--client', 'claude')
        self.assertIn('NOTE: Recorded the existing Codex integration from a legacy installation', result.stdout)
        self.assertEqual(self.integrations(), {'claude': {'recorded_from': '--client claude'},
                                               'codex': {'recorded_from': 'legacy installation'}})
        after = snapshot(self.root)
        self.assertEqual({k: after[k] for k in codex}, codex)

    def test_claude_bridge_is_added_only_when_claude_md_would_hide_agents_md(self):
        # Assumes no CLAUDE.md in the fixture's parent folders, which would itself require the bridge.
        self.init('--client', 'claude')
        self.assertFalse((self.root / 'CLAUDE.md').exists())
        notes = '# Team Claude notes\nUse plan mode.\n'
        (self.root / 'CLAUDE.md').write_text(notes)
        self.assertEqual(self.statuses(expect=1)['claude'], 'DAMAGED')
        self.init('--client', 'claude')
        block = '<!-- ASDG:BEGIN claude-bridge-v1 -->\n@AGENTS.md\n<!-- ASDG:END claude-bridge -->\n'
        self.assertEqual((self.root / 'CLAUDE.md').read_text(), block + '\n' + notes)
        self.assertIn(notes, [b.read_text() for b in (self.root / '.asdg/backups').glob('CLAUDE-before-*.md')])
        before = snapshot(self.root)
        self.init('--client', 'claude')
        self.init()
        self.assertEqual(snapshot(self.root), before)
        (self.root / 'CLAUDE.md').write_text('@AGENTS.md\n\n' + notes)  # the user's own import is kept
        before = snapshot(self.root)
        self.init('--client', 'claude')
        self.assertEqual(snapshot(self.root), before)
        (self.root / 'CLAUDE.md').write_text((block + '\n' + notes).replace('@AGENTS.md', '@OTHER.md'))
        before = snapshot(self.root)
        result = self.init('--client', 'claude', expect=1)
        self.assertIn('Edited, moved or duplicated ASDG Claude bridge', result.stdout + result.stderr)
        self.assertEqual(snapshot(self.root), before)
        (self.root / 'CLAUDE.md').unlink()
        (self.root / '.claude/CLAUDE.md').write_text(notes)
        self.init('--client', 'claude')
        self.assertTrue((self.root / '.claude/CLAUDE.md').read_text().startswith(block.replace('@AGENTS.md', '@../AGENTS.md')))
        self.assertFalse((self.root / 'CLAUDE.md').exists())
        (self.root / '.claude/CLAUDE.md').unlink()
        (self.root / 'CLAUDE.local.md').write_text('Personal notes.\n')
        self.init('--client', 'claude')
        self.assertEqual((self.root / 'CLAUDE.md').read_text(), block)
        self.assertEqual((self.root / 'CLAUDE.local.md').read_text(), 'Personal notes.\n')
        self.assertEqual(self.statuses()['claude'], 'COMPLETE')

    def test_project_work_cannot_patch_asdg_rules_through_the_guard(self):
        # Role-agnostic: the guard knows paths and sprint scope, not which role a session claims.
        self.init()
        self.active()
        rule = 'asdg/skills/asdg-focus/session-policy.md'
        payload = {'tool_name': 'apply_patch', 'cwd': str(self.root), 'tool_input': {'command':
                   f'*** Begin Patch\n*** Update File: {rule}\n@@\n-# ASDG\n+# Edited\n*** End Patch\n'}}
        self.assertEqual(self.hook(payload)['hookSpecificOutput']['permissionDecision'], 'deny')
        self.run_cli('sprint', 'check-implementation', '--path', rule, expect=1)
        sys.path.insert(0, str(self.root / 'asdg/scripts/lib'))
        self.addCleanup(sys.path.remove, str(self.root / 'asdg/scripts/lib'))
        from cli_files import Conflict
        from cli_sprint import relative_path
        with self.assertRaisesRegex(Conflict, 'policy paths cannot be implementation scope'):
            relative_path(self.root, 'asdg/')

    def test_session_instructions_define_no_role_none_path(self):
        # Documentation consistency only: conversation role state has no runtime enforcement.
        skills = CORE / 'skills'
        required = {
            CORE / 'AGENTS.md': ['00 Governance by default'],
            CORE / '00-governance/AGENTS.md': ['by default in every ASDG session', 'never inherits a specialist'],
            skills / 'asdg-focus/session-policy.md': ['There is no role None', 'GOVERNANCE_BOOTSTRAP',
                                                      'returns the role to 00 Governance', 'Preserve a valid recovered role',
                                                      'gains no specialist delivery or implementation authority'],
            skills / 'asdg-focus/session-state.md': ['Never None', 'record role Unknown'],
            skills / 'asdg-focus/SKILL.md': ['return the role to 00 Governance', 'there is no role None'],
            skills / 'asdg-focus/subject-focus.md': ['return the role to 00 Governance'],
            skills / 'asdg-status/SKILL.md': ['the role is the default 00 Governance'],
            skills / 'asdg-focus/focus-choices.md': ['returns to 00 Governance', 'never selects it'],
            skills / 'asdg-focus/rename-chat.md': ['a new session starting under 00 Governance', 'a legacy role None migrating',
                                                   'a clear returning to it', 'including ASDG Admin', 'set_session_title'],
            CORE / 'admin/AGENTS.md': ['explicit, visible human selection', 'it does not authorize any change',
                                       'never to remove a restriction'],
        }
        required[skills / 'asdg-focus/session-policy.md'] += ['no agent selects Admin itself', 'new-session Governance start',
                                                              'legacy None migration', 'clear to Governance']
        required[CORE / 'AGENTS.md'] += ['run only under explicitly selected [ASDG Admin]']
        for entry in CORE.glob('[01][0-9]-*/AGENTS.md'):
            required.setdefault(entry, []).append('ASDG Admin')
        for path, phrases in required.items():
            text = path.read_text()
            for phrase in phrases:
                self.assertIn(phrase, text, path)
        forbidden = re.compile(r'role None,|starts with role None|begins with role None|selects role None|'
                               r'means None, not Governance|displays `General`|clear only the role|under general assistance|'
                               r'A maintainer follows root instructions|maintainers follow the explicit maintenance|'
                               r"runs under the session's accountable role|removes selection without selecting Governance|"
                               r'general assistance under root instructions|distinct from None|an implementation gate in AGENTS|'
                               r'Package maintenance follows root instructions|governance remains distinct from no focus')
        for path in package_files(CORE):
            if path.suffix == '.md' and 'proposals' not in path.parts:
                self.assertIsNone(forbidden.search(path.read_text()), path)

    def test_decision_skill_relocates_and_preserves_unregistered_decisions(self):
        self.init()
        relative = Path('.agents/skills/asdg-decision')
        for name in ('SKILL.md', 'agents/openai.yaml'):
            self.assertEqual((self.root / relative / name).read_bytes(),
                             (self.root / 'asdg/templates' / relative / name).read_bytes())
        canonical = (self.root / relative / '../../../asdg/skills/asdg-decision/SKILL.md').resolve()
        self.assertEqual(canonical, (self.root / 'asdg/skills/asdg-decision/SKILL.md').resolve())
        self.assertTrue(canonical.is_file())
        self.assertTrue((canonical.parent / 'record-format.md').is_file())
        self.assertTrue((self.root / 'asdg/05-high-level-design-and-architecture/docs/architectural-decisions.md').is_file())
        decisions = self.root / 'docs/asdg/05-high-level-design-and-architecture/decisions'
        self.assertFalse(decisions.exists())
        doc = decisions / 'Keep session state local' / 'README.md'
        doc.parent.mkdir(parents=True)
        doc.write_text('# Keep session state local\n\nProposed; evidence remains incomplete.\n')
        protected = {p: (self.root / p).read_bytes()
                     for p in ('.asdg/project.json', '.asdg/lifecycle.json', '.asdg/sprint.json')}
        before = snapshot(self.root)
        self.init(cwd=self.root / 'docs')
        self.assertEqual(snapshot(self.root), before)
        for p, data in protected.items():
            self.assertEqual((self.root / p).read_bytes(), data)
        self.assertEqual((self.root / 'app.js').read_bytes(), self.app)
        self.assertFalse((decisions / 'Use Open AI Agent SDK').exists())

    def test_optional_decision_specialization_preserves_generic_roles_and_local_methods(self):
        self.init()
        catalogue = json.loads((self.root / 'asdg/00-governance/types/agent-catalog.json').read_text())
        roles = {row['stage']: row for row in catalogue['agents']}
        architecture = self.root / roles[5]['folder'] / 'skills/decision/SKILL.md'
        generic_role = self.root / roles[4]['folder'] / 'skills/decision/SKILL.md'
        self.assertTrue(architecture.is_file())
        self.assertFalse(generic_role.exists())
        self.run_cli('verify', cwd=self.root / 'docs')
        protected = {p: (self.root / p).read_bytes()
                     for p in ('.asdg/project.json', '.asdg/lifecycle.json', '.asdg/sprint.json', 'app.js')}
        generic_role.parent.mkdir(parents=True)
        generic_role.write_text('---\nname: decision\ndescription: Evaluate a benchmark choice.\n---\n\n'
                                '# Benchmark decision\n\nCompare representativeness and reproducibility.\n')
        before = snapshot(self.root)
        self.init(cwd=generic_role.parent)
        self.assertEqual(snapshot(self.root), before)
        self.run_cli('verify')
        for p, data in protected.items():
            self.assertEqual((self.root / p).read_bytes(), data)
        for stage, row in roles.items():
            if stage not in (4, 5):
                self.assertFalse((self.root / row['folder'] / 'skills/decision/SKILL.md').exists())

    def test_missing_shared_focus_template_fails_before_any_writes(self):
        for name in ('SKILL.md', 'agents/openai.yaml'):
            path = self.root / 'asdg/templates/.agents/skills/asdg-focus' / name
            original = path.read_bytes()
            path.unlink()
            before = snapshot(self.root)
            self.init(expect=1)
            self.assertEqual(snapshot(self.root), before)
            path.write_bytes(original)

    def test_retired_focus_template_is_rejected_before_any_writes(self):
        path = self.root / 'asdg/templates/.agents/skills/asdg-focus-05-architecture/SKILL.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\nname: asdg-focus-05-architecture\ndescription: Retired fixture.\n---\n')
        before = snapshot(self.root)
        self.init(expect=1)
        self.assertEqual(snapshot(self.root), before)

    def test_advice_report_creates_planning_parents_without_changing_state(self):
        self.init('--project-status', 'defining')
        before = snapshot(self.root)
        status = json.loads(self.run_cli('status', '--json').stdout)
        advice = dict(status='available',
            summary=dict(action='Review the existing context.',
                         reason='Its evidence is not registered.', question=None),
            action='Review the existing context and propose evidence references.',
            reason='Existing files need provenance review.',
            evidence=['.asdg/lifecycle.json'], questions=[],
            uncertainties=['Human acceptance is not recorded.'],
            requirements=['Human review remains pending.'],
            runtime=dict(sdk_version='0.163.0', cli_version='0.163.0', model='fixture',
                         model_provider='openai', model_basis='THREAD_CONFIGURATION',
                         thread_id='fixture-thread', turn_id='fixture-turn',
                         sandbox='read-only', approval_mode='deny-all', ephemeral=True))
        report = save_advice(self.root.resolve(), status, advice, repo=self.root)
        self.assertEqual(report.parent, self.root.resolve() / 'docs/asdg/07-planning')
        receipt = json.loads(report.with_suffix('.json').read_text())
        self.assertIsNone(receipt['document_review']['human_approval'])
        self.assertLessEqual(sum(bool(x.strip()) for x in report.read_text().splitlines()), 50)
        after = snapshot(self.root)
        self.assertEqual({k: after[k] for k in before}, before)
        self.assertEqual(set(after) - set(before),
                         {p.relative_to(self.root.resolve()).as_posix() for p in (report, report.with_suffix('.json'))})

    def test_preserves_client_instructions_documents_and_ignore(self):
        old = b'AI-MODIFIED - 2026-10-01T00:00Z | PME-APPROVED - 2026-10-02T00:00Z\n# Client\nKeep this client rule.\n'
        (self.root / 'AGENTS.md').write_bytes(old)
        (self.root / '.gitignore').write_text('node_modules/\n')
        doc = self.root / 'docs/asdg/02-purpose/README.md'
        doc.parent.mkdir(parents=True); doc.write_text('# Existing purpose\nKeep this content.\n')
        self.init()
        cli = self.bootstrap_module()
        self.assertEqual((self.root / 'AGENTS.md').read_bytes(), cli.BRIDGE.encode() + b'\n# Client\nKeep this client rule.\n')
        self.assertTrue((self.root / '.gitignore').read_text().startswith('node_modules/\n'))
        self.assertIn('Keep this content.', doc.read_text())
        ledger = json.loads((self.root / '.asdg/document-reviews.json').read_text())
        entry = next(e for e in ledger['events'] if e['path'] == 'AGENTS.md')
        self.assertEqual(entry['previous_state']['sha256'], hashlib.sha256(old).hexdigest())
        self.assertIn('PME-APPROVED', entry['previous_state']['visible_review_markers'][0])
        self.assertIsNone(entry['human_approval'])

    def test_existing_codex_config_conflict_has_no_side_effects(self):
        p = self.root / '.codex/config.toml';p.parent.mkdir();p.write_text('model = "user-choice"\n')
        before = snapshot(self.root)
        self.init(expect=1)
        self.assertEqual(snapshot(self.root), before)

    def test_foreign_binding_and_legacy_data_are_not_overwritten(self):
        p = self.root / '.asdg/project.json';p.parent.mkdir();p.write_text('{"provider":"other"}')
        before = snapshot(self.root)
        self.init(expect=1);self.assertEqual(snapshot(self.root), before)
        shutil.rmtree(p.parent);(self.root / '.asdlc').mkdir()
        before = snapshot(self.root)
        self.init(expect=1);self.assertEqual(snapshot(self.root), before)

    def test_edited_adapter_is_preserved_and_verification_fails(self):
        self.init()
        p=self.root/'.agents/skills/asdg-focus/SKILL.md';p.write_text(p.read_text()+'\nLocal change.\n')
        before=snapshot(self.root)
        self.init(expect=1); self.run_cli('verify', expect=1)
        self.assertEqual(snapshot(self.root), before)

    def test_malformed_or_missing_state_is_never_recreated(self):
        self.init()
        for rel in ('.asdg/sprint.json', '.asdg/lifecycle.json', '.asdg/document-reviews.json'):
            p=self.root/rel; old=p.read_bytes()
            for bad in (b'{bad json', None):
                if bad is None:p.unlink()
                else:p.write_bytes(bad)
                before=snapshot(self.root)
                self.init(expect=1);self.assertEqual(snapshot(self.root), before)
                p.write_bytes(old)

    def test_symlink_destination_is_rejected(self):
        outside=Path(self.area.name)/'outside';outside.mkdir()
        (self.root/'.asdg').symlink_to(outside, target_is_directory=True)
        self.init(expect=1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_relocation_and_subdirectory_invocation(self):
        self.init('--project-status','defining')
        before=snapshot(self.root)
        moved=Path(self.area.name)/"moved client's space";self.root.rename(moved);self.root=moved
        (self.root/'nested').mkdir()
        self.run_cli('verify',cwd=self.root/'nested')
        self.init(cwd=self.root/'nested')
        self.assertEqual(snapshot(self.root),before)
        result=self.hook(self.payload(['app.js']),cwd=self.root/'nested')
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'],'deny')
        for path in (self.root/'.asdg').glob('*.json'):
            self.assertNotIn(str(Path(self.area.name)/'client project'),path.read_text())

    def test_rejects_non_git_and_external_root(self):
        outside=Path(self.area.name)/'outside';outside.mkdir()
        self.init(cwd=outside,expect=1)
        subprocess.run(['git','init','-q',str(outside)],check=True)
        self.init(cwd=outside,expect=1)
        self.assertFalse((outside/'.asdg').exists())

    def test_inactive_sprint_blocks_patch_and_arbitrary_shell(self):
        self.init();before=snapshot(self.root)
        self.denied(self.payload(['app.js']))
        self.denied({'tool_name':'Bash','tool_input':{'command':'echo bad > app.js'},'cwd':str(self.root)})
        self.run_cli('sprint','check-implementation','--path','app.js',expect=1)
        self.assertEqual(snapshot(self.root),before)

    def test_documentation_writes_require_governance_bootstrap_but_no_sprint(self):
        self.init()
        doc = ['docs/asdg/07-planning/handoff.md']
        self.assertEqual(json.loads((self.root / '.asdg/sprint.json').read_text())['status'], 'inactive')
        self.assertEqual(self.hook(self.payload(doc), role="ASDG-07"), {})
        for relative in ('asdg/00-governance/types/contract.md', 'asdg/skills/asdg-focus/session-state.md'):
            path = self.root / relative
            original = path.read_bytes()
            path.unlink()
            for targets in (doc, ['app.js']):
                reason = self.hook(self.payload(targets))['hookSpecificOutput']['permissionDecisionReason']
                self.assertIn('BLOCKED: GOVERNANCE_BOOTSTRAP', reason)
                self.assertIn(f'{relative}: required governance source missing', reason)
            for command in ('git status --short', 'python3 asdg/scripts/cli.py status --json', 'cat AGENTS.md'):
                self.assertEqual(self.hook({'tool_name': 'Bash', 'cwd': str(self.root),
                                            'tool_input': {'command': command}}), {}, command)
            path.write_bytes(original)
            self.assertEqual(self.hook(self.payload(doc), role="ASDG-07"), {})

    def test_valid_admin_package_passes_without_changing_catalogue_or_binding(self):
        catalogue = (self.root / 'asdg/00-governance/types/agent-catalog.json').read_bytes()
        self.init()
        binding = (self.root / '.asdg/project.json').read_bytes()
        self.run_cli('verify')
        self.init()
        self.assertEqual((self.root / 'asdg/00-governance/types/agent-catalog.json').read_bytes(), catalogue)
        self.assertEqual((self.root / '.asdg/project.json').read_bytes(), binding)
        self.assertEqual(json.loads(binding)['catalog_sha256'], hashlib.sha256(catalogue).hexdigest())

    def test_invalid_admin_package_fails_preflight_and_verify_with_diagnostic(self):
        self.init()
        registration = self.root / 'asdg/admin/types/admin-role.json'
        original = registration.read_bytes()
        value = json.loads(original)
        cases = [
            (lambda: registration.unlink(), 'Admin registration missing: asdg/admin/types/admin-role.json'),
            (lambda: registration.write_text('{"role_id": '), 'Admin registration is not valid JSON'),
            (lambda: registration.write_text(json.dumps(dict(value, default=True))), 'field default must be false'),
            (lambda: registration.write_text(json.dumps(dict(value, activation='automatic'))), 'field activation must be'),
            (lambda: registration.write_text(json.dumps(dict(value, role_id='ASDG-COORDINATOR'))), 'field role_id must be'),
            (lambda: registration.write_text(json.dumps(dict(value, extra=1))), 'missing or unexpected fields'),
            (lambda: registration.write_text(json.dumps(dict(value, entry='asdg/admin/../AGENTS.md'))),
             'entry must be a path inside asdg/admin/'),
            (lambda: (self.root / 'asdg/admin/types/contract.md').unlink(),
             'Admin contract source missing: asdg/admin/types/contract.md'),
        ]
        contract = (self.root / 'asdg/admin/types/contract.md').read_bytes()
        for damage, diagnostic in cases:
            damage()
            result = self.run_cli('verify', expect=1)
            self.assertIn(diagnostic, result.stdout + result.stderr)
            before = snapshot(self.root)
            result = self.init(expect=1)
            self.assertIn(diagnostic, result.stdout + result.stderr)
            self.assertEqual(snapshot(self.root), before)
            registration.write_bytes(original)
            (self.root / 'asdg/admin/types/contract.md').write_bytes(contract)
        self.run_cli('verify')

    def test_documentation_patch_needs_no_sprint_or_lifecycle_state(self):
        self.init()
        targets = ['docs/asdg/03-system-model-and-use-cases/01.4-question.md',
                   'docs/asdg/03-system-model-and-use-cases/images/question.svg',
                   'docs/asdg/03-system-model-and-use-cases/handoff.json', 'docs/asdg/03-system-model-and-use-cases/question.puml']
        before = snapshot(self.root)
        self.assertEqual(self.hook(self.payload(targets), role="ASDG-03"), {})
        self.assertEqual(snapshot(self.root), before)
        for relative in ('.asdg/sprint.json', '.asdg/lifecycle.json'):
            path = self.root / relative
            original = path.read_bytes()
            path.write_text('{malformed')
            self.assertEqual(self.hook(self.payload(targets), role="ASDG-03"), {})
            self.denied(self.payload(['app.js']))
            path.unlink()
            self.assertEqual(self.hook(self.payload(targets), role="ASDG-03"), {})
            self.denied(self.payload(['app.js']))
            path.write_bytes(original)

    def test_mixed_documentation_and_code_checks_every_code_target(self):
        self.init()
        doc = 'docs/asdg/09-build-and-test-cycle/03-plan.md'
        self.denied(self.payload([doc, 'app.js']))
        self.active()
        self.assertEqual(self.hook(self.payload([doc, 'app.js'])), {})
        self.denied(self.payload([doc, 'app.js', 'index.html']))
        self.denied(self.payload([doc, 'docs/example.py']))
        self.denied(self.payload([doc, 'docs/example.js']))
        self.denied(self.payload([]))
        self.run_cli('sprint', 'check-implementation', '--path', 'index.html', expect=1)

    def test_documentation_exemption_rejects_escape_policy_and_symlink_targets(self):
        self.init()
        for target in ('docs/../app.js', 'docs/../.asdg/sprint.json',
                       'docs/AGENTS.md', 'docs/SKILL.md', 'docs/.codex/config.json',
                       'docs-other/note.md', '../outside.md'):
            self.denied(self.payload([target]))
        outside = Path(self.area.name) / 'outside'
        outside.mkdir()
        (self.root / 'docs/linked').symlink_to(outside, target_is_directory=True)
        self.denied(self.payload(['docs/linked/note.md']))
        destination = self.root / 'docs/note.md'
        destination.symlink_to(outside / 'note.md')
        self.denied(self.payload(['docs/note.md']))
        self.assertEqual(list(outside.iterdir()), [])

    def test_documentation_moves_validate_both_targets(self):
        self.init()
        def move(source, destination):
            return {'tool_name': 'apply_patch', 'cwd': str(self.root),
                    'tool_input': {'command': '*** Begin Patch\n*** Update File: '
                                   + source + '\n*** Move to: ' + destination
                                   + '\n@@\n-old\n+new\n*** End Patch'}}
        self.assertEqual(self.hook(move('docs/asdg/09-build-and-test-cycle/old.md', 'docs/asdg/09-build-and-test-cycle/new.md')), {})
        self.denied(move('app.js', 'docs/app.md'))
        self.denied(move('docs/note.md', 'app.js'))
        self.denied(move('docs/note.md', '.asdg/sprint.json'))

    def test_active_sprint_checks_every_path_and_is_preserved(self):
        self.init();self.active()
        self.assertEqual(self.hook(self.payload(['app.js'])),{})
        self.denied(self.payload(['app.js','index.html']))
        before=snapshot(self.root);self.init();self.assertEqual(snapshot(self.root),before)
        self.run_cli('sprint','check-implementation','--path','app.js')
        self.run_cli('sprint','check-implementation','--path','index.html',expect=1)
        self.run_cli('sprint','start','--id','S2','--objective','x','--scope','app.js','--acceptance','x',expect=1)
        self.run_cli('sprint','stop');self.denied(self.payload(['app.js']))

    def test_protected_governance_traversal_and_symlink_scope_blocked(self):
        self.init()
        for target in ('asdg/scripts/cli.py','.asdg/sprint.json','.codex/hooks.json','AGENTS.md','../outside','src/*'):
            self.run_cli('sprint','start','--id','S1','--objective','x','--scope',target,'--acceptance','x',expect=1)
        outside=Path(self.area.name)/'target';outside.write_text('safe')
        (self.root/'linked').symlink_to(outside)
        self.run_cli('sprint','start','--id','S1','--objective','x','--scope','linked','--acceptance','x',expect=1)
        self.assertEqual(outside.read_text(),'safe')

    def test_guard_failure_fallback_and_unknown_tool(self):
        self.init();self.denied({'tool_name':'unknown','tool_input':{}})
        (self.root/'asdg/scripts/hook.py').unlink()
        self.denied(self.payload(['app.js']))

    def test_guard_allows_only_local_factual_status(self):
        self.init()
        base={'tool_name':'Bash','cwd':str(self.root)}
        self.assertEqual(self.hook(dict(base,tool_input={'command':'python3 asdg/scripts/cli.py status --json'})),{})
        self.denied(dict(base,tool_input={'command':'python3 asdg/scripts/cli.py status --verbose'}))
        self.denied(dict(base,tool_input={'command':'python3 asdg/scripts/cli.py sprint stop'}))

    def test_logs_ignored_state_retained_and_no_raw_tool_data(self):
        self.init()
        payload={'hook_event_name':'SubagentStart','agent_type':'asdg_02','agent_id':'child-1',
                 'session_id':'session-1','turn_id':'turn-1','cwd':str(self.root)}
        self.hook(payload,event='SubagentStart');self.hook(payload,event='SubagentStart')
        payload.update(hook_event_name='PostToolUse',tool_name='Bash',tool_use_id='tool-1',
                       tool_input={'command':'sensitive content'},tool_response={'exit_code':0,'output':'private output'})
        self.hook(payload,event='PostToolUse')
        records=self.root/'logs/asdg/session-1/child-1/events.jsonl'
        rows=[json.loads(x) for x in records.read_text().splitlines()]
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['role_id'],'ASDG-02')
        self.assertNotIn('sensitive content',records.read_text());self.assertNotIn('private output',records.read_text())
        for path,code in [('logs/asdg/session-1/child-1/events.jsonl',0),('.asdg/sprint.json',1),('.asdg/document-reviews.json',1)]:
            result=subprocess.run(['git','check-ignore','-q',path],cwd=self.root)
            self.assertEqual(result.returncode,code,path)
        before={p.name:p.read_bytes() for p in (self.root/'.asdg').glob('*.json')}
        shutil.rmtree(self.root/'logs');self.run_cli('verify')
        self.assertEqual(before,{p.name:p.read_bytes() for p in (self.root/'.asdg').glob('*.json')})

    def test_recorded_evidence_and_release_survive_repeat_init(self):
        self.init()
        p=self.root/'docs/asdg/01-context-and-domain-analysis/current/context.md';p.parent.mkdir(exist_ok=True);p.write_text('# Evidence\nObserved fixture.\n')
        state={'schema_version':1,'project_status':'defining','release':{'release_id':'R1','status':'planning'},
               'stages':{'01':{'artifacts':[p.relative_to(self.root).as_posix()],'not_applicable_reason':None}}}
        (self.root/'.asdg/lifecycle.json').write_text(json.dumps(state))
        before=snapshot(self.root);self.init();self.assertEqual(snapshot(self.root),before)
        report=json.loads(self.run_cli('status','--json').stdout)
        self.assertEqual(report['current_stage']['number'],2);self.assertEqual(report['release_id'],'R1')

    def test_advice_context_and_environment_without_model_call(self):
        self.init()
        text=build_prompt(self.root,{},self.root)
        self.assertIn(str(self.root/'asdg/AGENTS.md'),text)
        self.assertIn(str(self.root/'asdg/docs/lifecycle-baseline.md'),text)
        environment=subprocess_environment({'PATH':'/usr/bin','API_KEY':'not-forwarded'})
        self.assertNotIn('API_KEY',environment)

    def test_transaction_rolls_back_only_its_own_changes(self):
        old=self.root/'client.txt';old.write_text('old')
        changes=[plan(self.root,'new/file.txt',b'new'),plan(self.root,'client.txt',b'changed',replace=True)]
        with patch('cli_files.atomic_replace',side_effect=OSError('injected failure')):
            with self.assertRaises(OSError):apply(changes)
        self.assertFalse((self.root/'new').exists());self.assertEqual(old.read_text(),'old')
        self.assertEqual((self.root/'app.js').read_bytes(),self.app)


if __name__ == '__main__':
    unittest.main()
