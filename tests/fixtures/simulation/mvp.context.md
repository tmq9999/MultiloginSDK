# Simulation context — multilogin-sdk-mvp

Generated 2026-10-22 from mocks: `./cloud`, `./launcher`, `./cookies`.
This file is how the next session starts without redoing the setup. Fill in each
@todo as you work, and update it when something you relied on turns out wrong.

## Purpose

Mocks HTTP dependencies: cloud (sdk-cloud), launcher (sdk-launcher), cookies (sdk-cookies).
Endpoints covered are in each handler under `tests/fixtures/simulation`.

<!-- @todo Once you've worked here, replace the line above: what this stands in
     for, and what work it unblocks. Needs hindsight — leave it until last. -->
<!-- @todo Add the origin host each mock above stands in for. -->

## Execution

```sh
# start the simulation first
postman simulation run tests/fixtures/simulation/mvp.sim.yaml \
  --port 3000 --output ndjson > /tmp/mvp-simulation.log 2>&1 &

# @todo start the service pointed at the simulation — command and env

# @todo prove it's up — a request and the response that confirms it

# what actually got called
grep '^{' /tmp/mvp-simulation.log \
  | jq -r 'select(.event=="request") | [.routeKey, .method, .path, .statusCode] | @tsv' \
  | sort | uniq -c

# stop
pkill -INT -f "simulation run .*mvp.sim.yaml"
```

<!-- @todo To intercept real hostnames instead of routing by routeKey, run with
     --proxy and a simulation.yaml (see `postman simulation run --help`). An
     intercepted HTTPS host is TLS-terminated with a CA minted for that run and
     deleted on exit, so record how to read its path, never the path itself:
     export NODE_EXTRA_CA_CERTS=$(grep -o '/[^ ]*/certs/ca\.pem' <log> | head -1) -->
<!-- @todo Add anything else needed to work here: how to authenticate and as
     whom, how to run the test suites, any setup they need. -->

## Assumptions

<!-- @todo Add every precondition you had to discover, the seeded test data
     worth reusing, and anything this simulation cannot reproduce — so nobody
     reads a green run as proof. Pair each claim with its consequence, like
     the generated ones below. -->

- **Requests with no matching mock are forwarded to the real host.**
  A passing run may have hit production. Check what got called for destinations
  you didn't expect and treat them as unmocked.

- **Mocks do not hot-reload.**
  Restart the simulation after editing a handler. Restarting the service is not enough.

- **Only HTTP dependencies are simulated.**
  Databases, caches and queues must run as real local instances.

- **Port 3000 must be free, and only one simulation runs at a time.**
  Startup fails, or the service reaches the wrong proxy.

## Observations

<!-- @todo After each run, replace the section below: which mocks got traffic,
     which got none, and anything surprising — unexpected statuses, unmocked
     destinations, behaviour the assumptions didn't predict. Last run only,
     summary not a request log. -->

<!-- begin:observations -->
_No runs yet._
<!-- end:observations -->
