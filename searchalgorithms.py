import time
import random
import string
import matplotlib.pyplot as plt

# Naive search algorithm
def naive_search(text, pattern):
    n = len(text)
    m = len(pattern)
    for i in range(n - m + 1):
        if text[i:i + m] == pattern:
            return i
    return -1

# Knuth-Morris-Pratt (KMP) search algorithm
def kmp_search(text, pattern):
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
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

    n = len(text)
    m = len(pattern)
    lps = compute_lps(pattern)
    i = 0
    j = 0
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
def boyer_moore_search(text, pattern):
    def bad_char_table(pattern):
        bad_char = [-1] * 256
        for i in range(len(pattern)):
            bad_char[ord(pattern[i])] = i
        return bad_char

    def good_suffix_table(pattern):
        m = len(pattern)
        good_suffix = [m] * m
        last_prefix = m
        for i in range(m - 1, -1, -1):
            if is_prefix(pattern, i + 1):
                last_prefix = i + 1
            good_suffix[m - 1 - i] = last_prefix - i + m - 1
        for i in range(m - 1):
            suffix_len = suffix_length(pattern, i)
            good_suffix[suffix_len] = m - 1 - i + suffix_len
        return good_suffix

    def is_prefix(pattern, p):
        m = len(pattern)
        for i in range(p, m):
            if pattern[i] != pattern[i - p]:
                return False
        return True

    def suffix_length(pattern, p):
        m = len(pattern)
        length = 0
        i = p
        j = m - 1
        while i >= 0 and pattern[i] == pattern[j]:
            length += 1
            i -= 1
            j -= 1
        return length

    n = len(text)
    m = len(pattern)
    bad_char = bad_char_table(pattern)
    good_suffix = good_suffix_table(pattern)

    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            return s
        else:
            s += max(good_suffix[j], j - bad_char[ord(text[s + j])])
    return -1

# Rabin-Karp search algorithm
def rabin_karp_search(text, pattern):
    d = 256
    q = 101
    m = len(pattern)
    n = len(text)
    h = 1
    p = 0
    t = 0
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
    def __init__(self):
        self.goto = {0: {}}
        self.out = {}
        self.fail = {}

    def add_pattern(self, pattern):
        current_state = 0
        for char in pattern:
            if char not in self.goto[current_state]:
                self.goto[current_state][char] = len(self.goto)
                self.goto[len(self.goto)] = {}
            current_state = self.goto[current_state][char]
        self.out.setdefault(current_state, []).append(pattern)

    def build(self):
        queue = []
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

    def search(self, text):
        state = 0
        results = []
        for i, char in enumerate(text):
            while state and char not in self.goto[state]:
                state = self.fail[state]
            state = self.goto[state].get(char, 0)
            for pattern in self.out.get(state, []):
                results.append((i - len(pattern) + 1, pattern))
        return results

# Function to generate random text
def generate_text(size):
    return ''.join(random.choices(string.ascii_lowercase + ' ', k=size))

# Function to measure execution time of a search function
def measure_time(search_function, text, pattern=None):
    start = time.time()
    if pattern is not None:
        search_function(text, pattern)
    else:
        search_function(text)
    end = time.time()
    return end - start

# Define file sizes and pattern
file_sizes = [10000, 50000, 100000, 500000, 1000000]
pattern = "searchpattern"
times_naive = []
times_kmp = []
times_boyer_moore = []
times_rabin_karp = []
times_aho_corasick = []

# Create Aho-Corasick object and add pattern
ac = AhoCorasick()
ac.add_pattern(pattern)
ac.build()

# Measure execution times
for size in file_sizes:
    text = generate_text(size)
    times_naive.append(measure_time(naive_search, text, pattern))
    times_kmp.append(measure_time(kmp_search, text, pattern))
    times_boyer_moore.append(measure_time(boyer_moore_search, text, pattern))
    times_rabin_karp.append(measure_time(rabin_karp_search, text, pattern))
    times_aho_corasick.append(measure_time(ac.search, text))

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
