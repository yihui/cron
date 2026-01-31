from fontTools.ttLib import TTFont

def generate_fallback_list(font_path, input_file, output_file):
    # 1. Load the font and get the Character Map (cmap)
    font = TTFont(font_path)
    cmap = font.getBestCmap() # Dictionary of {codepoint: name}

    # 2. Read input file and strip CRLF/newlines
    with open(input_file, 'r', encoding='utf-8') as f:
        # Read everything and remove carriage returns and line feeds
        content = f.read().replace('\r', '').replace('\n', '')
    
    # Use a set for "absolute precision" so we don't check the same char twice
    unique_chars = sorted(list(set(content)))

    missing = []

    # 3. Compare against font cmap
    for char in unique_chars:
        if ord(char) not in cmap:
            missing.append(char)

    # 4. Write missing characters to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(missing))

    print(f" Missing:    {missing}")

generate_fallback_list('gkai00mp.ttf', 'fonts/chars.txt', 'big5.txt')
