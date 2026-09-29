# Build investigation on macOS

Tested source: `0c58fb6683a49a178a8ad845a8c296c2cb83bd81`.
Host: Apple Silicon Mac, Docker through OrbStack.

**Both account and game servers compile and execute inside 32-bit Linux on
this Mac.** This is a server build/startup experiment, not a verified playable
installation. There is no game client in this repository.

## Reproduce the builds

From this repository's root, start a disposable 32-bit Linux environment.
The read-only mount keeps all build and runtime changes off the checkout.
Nothing is published to host network ports.

```sh
docker run --rm -it --platform linux/386 \
  --mount "type=bind,source=$PWD,target=/source,readonly" \
  i386/debian:bookworm bash
```

Inside the container:

```sh
apt-get update
apt-get install -y --no-install-recommends \
  build-essential libmariadb-dev-compat zlib1g-dev file
mkdir -p /work
cp -a /source/gmsv /source/saac /work/

make -C /work/saac clean
make -C /work/saac -j4 CC='gcc -fcommon -fgnu89-inline'

make -C /work/gmsv clean
make -C /work/gmsv -j8 \
  CFLAGS='-O1 -w -fcommon -fgnu89-inline -I. -I.. -I./include -I../include'

file /work/saac/saacjt.exe /work/gmsv/gmsvjt.exe
```

Both outputs are **ELF 32-bit Intel 80386 Linux executables**, despite their
`.exe` suffixes. They are not Windows or macOS programs. The tested toolchain
was Debian Bookworm GCC 12.2.0 and MariaDB 10.11 client development libraries.
Exiting this disposable container removes the built copies; copy desired
artifacts out before exiting if you need to keep them.

The flags preserve legacy common-symbol and GNU inline behavior. Without
them, the account server fails to link duplicate globals such as `Herolist`
and `fm_pk_list`; the game server also has unresolved inline-function symbols.
This compatibility workaround does not fix or audit the old game logic.

## Runtime work still required

Run each executable from its own directory so that relative configuration and
data paths resolve. The bundled account server listens on `9300`; the game
server listens on `9065` and connects to `127.0.0.1:9300`.

- Configure a local MySQL-compatible database and replace the sample database
  credentials in `saac/acserv.cf`. The repository omits the schema. The empty
  `sasql_craete_userinfo` and `sasql_craete_lock` functions do not create it.
  Derive the required tables from `saac/sasql.c`, including column order:
  login compares the password against `mysql_row[1]`.
- Ensure the game server's `acpasswd` matches the account server's `pass`.
  Preserve server world data and writable account/character directories.
- For an eventual local client, publish only the game port on loopback, for
  example `-p 127.0.0.1:9065:9065`. Separate database/account/game containers
  require updating their connection addresses; `127.0.0.1` refers to each
  container itself.
- Obtain a matching Windows client and its complete graphics/data pack. Test
  login, character creation, movement, battle, save and relogin. No client
  gameplay has been tested in this investigation.

The account server continues listening even when database connection fails,
so an open TCP port is **not** proof that login works.

### Observed startup result

A brief smoke test reached both listening ports. A subsequent 20-second test
running both services with the bundled configuration did **not** stay healthy:
the account server terminated with signal 11 after accepting the game-server
connection, and the game server exited after losing its account-server link.
The game process had reached NPC/signal and map-warp initialization, including
2,981 warp points. Logs also report a failed database connection and missing
`char_sleep` directories. The crash's root cause is not established; configuring
the database alone must not be assumed to fix it. Debug this handshake crash
before calling the setup runnable for gameplay.

## Why use Linux instead of a native Mac build?

The stock game-server build fails with Apple Clang because the legacy
`snprintf` declaration in `gmsv/include/common.h:46` conflicts with the macOS
SDK. Pointer-to-`int` casts, including `gmsv/buf.c:176`, also need auditing
before a 64-bit port. The 32-bit Linux environment avoids changing the data
model while establishing a baseline.

The newer [lhr0909/stoneage](https://github.com/lhr0909/stoneage) fork contains
a Win32 client and a different server generation. Its `VER25` client build
configuration is a lead to investigate, not evidence of protocol compatibility.
Its SQL schema and data should not be substituted blindly into this server.
For the Windows client, [CrossOver](https://www.codeweavers.com/support/docs/crossover-mac/index)
is a Mac compatibility option to test once the client and assets are available;
compatibility with this game remains unverified.
