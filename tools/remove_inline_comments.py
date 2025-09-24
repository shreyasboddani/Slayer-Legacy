import sys, re

if len(sys.argv) < 3:
    print('Usage: remove_inline_comments.py input.html output.html')
    sys.exit(2)

inp = sys.argv[1]
out = sys.argv[2]

with open(inp, 'r', encoding='utf-8') as f:
    data = f.read()

lines = data.splitlines(True)

def find_comment_index(line):
    in_s = in_d = in_b = False
    i = 0
    while i < len(line) - 1:
        c = line[i]
        # handle escapes
        prev = line[i-1] if i>0 else ''
        if c == "'" and not in_d and not in_b and prev != '\\':
            in_s = not in_s
        elif c == '"' and not in_s and not in_b and prev != '\\':
            in_d = not in_d
        elif c == '`' and not in_s and not in_d and prev != '\\':
            in_b = not in_b
        elif c == '/' and line[i+1] == '/' and not in_s and not in_d and not in_b:
            return i
        i += 1
    return -1

out_lines = []
section_divider_re = re.compile(r'^\s*//\s*[-#]')

for line in lines:
    idx = find_comment_index(line)
    if idx == -1:
        out_lines.append(line)
        continue
    # If the comment begins the line (ignoring leading whitespace), check if it's a section divider
    if re.match(r'^\s*//', line):
        if section_divider_re.search(line):
            out_lines.append(line)
            continue
        else:
            # whole-line comment to remove -> replace with empty line to preserve line numbers
            # but keep the newline
            if line.endswith('\r\n'):
                out_lines.append('\r\n')
            elif line.endswith('\n'):
                out_lines.append('\n')
            else:
                out_lines.append('\n')
            continue
    # Otherwise, it's an inline/trailing comment; remove from that index onward
    before = line[:idx].rstrip()
    # preserve original line ending
    ending = '\n'
    if line.endswith('\r\n'):
        ending = '\r\n'
    elif line.endswith('\n'):
        ending = '\n'
    else:
        ending = ''
    if before.strip() == '':
        # nothing before comment and not a divider -> keep blank line
        out_lines.append(ending)
    else:
        out_lines.append(before + ending)

with open(out, 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print('Wrote cleaned file to', out)
