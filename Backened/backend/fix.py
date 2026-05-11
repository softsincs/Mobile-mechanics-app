with open('test_apis_simple.py', 'r') as f:
    lines = f.readlines()

# Find and fix the problematic section around line 149
new_lines = []
i = 0
while i < len(lines):
    if i >= 145 and i <= 155 and 'print_response_data' in lines[i]:
        # Check if this is inside a requests.get call that needs fixing
        # Move print_response_data to after the closing parenthesis
        if i > 0 and 'headers=' in lines[i-1]:
            # Insert closing paren from previous line
            new_lines[-1] = lines[i-1].rstrip() + ')\n'
            new_lines.append(lines[i])  # This is print_response_data
            i += 1
            if i < len(lines) and lines[i].strip() == ')':
                i += 1  # Skip the extra closing paren
            continue
    new_lines.append(lines[i])
    i += 1

with open('test_apis_simple.py', 'w') as f:
    f.writelines(new_lines)

print("File fixed")
