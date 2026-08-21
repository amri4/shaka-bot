import importlib
import pkgutil


async def setup(bot):
    print("[Cases System] Starting loader...")

    package = importlib.import_module(__package__)

    print(f"[Cases System] Package: {package.__name__}")

    for module_info in pkgutil.walk_packages(
        package.__path__,
        prefix=f"{package.__name__}."
    ):
        module_name = module_info.name

        if module_name.endswith(".cog"):
            continue

        print(f"[Cases System] Found: {module_name}")

        try:
            module = importlib.import_module(module_name)

            setup_func = getattr(module, "setup", None)

            if setup_func is None:
                print(f"[Cases System] Skipped: {module_name}")
                continue

            print(f"[Cases System] Loading: {module_name}")

            await setup_func(bot)

            print(f"[Cases System] Loaded: {module_name}")

        except Exception as e:
            print(f"[Cases System] FAILED: {module_name}")
            print(f"[Cases System] {type(e).__name__}: {e}")

    print("[Cases System] Finished loading.")
