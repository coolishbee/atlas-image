import argparse
import json
import os
from pathlib import Path
import re
import subprocess

PACKAGE = Path('Packages/com.coolishbee.atlas-image')
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?')


def valid_version(value):
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise ValueError('유효한 버전 번호가 필요합니다. 빌드 메타데이터는 사용하지 않습니다.')
    return value


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def validate():
    manifest = json.loads((PACKAGE / 'package.json').read_text())
    assert manifest['name'] == 'com.coolishbee.atlas-image'
    valid_version(manifest['version'])
    for relative in ['README.md', 'README.md.meta', 'LICENSE', 'CHANGELOG.md']:
        assert (PACKAGE / relative).is_file(), relative
    for sample in manifest['samples']:
        assert (PACKAGE / sample['path']).is_dir(), sample['path']
    packed = json.loads(subprocess.check_output(
        ['npm', 'pack', '--dry-run', '--json', '--ignore-scripts'], cwd=PACKAGE, text=True))[0]
    names = {item['path'] for item in packed['files']}
    assert {'README.md', 'LICENSE', 'package.json', 'CHANGELOG.md'} <= names
    for prefix in ['Runtime/', 'Editor/', 'Samples~/']:
        assert any(name.startswith(prefix) for name in names), prefix
    assert not any(name.startswith(('SampleProject/', '.github/')) for name in names)
    assert packed['size'] < 512 * 1024 * 1024
    project_manifest = json.loads(Path('SampleProject/Packages/manifest.json').read_text())
    project_lock = json.loads(Path('SampleProject/Packages/packages-lock.json').read_text())
    expected_path = 'file:../../' + PACKAGE.as_posix()
    assert project_manifest['dependencies'][manifest['name']] == expected_path
    locked = project_lock['dependencies'][manifest['name']]
    assert locked['version'] == expected_path and locked['source'] == 'local'
    assert locked['dependencies'] == manifest['dependencies']
    local_manifest = {name for name, value in project_manifest['dependencies'].items() if value.startswith('file:')}
    local_lock = {name for name, value in project_lock['dependencies'].items() if value['source'] == 'local'}
    assert local_manifest == local_lock == {manifest['name']}
    validate_assets()
    print('패키지 정보와 배포 파일 검사 완료')


def validate_assets():
    guids = set()
    for path in PACKAGE.rglob('*'):
        if path.name.endswith('~'):
            continue
        if path.suffix == '.meta':
            if not path.with_suffix('').exists():
                raise ValueError(f'대상이 없는 메타 파일: {path}')
            match = re.search(r'^guid: ([0-9a-f]{32})$', path.read_text(), re.MULTILINE)
            if not match or match[1] in guids:
                raise ValueError(f'잘못되었거나 중복된 GUID: {path}')
            guids.add(match[1])
        elif not Path(str(path) + '.meta').is_file():
            raise ValueError(f'메타 파일 누락: {path}')
    shipped = PACKAGE / 'Samples~/AtlasImageSample'
    working = Path('SampleProject/Assets/AtlasImageSample')
    shipped_files = {p.relative_to(shipped): p.read_bytes() for p in shipped.rglob('*') if p.is_file()}
    working_files = {p.relative_to(working): p.read_bytes() for p in working.rglob('*') if p.is_file()}
    if not shipped_files or shipped_files != working_files:
        raise ValueError('배포 샘플과 검증 프로젝트 샘플이 다릅니다.')


def decide(retry_version=None):
    manifest = json.loads((PACKAGE / 'package.json').read_text())
    version = valid_version(retry_version or manifest['version'])
    tag = 'v' + version
    exists = subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/tags/' + tag]).returncode == 0
    if retry_version and not exists:
        raise ValueError('재시도할 태그가 없습니다.')
    if exists:
        tagged = json.loads(git('show', f'{tag}:{PACKAGE}/package.json'))
        assert tagged['name'] == manifest['name'] and tagged['version'] == version
        subprocess.run(['git', 'merge-base', '--is-ancestor', tag, 'HEAD'], check=True)
    values = {'version': version, 'tag': tag, 'create': str(not exists).lower(),
              'publish': str(bool(retry_version) or not exists).lower()}
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
            for key, value in values.items():
                stream.write(f'{key}={value}\n')
    print(json.dumps(values))
    return values


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['validate', 'decide'])
    parser.add_argument('--retry-version', default='')
    args = parser.parse_args()
    if args.command == 'validate':
        validate()
    else:
        decide(args.retry_version)
