from os.path import abspath, basename, dirname, exists, join

from android.utils import shell
from android.utils.keys_utils import copy_keys

GIT_URI = 'https://github.com/haiwen/seadroid.git'

DOCKER_IMAGE = 'lins05/android-sdk:latest'

class APKBuilder:
    """
    Builds signed apk from seadroid source code.
    """
    def __init__(self, tag):
        self.sourcedir = '/tmp/seadroid'
        self.tag = tag
        self.key_files = (
            'key.properties',
            'release.keystore',
        )

    def build(self):
        self.prepare_source()
        self.prepare_keys()
        self.do_build()

    def prepare_keys(self):
        for fn in self.key_files:
            copy_keys(fn, join(self.sourcedir, 'app'))

    def prepare_source(self):
        if not exists(self.sourcedir):
            shell(f'git clone {GIT_URI} {self.sourcedir}')
        else:
            shell(f'git fetch', cwd=self.sourcedir)
        shell(f'git reset --hard {self.tag}', cwd=self.sourcedir)

    def do_build(self):
        mounts = {
            self.sourcedir: self.sourcedir,
            '/tmp/seadroid-builder/.gradle': '/root/.gradle',
            '/tmp/seadroid-builder/.android': '/root/.android',
        }

        mounts_opts = ' '.join([f'-v {k}:{mounts[k]}' for k in mounts])
        cmd = 'docker run --rm -it --name seadroid ' + \
              f'{mounts_opts} -w {self.sourcedir} {DOCKER_IMAGE} ' + \
              './gradlew clean assembleRelease'
        shell(cmd)

    def get_output(self):
        outputfn = join(self.sourcedir, f'app/build/outputs/apk/seafile-{self.tag}.apk')
        assert exists(outputfn), outputfn
        return outputfn
