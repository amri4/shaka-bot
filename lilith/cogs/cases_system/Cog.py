import importlib
import pkgutil


async def setup(bot):
    package = importlib.import_module(__package__)

    for module_info in pkgutil.walk_packages(
        package.__path__,
        prefix=f"{package.__name__}."
    ):
        module_name = module_info.name

        # Don't try to load this loader again.
        if module_name.endswith(".cog"):
            continue

        module = importlib.import_module(module_name)

        setup_func = getattr(module, "setup", None)

        if setup_func is not None:
            await setup_func(bot)
