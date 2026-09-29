# Local Stone Age 2.5 server

From this repository:

```sh
docker compose up -d --build --wait
docker compose ps
docker compose logs -f gmsv
```

The game endpoint is **127.0.0.1:9065**. Only that loopback port is published.
The database and account server are internal to Compose. The development account
is **player / stoneage**. These are local development credentials, not a public
server configuration.

The image builds the bundled 2.5 server as i386 Linux, including its world data.
Apple Silicon needs a Docker engine capable of running `linux/386`; this was
verified with OrbStack on the development Mac. MariaDB runs at the host's native
architecture. The 32-bit ABI is intentional: the server has pointer/integer
assumptions that have not been ported to 64 bits.

## What is verified

The native macOS protocol probe built from the newer client's VER25 codec can
authenticate, list characters, create a character, enter the world, save/logout,
and reconnect. This is a server/protocol test, **not a playable graphical Mac
client**. See the client fork's `native/README.md` for its current porting status.

Startup fixes address an account read-buffer access at index -1, an oversized
manor-data input, and an unterminated ranking-file read. Empty lines and oversized
account lines are covered by a regression test. The game connection limit is
128 because the legacy table is indexed by OS file descriptors, not simply the
number of players.

## State and lifecycle

Compose volumes preserve SQL accounts, character saves, mail, families, rankings,
game-world writable files, and logs. First startup seeds game data from the image;
subsequent starts preserve that copy. It does not import the repository's sample
character saves. Schema initialization runs only for a fresh database volume.

```sh
docker compose stop                 # gracefully stop, retain state
docker compose start                # resume
docker compose down                 # remove containers/network, retain state
docker compose up -d --wait          # recreate using retained state
```

Do not add `--volumes` to `down` unless you intend to erase the saved game.
Changes to source world files require an explicit data migration for an existing
volume; rebuilding the image does not overwrite existing world state.

The account server's healthcheck checks its listening socket; it exits if SQL
initialization fails. The game check requires its listener and an established
account connection. These are startup healthchecks, not full login tests.

## Regression test

```sh
docker build --platform linux/386 --target test -t stoneage25-server:test .
```

This runs the actual account-server buffer routines with address/undefined
behavior sanitizers. The default Docker build produces the runtime image; Compose
explicitly selects the runtime stage. Compiler warnings are retained, and the
executables retain debug symbols. The runtime image contains no compiler.

For integration verification, use the client fork's native protocol probe against
this stack. With the optional character argument it creates a character only if
the account is empty, enters the world, then saves/logs out. Restart the stack and
repeat to check persistence.
