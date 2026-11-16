import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from package_release import PACKAGE, decide, valid_version, validate_assets


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'test')
        self.git('config', 'user.email', 'test@example.invalid')
        PACKAGE.mkdir(parents=True)
        self.write_version('1.0.0')

    def tearDown(self):
        os.chdir(self.previous)
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', *args], stderr=subprocess.STDOUT, text=True)

    def write_version(self, version):
        (PACKAGE / 'package.json').write_text(json.dumps({'name': 'com.coolishbee.atlas-image', 'version': version}))
        self.git('add', '.')
        self.git('commit', '-qm', version)

    def decision(self, version=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return decide(version)

    def test_new_version(self):
        self.assertEqual(self.decision(), {'version': '1.0.0', 'tag': 'v1.0.0', 'create': 'true', 'publish': 'true'})

    def test_existing_version_and_retry(self):
        self.git('tag', 'v1.0.0')
        self.assertEqual(self.decision()['publish'], 'false')
        self.write_version('1.0.1')
        self.assertEqual(self.decision()['create'], 'true')
        retry = self.decision('1.0.0')
        self.assertEqual(retry['create'], 'false')
        self.assertEqual(retry['publish'], 'true')

    def test_missing_retry_tag(self):
        with self.assertRaises(ValueError):
            self.decision('1.0.0')

    def test_mismatched_tag(self):
        self.git('tag', 'v2.0.0')
        with self.assertRaises(AssertionError):
            self.decision('2.0.0')

    def test_wrong_package_name(self):
        manifest = PACKAGE / 'package.json'
        manifest.write_text(json.dumps({'name': 'com.other.package', 'version': '1.0.0'}))
        self.git('add', '.')
        self.git('commit', '-qm', '다른 패키지')
        self.git('tag', 'v1.0.0')
        self.write_version('1.0.0')
        with self.assertRaises(AssertionError):
            self.decision()

    def test_tag_outside_history(self):
        self.git('tag', 'base')
        self.write_version('1.0.1')
        self.git('tag', 'v1.0.1')
        self.git('checkout', '-q', '--detach', 'base')
        with self.assertRaises(subprocess.CalledProcessError):
            self.decision('1.0.1')

    def test_invalid_versions(self):
        for value in ['1.0', '01.0.0', '1.0.0+build', '1.0.0-01', '$(id)', '../x', '1.0.0\ntag=x']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_version(value)
        self.assertEqual(valid_version('1.0.0-preview.1'), '1.0.0-preview.1')



class AssetValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.temp.name)
        PACKAGE.mkdir(parents=True)
        self.shipped = PACKAGE / 'Samples~/AtlasImageSample'
        self.shipped.mkdir(parents=True)
        Path(str(self.shipped) + '.meta').write_text('guid: ' + '1' * 32)
        (self.shipped / 'demo.txt').write_text('샘플')
        (self.shipped / 'demo.txt.meta').write_text('guid: ' + '2' * 32)
        self.working = Path('SampleProject/Assets/AtlasImageSample')
        import shutil
        shutil.copytree(self.shipped, self.working)

    def tearDown(self):
        os.chdir(self.previous)
        self.temp.cleanup()

    def test_matching_samples(self):
        validate_assets()

    def test_different_samples(self):
        (self.working / 'demo.txt').write_text('변경')
        with self.assertRaises(ValueError):
            validate_assets()

    def test_missing_meta(self):
        (self.shipped / 'demo.txt.meta').unlink()
        with self.assertRaises(ValueError):
            validate_assets()

    def test_orphan_meta(self):
        (PACKAGE / 'missing.meta').write_text('guid: ' + '3' * 32)
        with self.assertRaises(ValueError):
            validate_assets()

    def test_duplicate_guid(self):
        (self.shipped / 'demo.txt.meta').write_text('guid: ' + '1' * 32)
        with self.assertRaises(ValueError):
            validate_assets()


if __name__ == '__main__':
    unittest.main()
