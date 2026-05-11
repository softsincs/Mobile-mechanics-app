import os

files_to_fix = [
    'users/tests/test_auth_password_reset.py',
    'users/tests/test_auth_tokens.py',
    'users/tests/test_auth_security.py',
    'users/tests/test_auth_integration.py',
    'users/tests/test_auth_concurrency.py',
    'users/tests/test_auth_unit.py',
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Fix line 1 - handle the escaped triple quotes
        if lines and lines[0].startswith('"""'):
            # Find where the docstring actually ends
            for i in range(1, min(10, len(lines))):
                if '"""' in lines[i] or i == 1:  # Check first few lines
                    # Reconstruct proper docstring
                    if i < 5:
                        # Multi-line docstring, need to fix it
                        # Extract all content until we find proper closing quotes
                        docstring_content = []
                        for j in range(i, len(lines)):
                            if '"""' in lines[j] and not lines[j].strip().startswith('"'):
                                # Found the end
                                remaining = lines[j].split('"""')[1]
                                lines[j] = remaining
                                break
                            docstring_content.append(lines[j])
                        
                        # Rebuild the first lines
                        first_line_content = lines[0][3:].strip()  # Get content after initial """
                        lines[0] = '"""\n'
                        if first_line_content:
                            lines.insert(1, first_line_content + '\n')
                        break
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f'Processed: {filepath}')

print('Done!')
