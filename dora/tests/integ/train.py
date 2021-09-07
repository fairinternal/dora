import os

from dora.tests.test_main import get_main

main = get_main(os.environ['_DORA_TEST_TMPDIR'])

if os.environ.get('_DORA_CLEAN_GIT') == '1':
    main.dora.clean_git = True
