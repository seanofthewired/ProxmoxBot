MAX_LENGTH = 2000

import logging
import re
from typing import List, Tuple

# logging.basicConfig(level=logging.INFO)

class DiscordMessageSplitter:
    def __init__(self):
        self.char_limit = 2000

    def split_message(self, message):
        if len(message) <= self.char_limit:
            return [message]

        chunks = []
        current_chunk = ""

        patterns = {
            'inline_code': r"`[^`]+`",
            'code_block': r"```[\s\S]*?```",
            'mention': r"<@\d+>",
            'url': r"https?://\S+"
        }
        combined_pattern = f"({patterns['inline_code']})|({patterns['code_block']})|({patterns['mention']})|({patterns['url']})"

        cursor = 0
        for match in re.finditer(combined_pattern, message):
            start, end = match.span()
            # Process text up to the structured content
            while cursor < start:
                slice_end = min(start, cursor + self.char_limit - len(current_chunk))
                current_chunk += message[cursor:slice_end]
                cursor = slice_end

            structured_content = message[start:end]
            if len(current_chunk) + len(structured_content) > self.char_limit:
                if current_chunk and current_chunk.strip():
                    chunks.append(current_chunk)
                    current_chunk = ""

                # Splitting logic for multi-line code blocks
                if structured_content.startswith('```') and len(structured_content) > self.char_limit:
                    # Find language specifier if present
                    lang_specifier_end = structured_content.find('\n') + 1
                    lang_specifier = structured_content[:lang_specifier_end]

                    # Split at last possible newline within limit
                    split_pos = structured_content.rfind('\n', 0, self.char_limit)
                    if split_pos != -1:
                        first_part = structured_content[:split_pos]
                        remaining_part = structured_content[split_pos:]

                        # Ensure first_part ends with closing backticks if it's the end of the block
                        if not first_part.endswith('```'):
                            first_part += '```'  # Add closing backticks to first part

                        # If remaining_part does not start with backticks, add them along with the language specifier
                        if not remaining_part.startswith('```'):
                            lang_specifier = ''
                            if '\n' in first_part:  # Check if there's a language specifier
                                first_newline_pos = first_part.find('\n')
                                lang_specifier = first_part[3:first_newline_pos]  # Extract language specifier
                            remaining_part = f'```{lang_specifier}{remaining_part}'

                        # Now, append first_part and prepare remaining_part for the next chunk
                        chunks.append(first_part)
                        current_chunk = remaining_part
                    else:
                        # If there's no good place to split, default to cutting at char limit
                        first_part = structured_content[:self.char_limit]
                        remaining_part = structured_content[self.char_limit:]
                        chunks.append(first_part)
                        current_chunk = remaining_part
                else:
                    current_chunk = structured_content
            else:
                current_chunk += structured_content
            cursor = end

        # Add the remaining part of the message
        while cursor < len(message):
            slice_end = min(len(message), cursor + self.char_limit - len(current_chunk))
            current_chunk += message[cursor:slice_end]
            cursor = slice_end
            if len(current_chunk) >= self.char_limit:
                chunks.append(current_chunk)
                current_chunk = ""

        if current_chunk:
            chunks.append(current_chunk)

        return chunks