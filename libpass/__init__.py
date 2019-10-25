import os
import sys
import subprocess


class PasswordStore:
    def __init__(self, path=None):
        if path:
            path = os.path.expanduser(path)

            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Path to password store does not exist: {path}"
                )

            if not os.path.isdir(path):
                raise ValueError(f"Path to password store is not a directory: {path}")

            self._path = path
        else:
            self._path = os.path.expanduser("~/.password-store")

        print(self._path)

    def _cmd(self, cmd):
        popen = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True
        )

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
        files = []
        for root, _, fs in os.walk(self._path):
            files += [os.path.join(root, f) for f in fs]

        rel_files = [os.path.relpath(f, start=self._path) for f in files]
        rel_files.remove(".gpg-id")

        entries = [f.strip(".gpg") for f in rel_files]

        return entries

    def get(self, path):
        """
        Return the secret for `path', if found in the password store, None otherwise.
        """
        return self._cmd(["pass", path])
