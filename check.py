# Debug script to check available tools in crewai_tools
import crewai_tools
import pkgutil

print("=== CrewAI Tools Debug Information ===\n")

# Check the version
try:
    print(f"crewai_tools version: {crewai_tools.__version__}")
except AttributeError:
    print("Version information not available")

print(f"crewai_tools location: {crewai_tools.__file__}")

# Check what's available in the module
print("\n=== Available attributes in crewai_tools ===")
available_items = dir(crewai_tools)
for item in sorted(available_items):
    if not item.startswith('_'):
        print(f"  {item}")

# Check for Serper-related tools specifically
print("\n=== Searching for Serper-related tools ===")
serper_tools = [item for item in available_items if 'serper' in item.lower()]
if serper_tools:
    for tool in serper_tools:
        print(f"  Found: {tool}")
else:
    print("  No Serper-related tools found in main module")

# Check submodules
print("\n=== Available submodules ===")
try:
    for importer, modname, ispkg in pkgutil.iter_modules(crewai_tools.__path__):
        print(f"  {modname} (package: {ispkg})")
        
        # Try to import each submodule and check for SerperDevTool
        try:
            submodule = importer.find_spec(modname).loader.load_module(modname)
            if hasattr(submodule, 'SerperDevTool'):
                print(f"    → SerperDevTool found in {modname}!")
        except Exception as e:
            print(f"    → Could not check {modname}: {e}")
            
except Exception as e:
    print(f"Could not iterate submodules: {e}")

# Try alternative import patterns
print("\n=== Trying alternative imports ===")

alternatives = [
    "from crewai_tools.tools.serper_dev_tool import SerperDevTool",
    "from crewai_tools.tools import SerperDevTool",
    "from crewai_tools import SerperTool",
    "from crewai_tools.serper_dev_tool import SerperDevTool",
]

for alt in alternatives:
    try:
        exec(alt)
        print(f"  ✓ SUCCESS: {alt}")
        break
    except ImportError as e:
        print(f"  ✗ FAILED: {alt} - {e}")
    except Exception as e:
        print(f"  ✗ ERROR: {alt} - {e}")

print("\n=== Recommendations ===")
print("1. Try updating: pip install --upgrade crewai-tools")
print("2. Check if you need: pip install 'crewai-tools[serper]'")
print("3. Verify your API key is set up for Serper")
