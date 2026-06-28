import re

with open(r'C:\Users\sksra\.gemini\antigravity\brain\80cb68bc-e1f1-4e03-919c-4fcd718aad35\.system_generated\steps\599\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Find any color tokens
colors = re.findall(r'--token-[a-zA-Z0-9\-]+:\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))', text)
print("Color tokens found:")
for color in set(colors):
    print(color)

# Find some text snippets to understand the layout
print("\nText snippets:")
lines = text.split('\n')
for line in lines:
    if any(kw in line.lower() for kw in ['agent', 'automation', 'workflow', 'pricing', 'features', 'cosmoq']):
        if len(line.strip()) > 30 and len(line.strip()) < 500 and not '<style' in line and not '<script' in line:
            print(line.strip()[:100])
