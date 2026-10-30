import os
import re

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src"))
issues = []

for root, _, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith(".tsx"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8") as fl:
                content = fl.read()
                # Find className="..."
                matches = re.finditer(r'className=["\']([^"\']+)["\']', content)
                for m in matches:
                    cls_str = m.group(1)
                    parts = cls_str.split()
                    has_dark_bg = any("dark:bg" in p for p in parts)
                    has_dark_text = any("dark:text" in p for p in parts)
                    has_dark_border = any("dark:border" in p for p in parts)

                    for part in parts:
                        if (part == "bg-white" or part.lower() == "bg-[#ffffff]") and not has_dark_bg:
                            issues.append((f, "bg-white missing dark:bg", cls_str))
                            break
                        if (part == "bg-gray-50" or part == "bg-gray-100") and not has_dark_bg:
                            issues.append((f, f"{part} missing dark:bg", cls_str))
                            break
                        if (part in ["text-gray-900", "text-gray-800", "text-gray-700", "text-black"]) and not has_dark_text:
                            issues.append((f, f"{part} missing dark:text", cls_str))
                            break

print(f"Total theme issues found: {len(issues)}")
by_file = {}
for fname, issue_type, snippet in issues:
    by_file[fname] = by_file.get(fname, 0) + 1

for fn, count in sorted(by_file.items(), key=lambda x: -x[1]):
    print(f"  {fn}: {count} issues")

