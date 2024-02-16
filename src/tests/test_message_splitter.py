import logging
import unittest
from bot.message_splitter import DiscordMessageSplitter
import re

class TestDiscordMessageSplitter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.splitter = DiscordMessageSplitter()
        cls.MAX_LENGTH = 2000

    def _limit(self, text: str, limit: int = 2000) -> str:
        return "a" * (limit - len(text))

    def _char(self, count: int = 20) -> str:
        return "b" * count

    def scenario(self, contains: str, expected_chunk: int, limit: int = 2000, expected_chunks=2, buffer: str = None):
        if buffer is None:
            buffer = self._limit(contains, limit)
        
        eob = self._char()
        msg = f"{buffer}{contains}{eob}"
        chunks = self.splitter.split_message(msg)

        chunk_len = 0
        for i, chunk in enumerate(chunks):
            logging.info(f"Chunk #{i} length: {len(chunk)}")
            logging.info(chunk)
            self.assertLessEqual(len(chunk), self.MAX_LENGTH, f"Chunk #{i} exceeds the maximum length")
            chunk_len += len(chunk)
            
        self.assertEqual(len(chunks), expected_chunks, "Number of chunks does not match expected")
        
        reconstructed_message = "".join(chunks)
        reconstructed_message = re.sub(r"```(?:\w+\n)?", "", reconstructed_message)
        contains_clean = re.sub(r"```(?:\w+\n)?", "", contains)
        contains_clean = contains_clean.replace("\n", "")
        reconstructed_message = reconstructed_message.replace("\n", "")
        self.assertIn(contains_clean, reconstructed_message, "Expected content not found in the reconstructed message")

    # Specific test cases for different scenarios
    def test_code_block_split(self):
        fn = """
```
def example_function():
    print("Hello, world!")
```"""
        self.scenario(fn, 0)
        self.scenario(fn, 1, 2001)
    
    def test_mention_split(self):
        mention = "<@123456789012345678>"
        self.scenario(mention, 0)
        self.scenario(mention, 1, 2001)

    def test_url_split(self):
        url = "https://example.com/ "
        self.scenario(url, 0)
        self.scenario(url, 1, 2002)
    
    def test_multiple_small_code_blocks(self):
        multiple_small_code_blocks = "\n```python\nprint('Hello')\n```\n" * 4
        self.scenario(multiple_small_code_blocks, 0, 2000, expected_chunks=2)
    
    def test_large_code_block(self):
        large_code_block = "\n```python\n" + "print('Line ' + str(i))\n" * 100 + "```"
        self.scenario(large_code_block, 1, 2000, expected_chunks=2)
        
    def test_chunk_reaches_char_limit(self):
        # Test to trigger if len(current_chunk) >= self.char_limit
        long_text = self._char(self.MAX_LENGTH) + " Some additional text"
        chunks = self.splitter.split_message(long_text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), self.MAX_LENGTH)
        self.assertTrue(chunks[1].startswith(" Some additional text"))
        
    def test_no_good_place_to_split_code_block(self):
        long_code_block_without_newlines = "```" + self._char(self.MAX_LENGTH) + "```"
        self.scenario(long_code_block_without_newlines, 0, 2000, expected_chunks=2)
