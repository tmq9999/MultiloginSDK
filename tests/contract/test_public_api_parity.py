import inspect

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient


def test_public_api_parity():
    sync = MultiloginClient("T")
    async_ = AsyncMultiloginClient("T")
    for name in ["auth", "workspaces", "folders", "profiles", "launcher", "proxies"]:
        a = getattr(sync, name)
        b = getattr(async_, name)
        public = {m for m in dir(a) if not m.startswith("_")}
        assert public == {m for m in dir(b) if not m.startswith("_")}
        for method in public:
            p = list(inspect.signature(getattr(a, method)).parameters.values())
            q = list(inspect.signature(getattr(b, method)).parameters.values())
            assert [(x.name, x.kind, x.default) for x in p] == [
                (x.name, x.kind, x.default) for x in q
            ]
    sync.close()
