import os
import sys
import subprocess


class PasswordStore:
    def __init__(self, store_path=None):
        # TODO: locate gpg binary, or error
        # TODO: locate pass binary, or error

        if store_path:
            store_path = os.path.expanduser(store_path)
        else:
            store_path = os.path.expanduser("~/.password-store")

        if not os.path.exists(store_path):
            raise FileNotFoundError(f"Path to password store does not exist: {store_path}")

        if not os.path.isdir(store_path):
            raise ValueError(f"Path to password store is not a directory: {store_path}")

        self._store_path = store_path

    def _cmd(self, cmd):
        popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        return_code = popen.wait()

        if return_code == 0:
            output = popen.stdout.read().strip()
            return output

        err = popen.stderr.read() if popen.stderr else None
        if err:
            raise ValueError(f"return code: {return_code}: {err}")

    def unlock(self):
        """
        Make the gpg-agent ask for passphrase for unlocking the
        password-stores gpg-key, if it is not already in the
        agent.
        """
        self._cmd(
            [
                "gpg",
                "--quiet",
                "--no-greeting",
                "--clearsign",
                "--output",
                "/dev/null",
                "/dev/null",
            ]
        )

    def list(self):
        """
        Return a list of all entries in the password store.
        """
        # an entry in the password store is the relative path from the
        # root of the store, to some .gpg file in a subdirectory.

        files = []
        for root, _, fs in os.walk(self._path):
            files += [os.path.join(root, f) for f in fs]

        rel_files = [os.path.relpath(f, start=self._store_path) for f in files]
        rel_files.remove(".gpg-id")

        entries = [f.strip(".gpg") for f in rel_files]

        return entries

    def get(self, path):
        """
        Return the secret for `path', if found in the password store, None otherwise.
        """
        return self._cmd(["pass", path])

    def set(self, path, secret):
        """
        Insert `secret' into the password store, at `path'.
        """
        self._cmd(["pass", "insert", path, secret])

    def generate(self, path):
        """
        Insert a generated secret into `path' in the password store.
        """
        self._cmd(["pass", "generate", path])
