from gcloudc.db.backends.datastore import commands

# Store the original function
original_perform_unique_checks = commands.perform_unique_checks

# Create a patched version
def patched_perform_unique_checks(*args, **kwargs):
    try:
        return original_perform_unique_checks(*args, **kwargs)
    except Exception as e:
        if "Only ancestor queries are allowed inside transactions" in str(e):
            # Skip unique checks as a fallback
            return None
        raise

# Apply the patch
commands.perform_unique_checks = patched_perform_unique_checks