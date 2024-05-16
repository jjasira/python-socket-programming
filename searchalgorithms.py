"""Standard library imports."""
import random
import string
import time
from tabulate import tabulate

"""External imports."""
import matplotlib.pyplot as plt


# Naive search algorithm
def naive_search(text: str, pattern: str) -> int:
    n: int = len(text)
    m: int = len(pattern)
    """Doing a linear search, comparing every character of the 
        pattern to be searched with a pattern of the same length
        in the text.
    """
    for i in range(n - m + 1):
        if text[i:i + m] == pattern:
            return i
    return -1

# Knuth-Morris-Pratt (KMP) search algorithm
def kmp_search(text: str, pattern: str) -> int:
    """This algorithm improves the efficiency of string matching by 
        preprocessing the pattern to create a partial match table (prefix table) 
        that allows the search to skip characters in the text.
    """
    def compute_lps(pattern: str) -> list:
        """We create alist of 0's the whose length is equal to the patterns length."""
        lps: list = [0] * len(pattern)
        length: int = 0
        i: int = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    n: int = len(text)
    m: int = len(pattern)
    lps: list = compute_lps(pattern)
    i: int = 0
    j: int = 0
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == m:
            return i - j
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1

# Boyer-Moore search algorithm
def boyer_moore_search(text: str, pattern: str) -> int:
    """This algorithm preprocesses the pattern to create two tables 
       (bad character and good suffix) that guide the search, allowing 
        it to skip sections of the text, making it efficient for longer patterns.
    """
    def bad_char_table(pattern: str) -> list:
        bad_char:list = [-1] * 256
        for i in range(len(pattern)):
            bad_char[ord(pattern[i])] = i
        return bad_char

    def good_suffix_table(pattern: str) -> list:
        m: int = len(pattern)
        good_suffix: list = [m] * m
        last_prefix: int = m
        for i in range(m - 1, -1, -1):
            if is_prefix(pattern, i + 1):
                last_prefix: int = i + 1
            good_suffix[m - 1 - i] = last_prefix - i + m - 1
        for i in range(m - 1):
            suffix_len: int = suffix_length(pattern, i)
            good_suffix[suffix_len] = m - 1 - i + suffix_len
        return good_suffix

    def is_prefix(pattern: str, p: int) -> bool:
        m: int = len(pattern)
        for i in range(p, m):
            if pattern[i] != pattern[i - p]:
                return False
        return True

    def suffix_length(pattern: str, p: int) -> int:
        m: int = len(pattern)
        length: int = 0
        i: int = p
        j: int = m - 1
        while i >= 0 and pattern[i] == pattern[j]:
            length += 1
            i -= 1
            j -= 1
        return length

    n: int = len(text)
    m: int = len(pattern)
    bad_char: list = bad_char_table(pattern)
    good_suffix: list = good_suffix_table(pattern)

    s: int = 0
    while s <= n - m:
        j: int = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            return s
        else:
            s += max(good_suffix[j], j - bad_char[ord(text[s + j])])
    return -1

# Rabin-Karp search algorithm
def rabin_karp_search(text: str, pattern: str) -> int:
    """This algorithm uses hashing to find a substring within a 
       string. It calculates the hash of the pattern and compares 
       it with the hash of substring in the text.
    """
    d: int = 256
    q: int = 101
    m: int = len(pattern)
    n: int = len(text)
    h: int = 1
    p: int = 0
    t: int = 0
    for i in range(m - 1):
        h = (h * d) % q
    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q
    for i in range(n - m + 1):
        if p == t:
            if text[i:i + m] == pattern:
                return i
        if i < n - m:
            t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
            if t < 0:
                t += q
    return -1

# Aho-Corasick search algorithm
class AhoCorasick:
    """This algorithm builds a finite state machine from a set of patterns 
       and uses it to search for all occurrences of the pattern simultaneously
       in a text.
    """
    def __init__(self):
        self.goto: dict[int, dict]  = {0: {}}
        self.out: dict = {}
        self.fail: dict = {}

    def add_pattern(self, pattern: str):
        current_state = 0
        for char in pattern:
            if char not in self.goto[current_state]:
                self.goto[current_state][char] = len(self.goto)
                self.goto[len(self.goto)] = {}
            current_state = self.goto[current_state][char]
        self.out.setdefault(current_state, []).append(pattern)

    def build(self):
        queue: list = []
        for char in self.goto[0]:
            state = self.goto[0][char]
            self.fail[state] = 0
            queue.append(state)

        while queue:
            r = queue.pop(0)
            for char, s in self.goto[r].items():
                queue.append(s)
                state = self.fail[r]
                while state and char not in self.goto[state]:
                    state = self.fail[state]
                self.fail[s] = self.goto[state].get(char, 0) if state else 0
                self.out.setdefault(s, []).extend(self.out.get(self.fail[s], []))

    def search(self, text: str) -> list:
        state: int = 0
        results: list = []
        for i, char in enumerate(text):
            while state and char not in self.goto[state]:
                state = self.fail[state]
            state = self.goto[state].get(char, 0)
            for pattern in self.out.get(state, []):
                results.append((i - len(pattern) + 1, pattern))
        return results

# Function to generate random text
def generate_text(size: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + ' ', k=size))

# Function to measure execution time of a search function
def measure_time(search_function, text: str, pattern: str = None) -> float:
    start: float = time.time()
    if pattern is not None:
        search_function(text, pattern)
    else:
        search_function(text)
    end: float = time.time()
    return end - start

if __name__ == '__main__':
    
    # Define file sizes and pattern
    file_sizes: list = [10000, 50000, 100000, 500000, 1000000]
    pattern: str = "searchpattern"
    times_naive: list[float] = []
    times_kmp: list[float] = []
    times_boyer_moore: list[float] = []
    times_rabin_karp: list[float] = []
    times_aho_corasick: list[float] = []

    # Create Aho-Corasick object and add pattern
    ac: AhoCorasick = AhoCorasick()
    ac.add_pattern(pattern)
    ac.build()

    # Measure execution times
    for size in file_sizes:
        text: str = generate_text(size)
        times_naive.append(measure_time(naive_search, text, pattern))
        times_kmp.append(measure_time(kmp_search, text, pattern))
        times_boyer_moore.append(measure_time(boyer_moore_search, text, pattern))
        times_rabin_karp.append(measure_time(rabin_karp_search, text, pattern))
        times_aho_corasick.append(measure_time(ac.search, text))

    # Prepare data for table
    table_data = [
        ["File Size (characters)", "Naive Search", "KMP Search", "Boyer-Moore Search", "Rabin-Karp Search", "Aho-Corasick Search"]
    ]
    """The code above will populate the table headers as stipulated
       the one below will populate the table body with the search times
       for the search-algorithms against the file sizes.
    """

    for i in range(len(file_sizes)):
        table_data.append([
            file_sizes[i],
            times_naive[i],
            times_kmp[i],
            times_boyer_moore[i],
            times_rabin_karp[i],
            times_aho_corasick[i]
        ])

    # Print table
    """The table is printed using the tabulate module"""
    print(tabulate(table_data, headers="firstrow", tablefmt="grid"))

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(file_sizes, times_naive, label='Naive Search')
    plt.plot(file_sizes, times_kmp, label='KMP Search')
    plt.plot(file_sizes, times_boyer_moore, label='Boyer-Moore Search')
    plt.plot(file_sizes, times_rabin_karp, label='Rabin-Karp Search')
    plt.plot(file_sizes, times_aho_corasick, label='Aho-Corasick Search')
    plt.xlabel('File Size (characters)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time of Search Algorithms')
    plt.legend()
    plt.grid(True)
    plt.show()


